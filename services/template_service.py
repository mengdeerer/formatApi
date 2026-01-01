"""配置模板管理"""

import json
from typing import Dict, List


# 预设模板配置 - 现已清空，全部由用户自定义
TEMPLATES = {}


class TemplateManager:
    """模板管理器"""

    def __init__(self):
        from config import config

        self.templates_dir = config.templates_dir
        self._user_templates = {}
        self.load_user_templates()

    def get_all_templates(self) -> Dict[str, Dict]:
        """获取所有模板（预设 + 用户）"""
        return {**TEMPLATES, **self._user_templates}

    def get_template_names(self) -> List[str]:
        """获取所有模板名称（用于显示）"""
        all_templates = self.get_all_templates()
        return [info["name"] for info in all_templates.values()]

    def get_template_by_name(self, display_name: str) -> tuple[str, Dict]:
        """通过显示名称获取模板ID和内容"""
        all_templates = self.get_all_templates()
        for template_id, info in all_templates.items():
            if info["name"] == display_name:
                return template_id, info
        return None, None

    def load_user_templates(self):
        """从磁盘加载用户自定义模板"""
        self._user_templates = {}
        if not self.templates_dir.exists():
            return

        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template_data = json.load(f)
                    template_id = template_file.stem
                    self._user_templates[template_id] = {
                        "name": template_data.get("name", template_id),
                        "description": template_data.get("description", "用户自定义模板"),
                        "template": template_data.get("template", ""),
                        "is_preset": False,
                    }
            except Exception as e:
                print(f"加载模板失败 {template_file}: {e}")

    def save_user_template(self, name: str, template_data: dict, description: str = "") -> bool:
        """
        保存用户自定义模板

        Args:
            name: 模板名称
            template_data: 模板数据（JSON 对象或字符串）
            description: 模板描述

        Returns:
            是否保存成功
        """
        try:
            # 生成模板ID（使用名称的小写加下划线）
            template_id = name.lower().replace(" ", "_").replace("-", "_")

            # 防止覆盖预设模板
            if template_id in TEMPLATES:
                raise ValueError("不能使用预设模板名称")

            template_file = self.templates_dir / f"{template_id}.json"

            save_data = {
                "name": name,
                "description": description,
                "template": template_data,
            }

            with open(template_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            # 重新加载用户模板
            self.load_user_templates()
            return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False

    def delete_user_template(self, template_id: str) -> bool:
        """
        删除用户自定义模板

        Args:
            template_id: 模板ID

        Returns:
            是否删除成功
        """
        # 不能删除预设模板
        if template_id in TEMPLATES:
            return False

        try:
            template_file = self.templates_dir / f"{template_id}.json"
            if template_file.exists():
                template_file.unlink()
                self.load_user_templates()
                return True
            return False
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False

    def apply_template(self, template_id: str, data: Dict) -> str:
        """
        应用模板并填充数据（智能识别字段）

        Args:
            template_id: 模板ID
            data: {
                'api_key': 'sk-...',
                'base_url': 'https://...',
                'models': ['model1', 'model2', ...]
            }

        Returns:
            格式化后的JSON字符串
        """
        all_templates = self.get_all_templates()
        template_info = all_templates[template_id]
        template = template_info["template"]

        # 获取所有模型
        models = data.get("models", [])
        first_model = models[0] if models else ""

        # 如果模板是字符串，直接进行占位符替换
        if isinstance(template, str):
            result = (
                template.replace("{api_key}", data.get("api_key", ""))
                .replace("{base_url}", data.get("base_url", ""))
                .replace("{model}", first_model)
            )
            return result

        # 深拷贝模板
        import copy

        result = copy.deepcopy(template)

        # 智能替换：递归查找并替换可能的字段
        def smart_replace(obj, path=""):
            if isinstance(obj, dict):
                new_obj = {}
                for k, v in obj.items():
                    current_path = f"{path}.{k}" if path else k
                    key_lower = k.lower()

                    # 检查是否是需要替换的字段
                    if isinstance(v, str):
                        # API Key 相关字段
                        if any(
                            keyword in key_lower
                            for keyword in ["api_key", "apikey", "key", "token", "auth"]
                        ):
                            if "api_key" in data and data["api_key"]:
                                new_obj[k] = data["api_key"]
                            else:
                                new_obj[k] = v.replace("{api_key}", data.get("api_key", ""))
                        # URL 相关字段
                        elif any(keyword in key_lower for keyword in ["url", "endpoint", "base"]):
                            if "base_url" in data and data["base_url"]:
                                new_obj[k] = data["base_url"]
                            else:
                                new_obj[k] = v.replace("{base_url}", data.get("base_url", ""))
                        # Model 相关字段
                        elif (
                            any(keyword in key_lower for keyword in ["model"])
                            and "name" not in key_lower
                        ):
                            if models:
                                new_obj[k] = models
                            else:
                                new_obj[k] = v.replace("{model}", first_model)
                        else:
                            # 普通字符串，替换占位符
                            new_obj[k] = (
                                v.replace("{api_key}", data.get("api_key", ""))
                                .replace("{base_url}", data.get("base_url", ""))
                                .replace("{model}", first_model)
                            )
                    else:
                        new_obj[k] = smart_replace(v, current_path)
                return new_obj
            elif isinstance(obj, list):
                return [smart_replace(item, path) for item in obj]
            else:
                return obj

        result = smart_replace(result)

        # 格式化为JSON
        return json.dumps(result, indent=2, ensure_ascii=False)
