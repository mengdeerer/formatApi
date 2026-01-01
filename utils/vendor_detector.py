"""厂商识别工具"""

from typing import List, Optional


# 厂商特征配置
VENDOR_CONFIG = {
    "openai": {
        "keywords": ["openai.com", "openai"],
        "capabilities": ["vision", "function_calling", "stream"],
        "env_prefix": "OPENAI",
    },
    "anthropic": {
        "keywords": ["anthropic.com", "claude"],
        "capabilities": ["vision", "thinking", "stream"],
        "env_prefix": "ANTHROPIC",
    },
    "google": {
        "keywords": ["generativeai", "gemini", "googleapis", "google"],
        "capabilities": ["vision", "multimodal"],
        "env_prefix": "GOOGLE",
    },
    "deepseek": {
        "keywords": ["deepseek"],
        "capabilities": ["vision", "reasoning"],
        "env_prefix": "DEEPSEEK",
    },
    "zhipu": {
        "keywords": ["zhipuai", "chatglm"],
        "capabilities": ["vision"],
        "env_prefix": "ZHIPU",
    },
    "moonshot": {
        "keywords": ["moonshot", "kimi"],
        "capabilities": ["long_context"],
        "env_prefix": "MOONSHOT",
    },
    "custom": {"keywords": [], "capabilities": ["stream"], "env_prefix": "CUSTOM"},
}


def detect_vendor(url: str) -> str:
    """
    从URL检测厂商

    Args:
        url: API的base URL

    Returns:
        厂商名称（小写）
    """
    if not url:
        return "custom"

    url_lower = url.lower()

    for vendor, config in VENDOR_CONFIG.items():
        if vendor == "custom":
            continue
        for keyword in config["keywords"]:
            if keyword in url_lower:
                return vendor

    return "custom"


def get_vendor_capabilities(vendor: str) -> List[str]:
    """获取厂商默认能力"""
    return VENDOR_CONFIG.get(vendor, VENDOR_CONFIG["custom"])["capabilities"]


def get_env_prefix(vendor: str) -> str:
    """获取环境变量前缀"""
    return VENDOR_CONFIG.get(vendor, VENDOR_CONFIG["custom"])["env_prefix"]


def get_all_vendors() -> List[str]:
    """获取所有支持的厂商列表"""
    return list(VENDOR_CONFIG.keys())
