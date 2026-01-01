"""OCR识别服务（系统OCR + AI模型）"""

import base64
import re
from enum import Enum
from typing import List, Optional
from pathlib import Path
from config import config


class OCRMode(Enum):
    """OCR识别模式"""

    SYSTEM = "system"  # macOS系统OCR
    AI = "ai"  # AI模型（GPT-4V）


class OCRService:
    """图片识别服务"""

    def __init__(self, mode: OCRMode = OCRMode.SYSTEM):
        self.mode = mode

    def extract_models(self, image_path: str) -> List[str]:
        """
        从图片提取模型名称

        Args:
            image_path: 图片路径

        Returns:
            模型名称列表
        """
        try:
            if self.mode == OCRMode.SYSTEM:
                return self._extract_with_system(image_path)
            else:
                return self._extract_with_ai(image_path)
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return []

    def _extract_with_system(self, image_path: str) -> List[str]:
        """使用macOS系统OCR"""
        try:
            # 尝试使用Vision框架
            raw_text = self._system_ocr_recognize(image_path)
            return self._parse_model_names(raw_text)
        except ImportError:
            raise RuntimeError("系统OCR需要安装: pip install pyobjc-framework-Vision")
        except Exception as e:
            raise RuntimeError(f"系统OCR识别失败: {e}")

    def _system_ocr_recognize(self, image_path: str) -> str:
        """调用系统OCR识别"""
        try:
            from Cocoa import NSURL
            from Vision import VNRecognizeTextRequest, VNImageRequestHandler

            # 创建图片URL
            url = NSURL.fileURLWithPath_(image_path)

            # 创建请求处理器
            handler = VNImageRequestHandler.alloc().initWithURL_options_(url, None)

            # 创建文本识别请求
            request = VNRecognizeTextRequest.alloc().init()
            request.setRecognitionLevel_(1)  # 1=精确模式

            # 执行识别
            success, error = handler.performRequests_error_([request], None)

            if not success:
                raise RuntimeError(f"识别失败: {error}")

            # 提取结果
            results = request.results()
            if not results:
                return ""

            # 合并所有识别的文本
            texts = []
            for observation in results:
                candidates = observation.topCandidates_(1)
                if candidates:
                    texts.append(candidates[0].string())

            return "\n".join(texts)

        except ImportError as e:
            # 如果无法导入Vision框架，返回提示
            raise ImportError(
                "系统OCR不可用，请安装: pip install pyobjc-framework-Vision pyobjc-framework-Quartz"
            )

    def _extract_with_ai(self, image_path: str) -> List[str]:
        """使用AI模型（GPT-4V）"""
        try:
            # 读取图片并转base64
            with open(image_path, "rb") as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode("utf-8")

            # 调用AI API
            ai_client = AIOCRClient()
            models_text = ai_client.extract_models(img_base64)

            # 解析返回的模型列表
            models = [m.strip() for m in models_text.split("\n") if m.strip()]
            return models

        except Exception as e:
            raise RuntimeError(f"AI OCR识别失败: {e}")

    def _parse_model_names(self, text: str) -> List[str]:
        """
        从文本中解析模型名称

        常见模型命名模式：
        - gpt-4-turbo, gpt-3.5-turbo
        - claude-3-opus, claude-3-sonnet
        - gemini-pro, gemini-1.5-pro
        - 带日期的: claude-opus-4-5-20251001
        """
        patterns = [
            r"gpt-[\w.-]+",
            r"claude-[\w.-]+",
            r"gemini-[\w.-]+",
            r"deepseek-[\w.-]+",
            r"glm-[\w.-]+",
            r"moonshot-[\w.-]+",
            r"[\w-]+-\d{8,}",  # 带日期格式
            r"o1-[\w.-]+",  # OpenAI o1系列
            r"text-[\w.-]+",  # text-embedding等
        ]

        models = set()

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # 清理和验证
                model = match.strip().lower()
                # 过滤太短或太长的
                if 3 <= len(model) <= 80:
                    models.add(model)

        # 排序并返回
        return sorted(list(models))


class AIOCRClient:
    """AI模型OCR客户端（GPT-4V）"""

    def __init__(self):
        self.api_key = config.ai_api_key
        self.base_url = config.ai_base_url
        self.model = config.ai_model

        if not self.api_key:
            raise ValueError("未配置AI API密钥，请在设置中配置")

    def extract_models(self, image_base64: str) -> str:
        """
        调用GPT-4V提取模型名称

        Args:
            image_base64: Base64编码的图片

        Returns:
            模型名称列表（每行一个）
        """
        import requests

        prompt = """请从这张图片中提取所有AI模型名称。

要求：
1. 只返回模型名称，每行一个
2. 不要添加序号、说明文字或其他内容
3. 保持原始格式（如大小写、连字符）
4. 如果是表格，提取模型名称列

示例输出格式：
gpt-4-turbo
gpt-3.5-turbo
claude-3-opus-20240229
"""

        # 构建请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 判断是否是OpenAI格式的API
        if "openai" in self.base_url.lower() or "/v1" in self.base_url:
            # OpenAI格式
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                            },
                        ],
                    }
                ],
                "max_tokens": 2000,
            }
        else:
            raise ValueError("暂不支持该API格式，请使用OpenAI兼容的API")

        # 发送请求
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        # 解析响应
        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return content
