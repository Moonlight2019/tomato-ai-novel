# llm_adapters.py
# -*- coding: utf-8 -*-
import logging
from typing import Optional
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from google import genai
from google.genai import types
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
from openai import OpenAI
import requests

def check_base_url(url: str) -> str:
    """
    处理base_url的规则：
    1. 如果url以#结尾，则移除#并直接使用用户提供的url
    2. 否则检查是否需要添加/v1后缀
    """
    import re
    url = url.strip()
    if not url:
        return url

    if url.endswith('#'):
        return url.rstrip('#')

    if not re.search(r'/v\d+$', url):
        if '/v1' not in url:
            url = url.rstrip('/') + '/v1'
    return url


def _extract_openai_content(response) -> str:
    """
    从 openai SDK 的 chat.completions 响应中，稳健提取正文文本。

    兼容五种情况：
    1. content 为普通字符串（标准 OpenAI 格式）
    2. content 为字符串列表（推理流/多段 content）
    3. 无 content 但有 reasoning_content（推理模型先思考后回复）
    4. content 为空/None
    5. 响应不是 OpenAI 对象（如 base_url 配错导致 API 返回 404 文本 "Not Found"）

    返回拼接后的文本；失败时记录日志并返回 ""，绝不抛异常打断上层重试。
    """
    try:
        # 情况5：响应根本不是 OpenAI 对象（base_url 配错 / 网关返回纯文本 404 等）。
        # 这时 choices 属性不存在，且 response 可能是 str —— 单独提示，避免误判为"空回复"。
        if not isinstance(response, (str, bytes)):
            if not getattr(response, "choices", None):
                logging.warning("No choices in chat completion response.")
                return ""
        else:
            logging.warning(
                "Chat completion 返回了非 JSON 文本（base_url 或接口可能配置错误）：%r",
                response[:200] if isinstance(response, str) else response,
            )
            return ""

        msg = response.choices[0].message
        if msg is None:
            return ""

        content = getattr(msg, "content", None)

        # 情况1/2：content 可能是 str 或 list[part]
        if content:
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, str):
                        parts.append(item)
                    elif isinstance(item, dict):
                        t = item.get("text") or item.get("content")
                        if isinstance(t, str):
                            parts.append(t)
                text = "".join(parts)
            else:
                # 意外类型（如 pydantic message），兜底转字符串
                text = str(content)
            text = text.strip()
            if text:
                return text

        # 情况3：content 为空时退回 reasoning_content
        reasoning = getattr(msg, "reasoning_content", None)
        if reasoning:
            if isinstance(reasoning, str):
                text = reasoning.strip()
                if text:
                    return text
            elif isinstance(reasoning, list):
                parts = [str(x.get("text") or x.get("content") or "") if isinstance(x, dict) else str(x)
                         for x in reasoning]
                text = "".join(parts).strip()
                if text:
                    return text

        logging.warning("Chat completion returned empty content.")
        return ""
    except Exception as e:
        logging.error(f"提取 chat completion 内容失败: {e}")
        return ""

class BaseLLMAdapter:
    """
    统一的 LLM 接口基类，为不同后端（OpenAI、Ollama、ML Studio、Gemini等）提供一致的方法签名。
    """
    def invoke(self, prompt: str) -> str:
        raise NotImplementedError("Subclasses must implement .invoke(prompt) method.")

class DeepSeekAdapter(BaseLLMAdapter):
    """
    适配官方/OpenAI兼容接口。

    用原生 openai SDK（而非 langchain.ChatOpenAI），避免 chat.completions 返回
    推理流（content 为数组 / 含 reasoning_content）时 langchain 的 pydantic 绑定
    抛 "str object has no attribute model_dump"。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return _extract_openai_content(response)
        except Exception as e:
            logging.error(f"DeepSeek API 调用失败: {e}")
            return ""

class OpenAIAdapter(BaseLLMAdapter):
    """
    适配官方/OpenAI兼容接口（用原生 openai SDK，解析见 _extract_openai_content）。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=timeout,
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return _extract_openai_content(response)
        except Exception as e:
            logging.error(f"OpenAI API 调用失败: {e}")
            return ""

class GeminiAdapter(BaseLLMAdapter):
    """
    适配 Google Gemini (Google Generative AI) 接口
    """

    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        # 使用最新的 google-genai 客户端
        self._client = genai.Client(api_key=self.api_key)

    def invoke(self, prompt: str) -> str:
        # 使用当前 google-genai SDK 构造生成参数，API 调用异常保留给上层重试逻辑处理。
        config = types.GenerateContentConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )

        try:
            text = response.text
        except (ValueError, AttributeError):
            logging.warning("Gemini response blocked or empty (safety filter).")
            return ""

        if text:
            return text
        else:
            logging.warning("No text response from Gemini API.")
            return ""

class AzureOpenAIAdapter(BaseLLMAdapter):
    """
    适配 Azure OpenAI 接口（使用 langchain.ChatOpenAI）
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        import re
        match = re.match(r'https://(.+?)/openai/deployments/(.+?)/chat/completions\?api-version=(.+)', base_url)
        if match:
            self.azure_endpoint = f"https://{match.group(1)}"
            self.azure_deployment = match.group(2)
            self.api_version = match.group(3)
        else:
            raise ValueError("Invalid Azure OpenAI base_url format")
        
        self.api_key = api_key
        self.model_name = self.azure_deployment
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            azure_deployment=self.azure_deployment,
            api_version=self.api_version,
            api_key=self.api_key,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from AzureOpenAIAdapter.")
            return ""
        return response.content

class OllamaAdapter(BaseLLMAdapter):
    """
    Ollama 同样有一个 OpenAI-like /v1/chat 接口，可直接使用 ChatOpenAI。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        if self.api_key == '':
            self.api_key= 'ollama'

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        response = self._client.invoke(prompt)
        if not response:
            logging.warning("No response from OllamaAdapter.")
            return ""
        return response.content

class MLStudioAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatOpenAI(
            model=self.model_name,
            api_key=self.api_key,
            base_url=self.base_url,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.invoke(prompt)
            if not response:
                logging.warning("No response from MLStudioAdapter.")
                return ""
            return response.content
        except Exception as e:
            logging.error(f"ML Studio API 调用超时或失败: {e}")
            return ""

class AzureAIAdapter(BaseLLMAdapter):
    """
    适配 Azure AI Inference 接口，用于访问Azure AI服务部署的模型
    使用 azure-ai-inference 库进行API调用
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        import re
        # 匹配形如 https://xxx.services.ai.azure.com/models/chat/completions?api-version=xxx 的URL
        match = re.match(r'https://(.+?)\.services\.ai\.azure\.com(?:/models)?(?:/chat/completions)?(?:\?api-version=(.+))?', base_url)
        if match:
            # endpoint需要是形如 https://xxx.services.ai.azure.com/models 的格式
            self.endpoint = f"https://{match.group(1)}.services.ai.azure.com/models"
            # 如果URL中包含api-version参数，使用它；否则使用默认值
            self.api_version = match.group(2) if match.group(2) else "2024-05-01-preview"
        else:
            raise ValueError("Invalid Azure AI base_url format. Expected format: https://<endpoint>.services.ai.azure.com/models/chat/completions?api-version=xxx")
        
        self.base_url = self.endpoint  # 存储处理后的endpoint URL
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.complete(
                messages=[
                    SystemMessage("You are a helpful assistant."),
                    UserMessage(prompt)
                ]
            )
            if response and response.choices:
                return response.choices[0].message.content
            else:
                logging.warning("No response from AzureAIAdapter.")
                return ""
        except Exception as e:
            logging.error(f"Azure AI Inference API 调用失败: {e}")
            return ""

# 火山引擎实现
class VolcanoEngineAIAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=api_key,
            timeout=timeout  # 添加超时配置
        )
    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            if not response:
                logging.warning("No response from VolcanoEngineAdapter.")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"火山引擎API调用超时或失败: {e}")
            return ""

class SiliconFlowAdapter(BaseLLMAdapter):
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=api_key,
            timeout=timeout  # 添加超时配置
        )
    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            if not response:
                logging.warning("No response from SiliconFlowAdapter.")
                return ""
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"硅基流动API调用超时或失败: {e}")
            return ""

# Grok 实现
class GrokAdapter(BaseLLMAdapter):
    """
    适配 xAI Grok API
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        self.base_url = check_base_url(base_url)
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are Grok, created by xAI."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=self.timeout
            )
            if response and response.choices:
                return response.choices[0].message.content
            else:
                logging.warning("No response from GrokAdapter.")
                return ""
        except Exception as e:
            logging.error(f"Grok API 调用失败: {e}")
            return ""

class MimoAdapter(BaseLLMAdapter):
    """
    适配 mimo (Anthropic 兼容) 接口
    使用 anthropic Python SDK，通过 Anthropic 格式调用 mimo-v2.5 系列模型。
    """
    def __init__(self, api_key: str, base_url: str, model_name: str, max_tokens: int, temperature: float = 0.7, timeout: Optional[int] = 600):
        import anthropic
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

        self._client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def invoke(self, prompt: str) -> str:
        try:
            response = self._client.messages.create(
                model=self.model_name,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            if response and response.content:
                # mimo 可能返回 ThinkingBlock + TextBlock，取 TextBlock
                for block in response.content:
                    if block.type == "text":
                        return block.text
                # fallback: 没有 text block，用字符串拼接
                return ""
            else:
                logging.warning("No response from MimoAdapter.")
                return ""
        except Exception as e:
            msg = str(e)
            if "429" in msg or "quota" in msg.lower() or "rate limit" in msg.lower():
                logging.error(
                    "Mimo API 限流/配额不足（429）：可能触发账户限流或 token 额度已用尽。"
                    "请稍后重试、降低并发，或前往控制台查询配额。原始错误：%s", msg
                )
            else:
                logging.error(f"Mimo API 调用失败: {e}")
            return ""


def create_llm_adapter(
    interface_format: str,
    base_url: str,
    model_name: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> BaseLLMAdapter:
    """
    工厂函数：根据 interface_format 返回不同的适配器实例。
    """
    fmt = interface_format.strip().lower()
    if fmt == "deepseek":
        return DeepSeekAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "openai":
        return OpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "azure openai":
        return AzureOpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "azure ai":
        return AzureAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "ollama":
        return OllamaAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "ml studio":
        return MLStudioAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "gemini":
        return GeminiAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "阿里云百炼":
        return OpenAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "火山引擎":
        return VolcanoEngineAIAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "硅基流动":
        return SiliconFlowAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "grok":
        return GrokAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    elif fmt == "mimo" or fmt == "anthropic":
        return MimoAdapter(api_key, base_url, model_name, max_tokens, temperature, timeout)
    else:
        raise ValueError(f"Unknown interface_format: {interface_format}")


# 已知需要特殊 base_url 的供应商提示（用于给无效地址提供可操作诊断）
_SPECIAL_BASE_URL_HINTS = {
    "opencode": "OpenCode Go 的正确地址是 https://opencode.ai/zen/go/v1（不是 api.opencode.ai）",
    "mimo": "请确认为官方 OpenCode/提供商给出的 anthropic 接口地址",
}


def diagnose_llm_config(
    interface_format: str,
    base_url: str,
    model_name: str,
    api_key: str,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    timeout: int = 30,
) -> tuple:
    """
    预检一个 LLM 配置是否可用，返回 (ok: bool, message: str)。

    用于在切换模型 / 开始长任务前做轻量连通性自检，避免用坏配置跑长篇到一半才报错。
    诊断优先级：缺 key / 缺地址 / 地址或接口错误(404等) / key 无效(401) / 返回空 / 成功。

    此函数只做诊断，不抛出异常；message 是同 g 可读的中文提示。
    """
    interface_format = (interface_format or "").strip().lower()

    # 1) 缺 key：很多适配器缺 key 时也能构造，必须显式拦截
    if not api_key:
        return False, "未填写 API Key，请先在「设置-模型配置」里填入"

    # 2) 缺 base_url
    if not (base_url or "").strip():
        return False, "未填写接口地址(base_url)，请检查模型配置"

    # 3) 已知特殊地址的提示：base_url 明显不是该供应商时给操作建议
    for token, hint in _SPECIAL_BASE_URL_HINTS.items():
        if token in interface_format or token in (base_url or "").lower():
            if token == "opencode" and "zen/go/v1" not in base_url:
                return False, f"OpenCode 接口地址可能不对：{hint}"

    try:
        adapter = create_llm_adapter(
            interface_format=interface_format,
            base_url=base_url,
            model_name=model_name or "",
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        response = adapter.invoke("请只回复两个字的词：测试")
    except Exception as e:
        msg = str(e)
        # 401 = key 无效；404 = 地址/接口错
        if "401" in msg or "unauthorized" in msg.lower() or "invalid api" in msg.lower():
            return False, f"API Key 无效或未授权(401)：请检查 key 是否正确、是否有该模型权限"
        if "404" in msg or "not found" in msg.lower():
            return False, f"接口地址或模型不存在(404)：多为 base_url/model_name 配错，请检查"
        if "429" in msg or "quota" in msg.lower() or "rate limit" in msg.lower():
            return False, f"限流或配额不足(429)：请稍后重试或检查账户额度"
        # 其他异常(连接/超时/SSL等)
        return False, f"模型调用出错：{msg[:120]}"

    # 4) 返回为空：地址对但模型没返回正文（如纯推理流解析失败 / 模型不可用）
    if not (response or "").strip():
        return False, "模型没有返回正文：可能是模型参数不匹配或该模型不支持当前调用方式，请检查"

    return True, "✅ 连接正常"


# 会话级预检缓存：key = (format, base_url, model, api_key)，避免每次生成都重复发测试请求
_precheck_cache = {}


def precheck_llm_config(llm: dict, force: bool = False) -> tuple:
    """
    带缓存的 LLM 预检（供 GUI 在开始长任务前调用）。
    返回 (ok, msg)；同一配置只测一次（缓存），force=True 可强制重测。
    缺 LLM/缺接口格式时放行（留给上层逻辑处理），避免误阻断。
    """
    if not llm:
        return True, ""
    fp = llm.get("interface_format", "")
    bu = llm.get("base_url", "")
    mn = llm.get("model_name", "")
    ak = llm.get("api_key", "")
    if not fp:
        return True, ""
    cache_key = (fp, bu, mn, ak)
    if not force and cache_key in _precheck_cache:
        return _precheck_cache[cache_key]
    ok, msg = diagnose_llm_config(
        fp, bu, mn, ak,
        llm.get("temperature", 0.7), llm.get("max_tokens", 4096), llm.get("timeout", 30),
    )
    _precheck_cache[cache_key] = (ok, msg)
    return ok, msg
