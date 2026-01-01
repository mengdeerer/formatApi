"""候选项选择对话框"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, QSize
from typing import List, Dict, Optional


class CandidateDialog(QDialog):
    """候选项选择对话框"""

    def __init__(self, candidates: List[Dict], item_type: str, parent=None):
        """
        Args:
            candidates: 候选项列表 [{'value': '...', 'score': 0.9}, ...]
            item_type: 类型描述（如'URL'或'API Key'）
        """
        super().__init__(parent)
        self.setWindowTitle(f"选择 {item_type}")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(300)

        layout = QVBoxLayout()

        # 提示文字
        tip_text = f"🔍 检测到 {len(candidates)} 个可能的 {item_type}，请选择一个："
        tip = QLabel(tip_text)
        tip.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(tip)

        # 候选列表
        self.list_widget = QListWidget()
        self.list_widget.setWordWrap(True)  # 允许文字换行
        self.list_widget.setStyleSheet("""
            QListWidget {
                font-size: 13px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #3a3a3a;
                min-height: 60px;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
            }
        """)

        for idx, item in enumerate(candidates):
            value = item["value"]
            score = item.get("score", 0)

            # 置信度显示
            if score > 0.8:
                confidence = "高 ✓"
            elif score > 0.5:
                confidence = "中 ~"
            else:
                confidence = "低 ?"

            display = f"{value}\n置信度: {confidence} ({score:.0%})"

            list_item = QListWidgetItem(display)
            list_item.setData(Qt.ItemDataRole.UserRole, value)
            # 设置合适的高度以容纳两行文字
            list_item.setSizeHint(QSize(0, 70))
            self.list_widget.addItem(list_item)

            # 默认选中第一个（置信度最高）
            if idx == 0:
                self.list_widget.setCurrentRow(0)

        layout.addWidget(self.list_widget)

        # 按钮
        btn_layout = QHBoxLayout()

        confirm_btn = QPushButton("✓ 确认选择")
        confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
        """)
        confirm_btn.clicked.connect(self.accept)

        cancel_btn = QPushButton("✗ 取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #393e46;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4a515c;
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.candidates = candidates

    def get_selected(self) -> Optional[str]:
        """获取选中的值"""
        if self.result() == QDialog.DialogCode.Accepted:
            current_item = self.list_widget.currentItem()
            if current_item:
                return current_item.data(Qt.ItemDataRole.UserRole)
        return None
