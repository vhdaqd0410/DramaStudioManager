from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QPushButton, QMessageBox,
)
from PySide6.QtCore import Qt

from app.database.models import Episode


class EpisodeEditDialog(QDialog):
    """单条分集分配编辑"""

    def __init__(self, parent=None, episode: Episode = None):
        super().__init__(parent)
        self._episode = episode
        self._is_edit = episode is not None

        self.setWindowTitle("编辑分配" if self._is_edit else "添加分配")
        self.resize(350, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.editor_edit = QLineEdit()
        self.editor_edit.setPlaceholderText("剪辑师名字")
        form.addRow("剪辑师:", self.editor_edit)

        range_row = QHBoxLayout()
        self.start_spin = QSpinBox()
        self.start_spin.setRange(1, 9999)
        self.start_spin.setSuffix(" 集")
        range_row.addWidget(self.start_spin)

        dash_label = QLineEdit("—")
        dash_label.setReadOnly(True)
        dash_label.setAlignment(Qt.AlignCenter)
        dash_label.setFixedWidth(40)
        dash_label.setStyleSheet("border: none; background: transparent;")
        range_row.addWidget(dash_label)

        self.end_spin = QSpinBox()
        self.end_spin.setRange(1, 9999)
        self.end_spin.setSuffix(" 集")
        range_row.addWidget(self.end_spin)
        range_row.addStretch()
        form.addRow("集数范围:", range_row)

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("备注（可选）")
        form.addRow("备注:", self.notes_edit)

        layout.addLayout(form)

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
            self._load()

    def _load(self):
        self.editor_edit.setText(self._episode.editor_name)
        self.start_spin.setValue(self._episode.start_ep)
        self.end_spin.setValue(self._episode.end_ep)
        self.notes_edit.setText(self._episode.notes or "")

    def _save(self):
        name = self.editor_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入剪辑师名字")
            return
        if self.start_spin.value() > self.end_spin.value():
            QMessageBox.warning(self, "提示", "起始集号不能大于结束集号")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "editor_name": self.editor_edit.text().strip(),
            "start_ep": self.start_spin.value(),
            "end_ep": self.end_spin.value(),
            "notes": self.notes_edit.text().strip(),
        }
