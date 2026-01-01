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
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # AI OCR 配置组
        ai_group = QGroupBox("AI OCR 配置")
        ai_layout = QFormLayout()

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("sk-xxxxxxxxxxxxx")
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
        ai_layout.addRow("模型:", self.model_input)

        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)

        # 提示信息
        tip = QLabel("提示: AI OCR需要支持Vision的模型（如GPT-4V）")
        tip.setStyleSheet("color: #ffc93c; padding: 10px;")
        layout.addWidget(tip)

        layout.addStretch()

        # 按钮
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_settings)

        cancel_btn = QPushButton("取消")
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
