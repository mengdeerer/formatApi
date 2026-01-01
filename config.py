"""配置管理模块"""

import json
from pathlib import Path


class Config:
    """应用配置管理"""

    def __init__(self):
        self.config_dir = Path.home() / ".formatapi"
        self.config_file = self.config_dir / "config.json"
        self.history_file = self.config_dir / "history.json"
        self.templates_dir = self.config_dir / "templates"

        # 确保配置目录存在
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)

        # 默认配置
        self.default_config = {
            "ocr_mode": "system",  # system 或 ai
            "ai_api_key": "",
            "ai_base_url": "https://api.openai.com/v1",
            "ai_model": "gpt-4-vision-preview",
            "output_format": "env",  # env, json, yaml, toml
            "theme": "dark",
        }

        self._config = self.load()

    def load(self) -> dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return {**self.default_config, **json.load(f)}
            except Exception as e:
                print(f"加载配置失败: {e}")
                return self.default_config.copy()
        return self.default_config.copy()

    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key: str, default=None):
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key: str, value):
        """设置配置项"""
        self._config[key] = value
        self.save()

    @property
    def ocr_mode(self) -> str:
        return self._config.get("ocr_mode", "system")

    @ocr_mode.setter
    def ocr_mode(self, value: str):
        self.set("ocr_mode", value)

    @property
    def ai_api_key(self) -> str:
        return self._config.get("ai_api_key", "")

    @ai_api_key.setter
    def ai_api_key(self, value: str):
        self.set("ai_api_key", value)

    @property
    def ai_base_url(self) -> str:
        return self._config.get("ai_base_url", "https://api.openai.com/v1")

    @ai_base_url.setter
    def ai_base_url(self, value: str):
        self.set("ai_base_url", value)

    @property
    def ai_model(self) -> str:
        return self._config.get("ai_model", "gpt-4-vision-preview")

    @ai_model.setter
    def ai_model(self, value: str):
        self.set("ai_model", value)

    @property
    def output_format(self) -> str:
        return self._config.get("output_format", "env")

    @output_format.setter
    def output_format(self, value: str):
        self.set("output_format", value)


# 全局配置实例
config = Config()
