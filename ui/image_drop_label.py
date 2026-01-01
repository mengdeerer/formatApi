"""支持拖放的图片标签组件"""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class ImageDropLabel(QLabel):
    """支持多图拖放的图片预览标签"""

    # 信号：当图片被拖入时发出（发送图片文件路径列表）
    imagesDropped = pyqtSignal(list)

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.default_text = text
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)

        self.default_style = (
            "background-color: #2d2d2d; "
            "border: 2px dashed #3a3a3a; "
            "border-radius: 5px; "
            "padding: 10px;"
        )
        self.hover_style = (
            "background-color: #3a3a3a; "
            "border: 2px dashed #0d7377; "
            "border-radius: 5px; "
            "padding: 10px; "
            "color: #0d7377;"
        )
        self.setStyleSheet(self.default_style)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if any(self._is_image_file(u.toLocalFile()) for u in urls):
                event.acceptProposedAction()
                self.setStyleSheet(self.hover_style)
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.default_style)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(self.default_style)

        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if self._is_image_file(path):
                    file_paths.append(path)

            if file_paths:
                self.imagesDropped.emit(file_paths)
                event.acceptProposedAction()
                return

        event.ignore()

    def set_file_info(self, count: int):
        """显示文件数量信息"""
        if count <= 0:
            self.setText(self.default_text)
        else:
            self.setText(f"已加载 {count} 张图片")

    def _is_image_file(self, file_path: str) -> bool:
        image_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}
        return any(file_path.lower().endswith(ext) for ext in image_extensions)
