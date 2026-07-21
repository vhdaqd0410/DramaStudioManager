from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDateEdit, QComboBox, QPushButton,
    QFileDialog, QMessageBox, QLabel, QWidget,
)
from PySide6.QtCore import QDate

from app.database.models import Project


class ProjectDialog(QDialog):
    """新建 / 编辑项目对话框"""

    STATUSES = ["待开始", "进行中", "已完成", "已交付"]

    def __init__(self, parent=None, project: Project = None, defaults: dict = None):
        super().__init__(parent)
        self._project = project
        self._is_edit = project is not None

        self.setWindowTitle("编辑项目" if self._is_edit else "新增项目")
        self.resize(520, 480)
        self.setMinimumWidth(480)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.no_edit = QLineEdit()
        self.no_edit.setPlaceholderText("自动生成或手动输入")
        form.addRow("项目编号:", self.no_edit)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("必填")
        form.addRow("项目名称:", self.name_edit)

        self.status_combo = QComboBox()
        self.status_combo.addItems(self.STATUSES)
        form.addRow("状态:", self.status_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        form.addRow("开始时间:", self.start_date)

        self.delivery_date = QDateEdit()
        self.delivery_date.setCalendarPopup(True)
        self.delivery_date.setDate(QDate.currentDate().addMonths(1))
        form.addRow("交付时间:", self.delivery_date)

        # 本地路径
        local_row = QWidget()
        local_layout = QHBoxLayout(local_row)
        local_layout.setContentsMargins(0, 0, 0, 0)
        self.local_edit = QLineEdit()
        self.local_edit.setPlaceholderText("本地项目目录路径（可选）")
        btn_local_browse = QPushButton("浏览...")
        btn_local_browse.clicked.connect(self._browse_local)
        local_layout.addWidget(self.local_edit, 1)
        local_layout.addWidget(btn_local_browse)
        form.addRow("本地路径:", local_row)

        # NAS路径
        nas_row = QWidget()
        nas_layout = QHBoxLayout(nas_row)
        nas_layout.setContentsMargins(0, 0, 0, 0)
        self.nas_edit = QLineEdit()
        self.nas_edit.setPlaceholderText("NAS映射路径（可选）")
        btn_nas_browse = QPushButton("浏览...")
        btn_nas_browse.clicked.connect(self._browse_nas)
        nas_layout.addWidget(self.nas_edit, 1)
        nas_layout.addWidget(btn_nas_browse)
        form.addRow("NAS路径:", nas_row)

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("备注信息（可选）")
        form.addRow("备注:", self.notes_edit)

        layout.addLayout(form)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_save = QPushButton("保存")
        self.btn_save.setDefault(True)
        self.btn_cancel = QPushButton("取消")
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

        self.btn_save.clicked.connect(self._save)
        self.btn_cancel.clicked.connect(self.reject)

        if self._is_edit:
            self._load_project()
        elif defaults:
            self._load_defaults(defaults)

    def _load_defaults(self, defaults: dict):
        self.no_edit.setText(defaults.get("project_no", ""))
        self.name_edit.setText(defaults.get("name", ""))
        if defaults.get("nas_path"):
            self.nas_edit.setText(defaults["nas_path"])
        if defaults.get("local_path"):
            self.local_edit.setText(defaults["local_path"])

    def _browse_local(self):
        path = QFileDialog.getExistingDirectory(self, "选择本地项目目录")
        if path:
            self.local_edit.setText(path)

    def _browse_nas(self):
        path = QFileDialog.getExistingDirectory(self, "选择NAS项目目录")
        if path:
            self.nas_edit.setText(path)

    def _load_project(self):
        p = self._project
        self.no_edit.setText(p.project_no or "")
        self.name_edit.setText(p.name or "")
        idx = self.status_combo.findText(p.status or "待开始")
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)
        if p.start_date:
            self.start_date.setDate(QDate.fromString(p.start_date, "yyyy-MM-dd"))
        if p.delivery_date:
            self.delivery_date.setDate(QDate.fromString(p.delivery_date, "yyyy-MM-dd"))
        self.local_edit.setText(p.local_path or "")
        self.nas_edit.setText(p.nas_path or "")
        self.notes_edit.setText(p.notes or "")

    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "项目名称不能为空")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "project_no": self.no_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "status": self.status_combo.currentText(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd"),
            "delivery_date": self.delivery_date.date().toString("yyyy-MM-dd"),
            "local_path": self.local_edit.text().strip(),
            "nas_path": self.nas_edit.text().strip(),
            "notes": self.notes_edit.text().strip(),
        }
