"""历史记录服务（JSON文件存储）"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import config


class HistoryService:
    """历史记录管理服务"""

    def __init__(self):
        self.history_file = config.history_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """确保历史文件存在"""
        if not self.history_file.exists():
            self._save_history([])

    def _load_history(self) -> List[Dict]:
        """加载历史记录"""
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            return []

    def _save_history(self, history: List[Dict]):
        """保存历史记录"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def add(self, data: Dict):
        """
        添加历史记录

        Args:
            data: {
                'vendor': 'openai',
                'base_url': 'https://...',
                'api_key': 'sk-...',
                'models': ['gpt-4'],
                'capabilities': ['vision']
            }
        """
        history = self._load_history()

        # 创建新记录
        record = {
            "id": self._generate_id(history),
            "vendor": data.get("vendor", "custom"),
            "base_url": data.get("base_url", ""),
            "api_key": data.get("api_key", ""),
            "models": data.get("models", []),
            "capabilities": data.get("capabilities", []),
            "created_at": datetime.now().isoformat(),
        }

        # 添加到列表开头（最新的在前）
        history.insert(0, record)

        # 限制历史记录数量（最多保留100条）
        if len(history) > 100:
            history = history[:100]

        self._save_history(history)

    def get_recent(self, limit: int = 20) -> List[Dict]:
        """获取最近的记录"""
        history = self._load_history()
        return history[:limit]

    def delete(self, record_id: int):
        """删除记录"""
        history = self._load_history()
        history = [r for r in history if r.get("id") != record_id]
        self._save_history(history)

    def clear_all(self):
        """清空所有历史记录"""
        self._save_history([])

    def search(self, keyword: str) -> List[Dict]:
        """
        搜索记录

        Args:
            keyword: 搜索关键词（匹配vendor或base_url）
        """
        if not keyword:
            return self.get_recent(20)

        history = self._load_history()
        keyword_lower = keyword.lower()

        results = []
        for record in history:
            vendor = record.get("vendor", "").lower()
            base_url = record.get("base_url", "").lower()

            if keyword_lower in vendor or keyword_lower in base_url:
                results.append(record)

        return results

    def _generate_id(self, history: List[Dict]) -> int:
        """生成新的记录ID"""
        if not history:
            return 1
        max_id = max(r.get("id", 0) for r in history)
        return max_id + 1
