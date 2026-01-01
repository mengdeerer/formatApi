"""主窗口UI"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QFileDialog,
    QSplitter,
    QListWidget,
    QMessageBox,
    QListWidgetItem,
    QApplication,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from pathlib import Path
import pyperclip

from services.text_parser import TextParser
from services.formatter_service import FormatterService, OutputFormat
from services.history_service import HistoryService
from services.ocr_service import OCRService, OCRMode
from utils.validators import mask_api_key
from utils.vendor_detector import get_vendor_capabilities
from ui.candidate_dialog import CandidateDialog
from ui.settings_dialog import SettingsDialog
from ui.image_drop_label import ImageDropLabel
from config import config


class OCRThread(QThread):
    """OCR识别线程（避免阻塞UI）"""

    finished = pyqtSignal(list)  # 识别完成信号
    error = pyqtSignal(str)  # 错误信号

    def __init__(self, image_paths: list, mode: OCRMode):
        super().__init__()
        self.image_paths = image_paths
        self.mode = mode

    def run(self):
        try:
            ocr_service = OCRService(self.mode)
            all_models = []
            for path in self.image_paths:
                models = ocr_service.extract_models(path)
                all_models.extend(models)

            # 去重并排序
            unique_models = sorted(list(set(all_models)))
            self.finished.emit(unique_models)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI API 配置格式化工具")

        # 设置窗口图标
        icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.setGeometry(100, 100, 1400, 900)

        # 初始化服务
        self.history_service = HistoryService()
        self.formatter_service = FormatterService()

        # 当前数据
        self.current_image_paths = []  # 支持多张图片
        self.current_models = []
        self.parsed_data = {}

        # 设置UI
        self.setup_ui()

        # 加载样式
        self.load_stylesheet()

        # 加载历史记录
        self.load_history_list()

    def setup_ui(self):
        """设置UI"""
        # 主分割器（左边操作区，右边历史记录）
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === 左侧：主操作区 ===
        left_widget = self.create_main_panel()

        # === 右侧：历史记录 ===
        right_widget = self.create_history_panel()

        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([1000, 400])

        self.setCentralWidget(splitter)

        # 创建菜单栏
        self.create_menu()

    def create_main_panel(self) -> QWidget:
        """创建主操作面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_layout = QHBoxLayout()
        title = QLabel("AI API 配置格式化工具")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0d7377; padding: 10px;")
        title_layout.addWidget(title)

        title_layout.addStretch()

        # 快捷设置按钮
        self.ocr_config_btn = QPushButton("⚙️ AI OCR 配置")
        self.ocr_config_btn.clicked.connect(self.show_settings)
        title_layout.addWidget(self.ocr_config_btn)

        self.manage_template_btn = QPushButton("📑 管理模板")
        self.manage_template_btn.clicked.connect(self.show_template_manager)
        title_layout.addWidget(self.manage_template_btn)

        layout.addLayout(title_layout)

        # 1. 文本输入区
        layout.addWidget(QLabel("粘贴包含 URL 和 API Key 的文本:"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "示例:\n"
            "https://api.openai.com/v1\n"
            "sk-xxxxxxxxxxxxx\n\n"
            "或者任意格式的文本，工具会自动识别URL和密钥"
        )
        self.text_input.setMaximumHeight(150)
        layout.addWidget(self.text_input)

        # 2. 图片上传 + OCR模式选择
        layout.addWidget(QLabel("上传模型列表图片（可选）:"))

        img_layout = QHBoxLayout()

        self.image_btn = QPushButton("选择图片")
        self.image_btn.clicked.connect(self.select_image)
        img_layout.addWidget(self.image_btn)

        img_layout.addWidget(QLabel("识别方式:"))
        self.ocr_mode_combo = QComboBox()
        self.ocr_mode_combo.addItems(["系统OCR (免费)", "AI模型 (需配置)"])
        self.ocr_mode_combo.setMinimumWidth(180)  # 设置最小宽度
        if config.ocr_mode == "ai":
            self.ocr_mode_combo.setCurrentIndex(1)
        img_layout.addWidget(self.ocr_mode_combo)

        img_layout.addStretch()
        layout.addLayout(img_layout)

        # 图片预览（支持拖放）
        self.image_label = ImageDropLabel("拖入图片或点击上方按钮选择")
        self.image_label.setMaximumHeight(120)
        # 连接拖放信号（已改为 imagesDropped）
        self.image_label.imagesDropped.connect(self.on_images_dropped)
        layout.addWidget(self.image_label)

        # 3. 模板选择（可选）
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("模板（可选）:"))
        self.template_combo = QComboBox()
        # 添加模板选项
        from services.template_service import TemplateManager

        self.template_manager = TemplateManager()
        for template_name in self.template_manager.get_template_names():
            self.template_combo.addItem(template_name)

        # 添加真正的无模板选项（只输出三个字段）
        self.template_combo.addItem("无模板")

        self.template_combo.setMinimumWidth(200)
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        layout.addLayout(template_layout)

        # 4. 输出格式选择
        # 3. 输出格式选择
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([".env", "JSON", "YAML", "TOML"])
        self.format_combo.setMinimumWidth(120)  # 设置最小宽度，避免文字被截断
        self.format_combo.setCurrentText(
            config.output_format.upper() if config.output_format != "env" else ".env"
        )
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # 4. 处理按钮
        self.process_btn = QPushButton("开始解析并格式化")
        self.process_btn.setObjectName("processBtn")
        self.process_btn.clicked.connect(self.process)
        layout.addWidget(self.process_btn)

        # 5. 结果展示
        layout.addWidget(QLabel("格式化结果:"))
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("处理结果将在这里显示...")
        layout.addWidget(self.result_output)

        # 6. 操作按钮
        btn_layout = QHBoxLayout()

        self.copy_btn = QPushButton("复制到剪贴板")
        self.copy_btn.clicked.connect(self.copy_result)
        self.copy_btn.setEnabled(False)
        btn_layout.addWidget(self.copy_btn)

        self.save_btn = QPushButton("保存为文件")
        self.save_btn.clicked.connect(self.save_result)
        self.save_btn.setEnabled(False)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        widget.setLayout(layout)
        return widget

    def create_history_panel(self) -> QWidget:
        """创建历史记录面板"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 20)

        # 标题
        title = QLabel("📚 历史记录")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)

        # 搜索框
        self.history_search = QTextEdit()
        self.history_search.setPlaceholderText("🔍 搜索...")
        self.history_search.setMaximumHeight(35)
        self.history_search.textChanged.connect(self.search_history)
        layout.addWidget(self.history_search)

        # 历史列表
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_item)
        layout.addWidget(self.history_list)

        # 操作按钮
        btn_layout = QHBoxLayout()

        self.delete_history_btn = QPushButton("🗑️ 删除")
        self.delete_history_btn.clicked.connect(self.delete_history)
        btn_layout.addWidget(self.delete_history_btn)

        self.clear_history_btn = QPushButton("🧹 清空全部")
        self.clear_history_btn.clicked.connect(self.clear_all_history)
        btn_layout.addWidget(self.clear_history_btn)

        layout.addLayout(btn_layout)

        widget.setLayout(layout)
        return widget

    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 设置菜单
        settings_menu = menubar.addMenu("⚙️ 设置")

        ai_config_action = settings_menu.addAction("AI OCR 配置")
        ai_config_action.triggered.connect(self.show_settings)

        template_manager_action = settings_menu.addAction("管理模板")
        template_manager_action.triggered.connect(self.show_template_manager)

    def load_stylesheet(self):
        """加载样式表"""
        qss_file = Path(__file__).parent / "styles.qss"
        if qss_file.exists():
            with open(qss_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def select_image(self):
        """选择图片（支持多选）"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择模型列表图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;所有文件 (*.*)",
        )

        if file_paths:
            self.load_images(file_paths)

    def on_images_dropped(self, file_paths: list):
        """处理拖入的多张图片"""
        self.load_images(file_paths)

    def load_images(self, file_paths: list):
        """加载多张图片并更新 UI"""
        self.current_image_paths = file_paths
        self.image_label.set_file_info(len(file_paths))

    def process(self):
        """处理逻辑"""
        # 1. 解析文本
        text = self.text_input.toPlainText().strip()

        if not text:
            QMessageBox.warning(self, "提示", "请输入包含URL和API Key的文本")
            return

        parser = TextParser()
        self.parsed_data = parser.parse(text)

        # 如果有多个URL候选，让用户选择
        if len(self.parsed_data.get("url_candidates", [])) > 1:
            dialog = CandidateDialog(self.parsed_data["url_candidates"], "URL", self)
            if dialog.exec():
                selected = dialog.get_selected()
                if selected:
                    self.parsed_data["base_url"] = selected

        # 如果有多个Key候选，让用户选择
        if len(self.parsed_data.get("key_candidates", [])) > 1:
            dialog = CandidateDialog(self.parsed_data["key_candidates"], "API Key", self)
            if dialog.exec():
                selected = dialog.get_selected()
                if selected:
                    self.parsed_data["api_key"] = selected

        # 验证必要字段
        if not self.parsed_data.get("base_url"):
            QMessageBox.warning(self, "提示", "未能识别到有效的URL，请检查输入")
            return

        if not self.parsed_data.get("api_key"):
            QMessageBox.warning(self, "提示", "未能识别到有效的API Key，请检查输入")
            return

        # 2. OCR识别（如果有图片）
        if self.current_image_paths:
            self.process_btn.setEnabled(False)
            self.process_btn.setText(f"🔄 正在识别 {len(self.current_image_paths)} 张图片...")

            # 判断OCR模式
            ocr_mode = OCRMode.SYSTEM if self.ocr_mode_combo.currentIndex() == 0 else OCRMode.AI

            # 使用线程避免阻塞UI
            self.ocr_thread = OCRThread(self.current_image_paths, ocr_mode)
            self.ocr_thread.finished.connect(self.on_ocr_finished)
            self.ocr_thread.error.connect(self.on_ocr_error)
            self.ocr_thread.start()
        else:
            # 没有图片，直接格式化
            self.format_and_display()

    def on_ocr_finished(self, models: list):
        """OCR识别完成"""
        self.process_btn.setEnabled(True)
        self.process_btn.setText("🚀 开始解析并格式化")

        self.current_models = models
        self.parsed_data["models"] = models

        if not models:
            QMessageBox.information(self, "提示", "未从图片中识别到模型名称")

        self.format_and_display()

    def on_ocr_error(self, error_msg: str):
        """OCR识别错误"""
        self.process_btn.setEnabled(True)
        self.process_btn.setText("🚀 开始解析并格式化")

        QMessageBox.critical(self, "OCR识别失败", f"错误: {error_msg}")

    def format_and_display(self, save_to_history: bool = True):
        """
        格式化并显示结果

        Args:
            save_to_history: 是否保存到历史记录（从历史加载时为False）
        """
        # 添加capabilities（如果没有的话）
        if "capabilities" not in self.parsed_data or not self.parsed_data["capabilities"]:
            vendor = self.parsed_data.get("vendor", "custom")
            self.parsed_data["capabilities"] = get_vendor_capabilities(vendor)

        # 检查选择了什么模板
        template_text = self.template_combo.currentText()

        # 格式映射
        format_map = {
            ".env": OutputFormat.ENV,
            "JSON": OutputFormat.JSON,
            "YAML": OutputFormat.YAML,
            "TOML": OutputFormat.TOML,
        }
        selected_format = format_map[self.format_combo.currentText()]

        if template_text == "无模板":
            # 真正的无模板 - 极简输出
            result = self.formatter_service.format_minimal(self.parsed_data, selected_format)
        elif template_text == "oai2ollama":
            # oai2ollama 标准格式（原无模板）
            result = self.formatter_service.format(self.parsed_data, selected_format)
        else:
            # 使用预设或用户模板
            template_id, template_info = self.template_manager.get_template_by_name(template_text)

            if template_id:
                try:
                    result = self.template_manager.apply_template(template_id, self.parsed_data)
                except Exception as e:
                    QMessageBox.critical(self, "模板应用失败", f"错误: {e}")
                    return
            else:
                QMessageBox.warning(self, "错误", f"未找到模板: {template_text}")
                return

        # 显示结果
        self.result_output.setText(result)

        # 启用按钮
        self.copy_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

        # 只有在新处理时才保存到历史并显示提示
        if save_to_history:
            self.history_service.add(self.parsed_data)
            self.load_history_list()
            QMessageBox.information(self, "成功", "✅ 配置已格式化完成！")

    def copy_result(self):
        """复制结果到剪贴板"""
        result = self.result_output.toPlainText()
        if result:
            pyperclip.copy(result)
            QMessageBox.information(self, "成功", "已复制到剪贴板！")

    def save_result(self):
        """保存结果为文件"""
        result = self.result_output.toPlainText()
        if not result:
            return

        # 获取文件扩展名
        format_map = {".env": ".env", "JSON": ".json", "YAML": ".yaml", "TOML": ".toml"}
        ext = format_map[self.format_combo.currentText()]

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存配置文件",
            f"api_config{ext}",
            f"配置文件 (*{ext});;所有文件 (*.*)",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(result)
                QMessageBox.information(self, "成功", f"文件已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def load_history_list(self):
        """加载历史列表"""
        self.history_list.clear()
        records = self.history_service.get_recent(20)

        for record in records:
            vendor = record.get("vendor", "custom").upper()
            base_url = record.get("base_url", "")[:35]
            api_key = mask_api_key(record.get("api_key", ""))
            created_at = record.get("created_at", "")[:10]  # 只显示日期

            display = f"[{vendor}] {base_url}...\n{api_key} | {created_at}"

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, record)
            self.history_list.addItem(item)

    def search_history(self):
        """搜索历史"""
        keyword = self.history_search.toPlainText().strip()

        self.history_list.clear()
        records = self.history_service.search(keyword)

        for record in records:
            vendor = record.get("vendor", "custom").upper()
            base_url = record.get("base_url", "")[:35]
            api_key = mask_api_key(record.get("api_key", ""))
            created_at = record.get("created_at", "")[:10]

            display = f"[{vendor}] {base_url}...\n{api_key} | {created_at}"

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, record)
            self.history_list.addItem(item)

    def load_history_item(self, item: QListWidgetItem):
        """加载历史记录项"""
        record = item.data(Qt.ItemDataRole.UserRole)

        # 填充到输入框
        text = f"{record.get('base_url', '')}\n{record.get('api_key', '')}"
        self.text_input.setText(text)

        # 设置模型
        self.current_models = record.get("models", [])
        self.parsed_data = record

        # 格式化并显示（不保存到历史，因为是从历史加载的）
        self.format_and_display(save_to_history=False)

    def delete_history(self):
        """删除选中的历史记录"""
        current_item = self.history_list.currentItem()
        if not current_item:
            return

        record = current_item.data(Qt.ItemDataRole.UserRole)
        record_id = record.get("id")

        reply = QMessageBox.question(
            self,
            "确认删除",
            "确定要删除这条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.history_service.delete(record_id)
            self.load_history_list()

    def clear_all_history(self):
        """清空所有历史记录"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.history_service.clear_all()
            self.load_history_list()
            QMessageBox.information(self, "成功", "历史记录已清空")

    def on_template_changed(self, index: int):
        """模板选择变化"""
        template_text = self.template_combo.currentText()

        if template_text == "无模板":
            self.format_combo.setEnabled(True)
            return

        # 获取模板内容
        template_id, template_info = self.template_manager.get_template_by_name(template_text)
        if template_id:
            template = template_info.get("template", "")
            if isinstance(template, (dict, list)):
                # 如果模板是 JSON 结构，锁定为 JSON 格式输出
                self.format_combo.setCurrentText("JSON")
                self.format_combo.setEnabled(False)
            else:
                # 如果模板是纯文本（.env, txt等），允许自由选择（或者保持原样）
                # 这里我们允许启用，因为模板本身可能已经是所需格式
                self.format_combo.setEnabled(True)

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def show_template_manager(self):
        """显示模板管理对话框"""
        from ui.template_manager_dialog import TemplateManagerDialog

        dialog = TemplateManagerDialog(self.template_manager, self)
        dialog.exec()

        # 对话框关闭后重新加载模板列表
        self.refresh_template_list()

    def refresh_template_list(self):
        """刷新模板下拉列表"""
        current_selection = self.template_combo.currentText()
        self.template_combo.clear()

        # 默认只有无模板选项
        self.template_combo.addItem("无模板")

        # 重新加载用户模板
        self.template_manager.load_user_templates()
        for template_name in self.template_manager.get_template_names():
            self.template_combo.addItem(template_name)

        # 恢复之前的选择（如果还存在）
        index = self.template_combo.findText(current_selection)
        if index >= 0:
            self.template_combo.setCurrentIndex(index)
