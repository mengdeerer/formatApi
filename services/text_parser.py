"""智能文本解析服务"""

import re
from typing import Dict, List, Optional
from utils.validators import (
    extract_url,
    extract_api_key,
    is_valid_url,
    is_valid_api_key,
)
from utils.vendor_detector import detect_vendor


class TextParser:
    """智能文本解析器"""

    def __init__(self):
        pass

    def parse(self, text: str) -> Dict:
        """
        解析文本，提取URL和API Key

        Args:
            text: 输入文本

        Returns:
            {
                'base_url': 'https://...',  # 最佳匹配
                'api_key': 'sk-...',        # 最佳匹配
                'vendor': 'openai',
                'url_candidates': [...],     # 所有候选URL
                'key_candidates': [...]      # 所有候选Key
            }
        """
        result = {
            "base_url": None,
            "api_key": None,
            "vendor": "custom",
            "url_candidates": [],
            "key_candidates": [],
        }

        # 1. 查找所有可能的URL
        url_candidates = self._find_url_candidates(text)
        result["url_candidates"] = url_candidates

        # 选择最佳URL
        if url_candidates:
            result["base_url"] = url_candidates[0]["value"]

        # 2. 查找所有可能的API Key
        key_candidates = self._find_key_candidates(text)
        result["key_candidates"] = key_candidates

        # 选择最佳Key
        if key_candidates:
            result["api_key"] = key_candidates[0]["value"]

        # 3. 推断厂商
        if result["base_url"]:
            result["vendor"] = detect_vendor(result["base_url"])

        return result

    def _find_url_candidates(self, text: str) -> List[Dict]:
        """
        查找所有可能的URL

        Returns:
            [{'value': 'https://...', 'score': 0.9}, ...]
        """
        candidates = []

        # 匹配所有URL
        pattern = r'https?://[^\s,;。，；\'"]+(?:/[^\s,;。，；\'"]*)?'
        matches = re.finditer(pattern, text)

        for match in matches:
            url = match.group(0)
            # 清理末尾标点
            url = url.rstrip(".,;:!?。，；：！？")

            if is_valid_url(url):
                score = self._score_url(url)
                candidates.append({"value": url, "score": score})

        # 按分数排序
        candidates.sort(key=lambda x: x["score"], reverse=True)

        # 去重
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c["value"] not in seen:
                seen.add(c["value"])
                unique_candidates.append(c)

        return unique_candidates

    def _find_key_candidates(self, text: str) -> List[Dict]:
        """
        查找所有可能的API Key

        Returns:
            [{'value': 'sk-...', 'score': 0.9}, ...]
        """
        candidates = []

        # 1. 查找sk-开头的（OpenAI格式）
        sk_pattern = r"sk-[A-Za-z0-9]{20,}"
        for match in re.finditer(sk_pattern, text):
            key = match.group(0)
            candidates.append(
                {
                    "value": key,
                    "score": 0.95,  # 高置信度
                }
            )

        # 2. 查找Bearer Token
        bearer_pattern = r"Bearer\s+([A-Za-z0-9_-]{20,})"
        for match in re.finditer(bearer_pattern, text, re.IGNORECASE):
            key = match.group(1)
            candidates.append({"value": key, "score": 0.9})

        # 3. 查找其他长字符串（排除URL）
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # 跳过URL行
            if line.startswith("http"):
                continue
            # 跳过包含中文的行
            if re.search(r"[\u4e00-\u9fff]", line):
                continue
            # 匹配32-100个字符的字母数字组合
            if 32 <= len(line) <= 100 and re.match(r"^[A-Za-z0-9_-]+$", line):
                candidates.append(
                    {
                        "value": line,
                        "score": 0.7,  # 中等置信度
                    }
                )

        # 按分数排序
        candidates.sort(key=lambda x: x["score"], reverse=True)

        # 去重
        seen = set()
        unique_candidates = []
        for c in candidates:
            if c["value"] not in seen:
                seen.add(c["value"])
                unique_candidates.append(c)

        return unique_candidates

    def _score_url(self, url: str) -> float:
        """
        给URL打分

        评分规则：
        - 包含/v1: +0.3
        - HTTPS: +0.1
        - 已知厂商域名: +0.2
        - 基础分: 0.4
        """
        score = 0.4

        url_lower = url.lower()

        # 包含API版本号
        if "/v1" in url_lower:
            score += 0.3

        # HTTPS
        if url_lower.startswith("https://"):
            score += 0.1

        # 已知厂商
        known_domains = [
            "openai.com",
            "anthropic.com",
            "googleapis.com",
            "deepseek",
            "zhipuai",
            "moonshot",
        ]
        if any(domain in url_lower for domain in known_domains):
            score += 0.2

        return min(score, 1.0)
