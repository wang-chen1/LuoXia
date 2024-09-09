SUPPORT_LOCALES = [
    "zh-CN",
    "zh-HK",
    "zh-TW",
    "de-DE",
    "en-US",
    "fr-FR",
    "vi-VN",
    "th-TH",
]

LLM_PROVIDERS = [
    "OpenAI",
    "Moonshot",
    "Azure",
    "Qwen",
    "DeepSeek",
    "Gemini",
    "Ollama",
    "G4f",
    "OneAPI",
    "Cloudflare",
    "ERNIE",
]

OLLAMA_HELPER = """
##### Ollama配置说明
- **API Key**: 随便填写，比如 123
- **Base Url**: 一般为 http://localhost:11434/v1
    - 如果 `MoneyPrinterTurbo` 和 `Ollama` **不在同一台机器上**，需要填写 `Ollama` 机器的IP地址
    - 如果 `MoneyPrinterTurbo` 是 `Docker` 部署，建议填写 `http://host.docker.internal:11434/v1`
- **Model Name**: 使用 `ollama list` 查看，比如 `qwen:7b`
"""

OPENAI_HELPER = """
##### OpenAI 配置说明
> 需要VPN开启全局流量模式
- **API Key**: [点击到官网申请](https://platform.openai.com/api-keys)
- **Base Url**: 可以留空
- **Model Name**: 填写**有权限**的模型，[点击查看模型列表](https://platform.openai.com/settings/organization/limits)
"""

MOOSHOT_HELPER = """
##### Moonshot 配置说明
- **API Key**: [点击到官网申请](https://platform.moonshot.cn/console/api-keys)
- **Base Url**: 固定为 https://api.moonshot.cn/v1
- **Model Name**: 比如 moonshot-v1-8k，[点击查看模型列表](https://platform.moonshot.cn/docs/intro#%E6%A8%A1%E5%9E%8B%E5%88%97%E8%A1%A8)
"""

ONE_HELPER = """
##### OneAPI 配置说明
- **API Key**: 填写您的 OneAPI 密钥
- **Base Url**: 填写 OneAPI 的基础 URL
- **Model Name**: 填写您要使用的模型名称，例如 claude-3-5-sonnet-20240620
"""

QWEN_HELPER = """
##### 通义千问Qwen 配置说明
- **API Key**: [点击到官网申请](https://dashscope.console.aliyun.com/apiKey)
- **Base Url**: 留空
- **Model Name**: 比如 qwen-max，[点击查看模型列表](https://help.aliyun.com/zh/dashscope/developer-reference/model-introduction#3ef6d0bcf91wy)
"""

G4F_HELPER = """
##### gpt4free 配置说明
> [GitHub开源项目](https://github.com/xtekky/gpt4free)，可以免费使用GPT模型，但是**稳定性较差**
- **API Key**: 随便填写，比如 123
- **Base Url**: 留空
- **Model Name**: 比如 gpt-3.5-turbo，[点击查看模型列表](https://github.com/xtekky/gpt4free/blob/main/g4f/models.py#L308)
"""

AZURE_HELPER = """
##### Azure 配置说明
> [点击查看如何部署模型](https://learn.microsoft.com/zh-cn/azure/ai-services/openai/how-to/create-resource)
- **API Key**: [点击到Azure后台创建](https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI)
- **Base Url**: 留空
- **Model Name**: 填写你实际的部署名
"""

GEMINI_HELPER = """
##### Gemini 配置说明
> 需要VPN开启全局流量模式
- **API Key**: [点击到官网申请](https://ai.google.dev/)
- **Base Url**: 留空
- **Model Name**: 比如 gemini-1.0-pro
"""

DEEPSEEK_HELPER = """
##### DeepSeek 配置说明
- **API Key**: [点击到官网申请](https://platform.deepseek.com/api_keys)
- **Base Url**: 固定为 https://api.deepseek.com
- **Model Name**: 固定为 deepseek-chat
"""

ERNIE_HELPER = """
##### 百度文心一言 配置说明
- **API Key**: [点击到官网申请](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
- **Secret Key**: [点击到官网申请](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
- **Base Url**: 填写 **请求地址** [点击查看文档](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/jlil56u11#%E8%AF%B7%E6%B1%82%E8%AF%B4%E6%98%8E)
"""
