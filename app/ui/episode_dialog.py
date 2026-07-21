from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QMessageBox, QLabel,
)
from PySide6.QtCore import Qt

from app.services.episode_service import EpisodeService


class EpisodeDialog(QDialog):
    """管理项目分集分配（按剪辑师合并显示）"""

    def __init__(self, parent=None, project_id: int = None, project_name: str = ""):
        super().__init__(parent)
        self._project_id = project_id
        self._project_name = project_name

        self.setWindowTitle(f"分集管理 — {project_name}")
        self.resize(600, 450)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        hint = QLabel("管理剪辑师分配，格式如：张三负责第1-3集、李四负责第4-8集")
        hint.setStyleSheet("color: gray;")
        layout.addWidget(hint)

        # 表格 — 3列：剪辑师 / 剪辑任务 / 备注
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["剪辑师", "剪辑任务", "备注"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table, 1)

        # 底部统计
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #666; padding: 4px;")
        layout.addWidget(self.stats_label)

        # 按钮行
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("添加分配")
        self.btn_edit = QPushButton("编辑")
        self.btn_delete = QPushButton("删除")
        self.btn_batch = QPushButton("批量导入")
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_edit)
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_batch)
        btn_row.addStretch()
        self.btn_close = QPushButton("关闭")
        btn_row.addWidget(self.btn_close)
        layout.addLayout(btn_row)

        self.btn_add.clicked.connect(self._add)
        self.btn_edit.clicked.connect(self._edit)
        self.btn_delete.clicked.connect(self._delete)
        self.btn_batch.clicked.connect(self._batch_import)
        self.btn_close.clicked.connect(self.accept)

        self._load()

    def _load(self):
        episodes = EpisodeService.get_by_project(self._project_id)
        merged = EpisodeService.merge_by_editor(episodes)

        self.table.setRowCount(0)
        for m in merged:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(m["editor_name"]))
            self.table.setItem(row, 1, QTableWidgetItem(m["ranges"]))
            self.table.setItem(row, 2, QTableWidgetItem(""))
            # 存 editor_name 用于后续操作
            item = self.table.item(row, 0)
            if item:
                item.setData(Qt.UserRole, m["editor_name"])

        # 统计
        total_editors = len(merged)
        total_eps = sum(m["total_eps"] for m in merged)
        if merged:
            all_starts = []
            all_ends = []
            for ep in episodes:
                all_starts.append(ep.start_ep)
                all_ends.append(ep.end_ep)
            self.stats_label.setText(
                f"共 {total_editors} 位剪辑师，覆盖 {min(all_starts)}-{max(all_ends)} 集，"
                f"合计 {total_eps} 集分配任务"
            )
        else:
            self.stats_label.setText("暂无分集分配")

    def _selected_editor(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _add(self):
        dlg = _AssignmentDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            data["project_id"] = self._project_id
            EpisodeService.create(data)
            self._load()

    def _edit(self):
        editor_name = self._selected_editor()
        if editor_name is None:
            QMessageBox.information(self, "提示", "请先选择一条记录")
            return
        eps = EpisodeService.get_by_project_and_editor(self._project_id, editor_name)
        if not eps:
            return
        dlg = _AssignmentDialog(self, editor_name=editor_name, episodes=eps)
        if dlg.exec():
            EpisodeService.delete_by_editor(self._project_id, editor_name)
            assignments = dlg.get_data()
            for a in assignments:
                a["project_id"] = self._project_id
            EpisodeService.batch_create(self._project_id, assignments)
            self._load()

    def _delete(self):
        editor_name = self._selected_editor()
        if editor_name is None:
            QMessageBox.information(self, "提示", "请先选择一条记录")
            return
        reply = QMessageBox.question(
            self, "确认", f"确定要删除「{editor_name}」的所有分集分配吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            EpisodeService.delete_by_editor(self._project_id, editor_name)
            self._load()

    def _batch_import(self):
        from PySide6.QtWidgets import QTextEdit, QDialog as QD, QVBoxLayout as QVL

        class BatchDialog(QD):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("批量导入分集分配")
                self.resize(450, 300)
                layout = QVL(self)
                hint = QLabel(
                    "每行一条，支持多段集数用逗号分隔\n"
                    "格式：剪辑师:起始-结束,起始-结束\n例如：\n"
                    "张大强:1-2\n任显翔:3-8,38-45\n"
                    "陈春阳:9-13,36-37\n金文龙:14-28\n李钊琦:29-35"
                )
                layout.addWidget(hint)
                self.text_edit = QTextEdit()
                self.text_edit.setPlaceholderText("在此粘贴分配信息...")
                layout.addWidget(self.text_edit, 1)
                btn_row = QHBoxLayout()
                btn_row.addStretch()
                btn_ok = QPushButton("导入")
                btn_cancel = QPushButton("取消")
                btn_row.addWidget(btn_ok)
                btn_row.addWidget(btn_cancel)
                layout.addLayout(btn_row)
                btn_ok.clicked.connect(self.accept)
                btn_cancel.clicked.connect(self.reject)

            def get_data(self) -> list[dict]:
                result = []
                text = self.text_edit.toPlainText().strip()
                if not text:
                    return result
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    for sep in [":", "："]:
                        if sep in line:
                            name, ranges_str = line.split(sep, 1)
                            break
                    else:
                        continue
                    name = name.strip()
                    ranges_str = ranges_str.strip()
                    for part in ranges_str.split(","):
                        part = part.strip()
                        if not part:
                            continue
                        start, end = self._parse_range(part)
                        if start is not None:
                            result.append({"editor_name": name, "start_ep": start, "end_ep": end})
                return result

            @staticmethod
            def _parse_range(rng: str) -> tuple:
                rng = rng.strip()
                if rng.isdigit():
                    v = int(rng)
                    return v, v
                for dash in ["-", "—", "~"]:
                    if dash in rng:
                        parts = rng.split(dash, 1)
                        try:
                            return int(parts[0].strip()), int(parts[1].strip())
                        except ValueError:
                            break
                return None, None

        reply = QMessageBox.question(
            self, "批量导入",
            "批量导入会清空现有分集分配，确定继续吗？",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        dlg = BatchDialog(self)
        if dlg.exec():
            assignments = dlg.get_data()
            if assignments:
                EpisodeService.delete_by_project(self._project_id)
                EpisodeService.batch_create(self._project_id, assignments)
                self._load()
                QMessageBox.information(self, "提示", f"成功导入 {len(assignments)} 条分配记录")
            else:
                QMessageBox.warning(self, "提示", "未能解析到有效的分配数据")


class _AssignmentDialog(QDialog):
    """单条添加 / 编辑分配（输入剪辑师名字 + 集数范围文本）"""

    def __init__(self, parent=None, editor_name: str = "", episodes: list = None):
        super().__init__(parent)
        self.setWindowTitle("编辑分配" if episodes else "添加分配")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("剪辑师:"))
        from PySide6.QtWidgets import QLineEdit
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("剪辑师名字")
        self.name_edit.setText(editor_name)
        name_layout.addWidget(self.name_edit, 1)
        layout.addLayout(name_layout)

        layout.addWidget(QLabel("集数范围（逗号分隔多段）:"))
        from PySide6.QtWidgets import QTextEdit
        self.ranges_edit = QTextEdit()
        self.ranges_edit.setPlaceholderText("1-3, 38-45")
        self.ranges_edit.setMaximumHeight(80)
        if episodes:
            parts = []
            for ep in sorted(episodes, key=lambda e: e.start_ep):
                parts.append(str(ep.start_ep) if ep.start_ep == ep.end_ep else f"{ep.start_ep}-{ep.end_ep}")
            self.ranges_edit.setPlainText(", ".join(parts))
        layout.addWidget(self.ranges_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_ok = QPushButton("保存")
        btn_cancel = QPushButton("取消")
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        layout.addLayout(btn_row)

        btn_ok.clicked.connect(self._save)
        btn_cancel.clicked.connect(self.reject)

    def _save(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入剪辑师名字")
            return
        if not self.ranges_edit.toPlainText().strip():
            QMessageBox.warning(self, "提示", "请输入集数范围")
            return
        self.accept()

    def get_data(self) -> list[dict]:
        name = self.name_edit.text().strip()
        result = []
        text = self.ranges_edit.toPlainText().strip()
        for part in text.split(","):
            part = part.strip()
            if not part:
                continue
            for dash in ["-", "—", "~"]:
                if dash in part:
                    p = part.split(dash, 1)
                    try:
                        s, e = int(p[0].strip()), int(p[1].strip())
                        result.append({"editor_name": name, "start_ep": s, "end_ep": e})
                    except ValueError:
                        pass
                    break
            else:
                if part.isdigit():
                    v = int(part)
                    result.append({"editor_name": name, "start_ep": v, "end_ep": v})
        return result
