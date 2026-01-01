"""模板管理对话框"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QTextEdit,
    QLabel,
    QMessageBox,
    QInputDialog,
    QListWidgetItem,
    QSplitter,
)
from PyQt6.QtCore import Qt
import json


class TemplateManagerDialog(QDialog):
    """模板管理对话框"""

    def __init__(self, template_manager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle("模板管理")
        self.setGeometry(200, 200, 900, 600)
        self.selected_template_id = None

        self.setup_ui()
        self.load_template_list()

    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # 标题
        title = QLabel("模板管理")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # 主分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧：模板列表
        left_widget = self.create_template_list_panel()
        splitter.addWidget(left_widget)

        # 右侧：模板内容预览
        right_widget = self.create_template_preview_panel()
        splitter.addWidget(right_widget)

        splitter.setSizes([300, 600])
        layout.addWidget(splitter)

        # 底部按钮
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("保存为新模板")
        self.save_btn.clicked.connect(self.save_as_new_template)
        btn_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("删除模板")
        self.delete_btn.clicked.connect(self.delete_template)
        self.delete_btn.setEnabled(False)
        btn_layout.addWidget(self.delete_btn)

        btn_layout.addStretch()

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def create_template_list_panel(self):
        """创建模板列表面板"""
        from PyQt6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        label = QLabel("可用模板")
        label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(label)

        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.on_template_selected)
        layout.addWidget(self.template_list)

        widget.setLayout(layout)
        return widget

    def create_template_preview_panel(self):
        """创建模板预览面板"""
        from PyQt6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题
        label = QLabel("模板内容")
        label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(label)

        # 模板内容编辑器
        self.template_content = QTextEdit()
        self.template_content.setPlaceholderText("选择或导入模板以查看内容...")
        layout.addWidget(self.template_content)

        widget.setLayout(layout)
        return widget

    def load_template_list(self):
        """加载模板列表"""
        self.template_list.clear()
        all_templates = self.template_manager.get_all_templates()

        for template_id, info in all_templates.items():
            name = info["name"]
            is_preset = info.get("is_preset", False)
            display = f"{'[锁定] ' if is_preset else ''}{name}"

            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, template_id)
            self.template_list.addItem(item)

    def on_template_selected(self, item: QListWidgetItem):
        """选中模板时"""
        template_id = item.data(Qt.ItemDataRole.UserRole)
        self.selected_template_id = template_id

        all_templates = self.template_manager.get_all_templates()
        template_info = all_templates.get(template_id, {})

        # 显示模板内容
        template_data = template_info.get("template", "")
        if isinstance(template_data, (dict, list)):
            self.template_content.setText(json.dumps(template_data, indent=2, ensure_ascii=False))
        else:
            self.template_content.setText(str(template_data))

        # 更新删除按钮状态（预设模板不可删除）
        is_preset = template_info.get("is_preset", False)
        self.delete_btn.setEnabled(not is_preset)

    def save_as_new_template(self):
        """保存为新模板"""
        content = self.template_content.toPlainText().strip()

        if not content:
            QMessageBox.warning(self, "提示", "请先导入或编辑模板内容")
            return

        # 尝试验证 JSON 格式（可选，仅用于美化预览）
        try:
            template_data = json.loads(content)
        except json.JSONDecodeError:
            # 如果不是 JSON，则作为普通字符串处理
            template_data = content

        # 输入模板名称
        name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")

        if ok and name:
            # 输入描述（可选）
            description, _ = QInputDialog.getText(self, "模板描述", "请输入模板描述（可选）:")

            # 保存模板
            success = self.template_manager.save_user_template(name, template_data, description)

            if success:
                QMessageBox.information(self, "成功", f"模板 '{name}' 已保存")
                self.load_template_list()
                self.template_content.clear()
            else:
                QMessageBox.critical(
                    self, "保存失败", "保存模板失败，请检查模板名称是否与预设模板重复"
                )

    def delete_template(self):
        """删除模板"""
        if not self.selected_template_id:
            return

        all_templates = self.template_manager.get_all_templates()
        template_info = all_templates.get(self.selected_template_id, {})
        name = template_info.get("name", "")

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除模板 '{name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.template_manager.delete_user_template(self.selected_template_id)

            if success:
                QMessageBox.information(self, "成功", f"模板 '{name}' 已删除")
                self.load_template_list()
                self.template_content.clear()
                self.selected_template_id = None
                self.delete_btn.setEnabled(False)
            else:
                QMessageBox.critical(self, "删除失败", "无法删除预设模板")
