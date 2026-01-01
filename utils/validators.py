"""验证工具模块"""

import re
from typing import Optional


def is_valid_url(text: str) -> bool:
    """验证URL格式"""
    url_pattern = r"^https?://[^\s]+$"
    return bool(re.match(url_pattern, text.strip()))


def is_valid_api_key(text: str) -> bool:
    """验证API Key格式"""
    # 常见的API Key格式
    patterns = [
        r"^sk-[A-Za-z0-9]{20,}$",  # OpenAI格式
        r"^[A-Za-z0-9_-]{32,}$",  # 通用长字符串
    ]

    text = text.strip()
    return any(re.match(p, text) for p in patterns)


def extract_url(text: str) -> Optional[str]:
    """从文本中提取URL"""
    # 匹配http(s)://开头的URL
    pattern = r'https?://[^\s,;。，；\'"]+(?:/[^\s,;。，；\'"]*)?'
    match = re.search(pattern, text)
    if match:
        url = match.group(0)
        # 清理末尾的标点
        url = url.rstrip(".,;:!?。，；：！？")
        return url
    return None


def extract_api_key(text: str) -> Optional[str]:
    """从文本中提取API Key"""
    # OpenAI格式
    sk_pattern = r"sk-[A-Za-z0-9]{20,}"
    match = re.search(sk_pattern, text)
    if match:
        return match.group(0)

    # Bearer Token
    bearer_pattern = r"Bearer\s+([A-Za-z0-9_-]+)"
    match = re.search(bearer_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)

    # 通用格式：至少32个字符的字母数字组合
    # 排除明显不是key的内容（如URL）
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        # 跳过URL行
        if line.startswith("http"):
            continue
        # 匹配长字符串
        if len(line) >= 32 and re.match(r"^[A-Za-z0-9_-]+$", line):
            return line

    return None


def mask_api_key(key: str) -> str:
    """脱敏API Key显示"""
    if not key:
        return ""
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}***{key[-4:]}"
