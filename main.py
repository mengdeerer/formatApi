"""formatApi - 程序入口

功能：
1. 智能解析文本中的URL和API Key
2. 支持系统OCR和AI模型双模式识别图片中的模型列表
3. 多格式输出（.env, JSON, YAML, TOML）
4. 历史记录管理
"""

import sys
import os
from pathlib import Path

# 抑制 macOS 特有的 TSMSendMessageToUIServer 错误消息（通常为系统环境性误报警）
if sys.platform == "darwin":
    os.environ["QT_MAC_WANTS_LAYER"] = "1"
    # 同时抑制部分已知的字体/底层通信警告输出到终端
    os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false;qt.qpa.input.methods=false"

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置应用图标
    from PyQt6.QtGui import QIcon
    from pathlib import Path

    icon_path = Path(__file__).parent / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 设置应用信息
    app.setApplicationName("formatApi")
    app.setOrganizationName("FormatAPI")

    # 创建主窗口
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
