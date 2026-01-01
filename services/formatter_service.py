"""格式化输出服务"""

import json
import yaml
import toml
from enum import Enum
from typing import Dict
from utils.vendor_detector import get_env_prefix, get_vendor_capabilities


class OutputFormat(Enum):
    """输出格式枚举"""

    ENV = "env"
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


class FormatterService:
    """格式化输出服务"""

    def format(self, data: Dict, output_format: OutputFormat) -> str:
        """
        格式化配置数据

        Args:
            data: {
                'api_key': 'sk-...',
                'base_url': 'https://...',
                'vendor': 'openai',
                'models': ['gpt-4', 'gpt-3.5'],
                'capabilities': ['vision', 'thinking']
            }
            output_format: 输出格式

        Returns:
            格式化后的字符串
        """
        if output_format == OutputFormat.ENV:
            return self._to_env(data)
        elif output_format == OutputFormat.JSON:
            return self._to_json(data)
        elif output_format == OutputFormat.YAML:
            return self._to_yaml(data)
        elif output_format == OutputFormat.TOML:
            return self._to_toml(data)
        else:
            return self._to_env(data)

    def _to_env(self, data: Dict) -> str:
        """生成.env格式"""
        vendor = data.get("vendor", "custom")
        prefix = get_env_prefix(vendor)

        lines = []

        # API Key
        if data.get("api_key"):
            lines.append(f"{prefix}_API_KEY={data['api_key']}")

        # Base URL
        if data.get("base_url"):
            lines.append(f"{prefix}_BASE_URL={data['base_url']}")

        # Host (固定值)
        lines.append("HOST=0.0.0.0")

        # Capabilities
        capabilities = data.get("capabilities", [])
        if not capabilities:
            capabilities = get_vendor_capabilities(vendor)
        lines.append(f"CAPABILITIES={json.dumps(capabilities)}")

        # Models
        models = data.get("models", [])
        if models:
            lines.append(f"MODELS={json.dumps(models)}")

        return "\n".join(lines)

    def _to_json(self, data: Dict) -> str:
        """生成JSON格式"""
        vendor = data.get("vendor", "custom")

        output = {}

        if data.get("api_key"):
            output["api_key"] = data["api_key"]

        if data.get("base_url"):
            output["base_url"] = data["base_url"]

        output["host"] = "0.0.0.0"

        capabilities = data.get("capabilities", [])
        if not capabilities:
            capabilities = get_vendor_capabilities(vendor)
        output["capabilities"] = capabilities

        models = data.get("models", [])
        if models:
            output["models"] = models

        return json.dumps(output, indent=2, ensure_ascii=False)

    def _to_yaml(self, data: Dict) -> str:
        """生成YAML格式"""
        vendor = data.get("vendor", "custom")

        output = {}

        if data.get("api_key"):
            output["api_key"] = data["api_key"]

        if data.get("base_url"):
            output["base_url"] = data["base_url"]

        output["host"] = "0.0.0.0"

        capabilities = data.get("capabilities", [])
        if not capabilities:
            capabilities = get_vendor_capabilities(vendor)
        output["capabilities"] = capabilities

        models = data.get("models", [])
        if models:
            output["models"] = models

        return yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def _to_toml(self, data: Dict) -> str:
        """生成TOML格式"""
        vendor = data.get("vendor", "custom")

        output = {}

        if data.get("api_key"):
            output["api_key"] = data["api_key"]

        if data.get("base_url"):
            output["base_url"] = data["base_url"]

        output["host"] = "0.0.0.0"

        capabilities = data.get("capabilities", [])
        if not capabilities:
            capabilities = get_vendor_capabilities(vendor)
        output["capabilities"] = capabilities

        models = data.get("models", [])
        if models:
            output["models"] = models

        return toml.dumps(output)

    def format_minimal(self, data: Dict, output_format: OutputFormat) -> str:
        """
        极简格式化 - 只输出 api_key, base_url, model

        Args:
            data: 原始数据
            output_format: 输出格式

        Returns:
            格式化后的字符串
        """
        output = {}

        if data.get("api_key"):
            output["api_key"] = data["api_key"]

        if data.get("base_url"):
            output["base_url"] = data["base_url"]

        # 获取所有模型
        models = data.get("models", [])
        if models:
            output["models"] = models

        # 根据格式输出
        if output_format == OutputFormat.ENV:
            lines = []
            if "api_key" in output:
                lines.append(f"API_KEY={output['api_key']}")
            if "base_url" in output:
                lines.append(f"BASE_URL={output['base_url']}")
            if "models" in output:
                lines.append(f"MODELS={json.dumps(output['models'])}")
            return "\n".join(lines)
        elif output_format == OutputFormat.JSON:
            return json.dumps(output, indent=2, ensure_ascii=False)
        elif output_format == OutputFormat.YAML:
            return yaml.dump(output, allow_unicode=True, default_flow_style=False, sort_keys=False)
        elif output_format == OutputFormat.TOML:
            return toml.dumps(output)
        else:
            return json.dumps(output, indent=2, ensure_ascii=False)

    def get_file_extension(self, output_format: OutputFormat) -> str:
        """获取文件扩展名"""
        extension_map = {
            OutputFormat.ENV: ".env",
            OutputFormat.JSON: ".json",
            OutputFormat.YAML: ".yaml",
            OutputFormat.TOML: ".toml",
        }
        return extension_map.get(output_format, ".txt")
