"""设置对话框"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QFormLayout,
)
from config import config


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI OCR 配置")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # AI OCR 配置组
        ai_group = QGroupBox("配置参数")
        ai_layout = QFormLayout()
        ai_layout.setSpacing(15)
        ai_layout.setContentsMargins(15, 20, 15, 15)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入 API Key")
        self.api_key_input.setText(config.ai_api_key)
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        ai_layout.addRow("API Key:", self.api_key_input)

        # Base URL
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.openai.com/v1")
        self.base_url_input.setText(config.ai_base_url)
        ai_layout.addRow("Base URL:", self.base_url_input)

        # Model
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("gpt-4-vision-preview")
        self.model_input.setText(config.ai_model)
        ai_layout.addRow("识别模型:", self.model_input)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # 提示信息
        tip_layout = QHBoxLayout()
        tip_icon = QLabel("💡")
        tip_icon.setStyleSheet("font-size: 16px;")
        tip = QLabel("AI OCR 需要支持 Vision 的模型（如 GPT-4V 或 Claude 3.5 Sonnet）")
        tip.setWordWrap(True)
        tip.setObjectName("settingsTip")
        tip_layout.addWidget(tip_icon)
        tip_layout.addWidget(tip)
        layout.addLayout(tip_layout)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setMinimumHeight(40)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(40)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_settings(self):
        """保存设置"""
        config.ai_api_key = self.api_key_input.text().strip()
        config.ai_base_url = self.base_url_input.text().strip()
        config.ai_model = self.model_input.text().strip()

        self.accept()
