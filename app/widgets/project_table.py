from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenu, QAbstractItemView, QApplication, QToolTip,
)
from PySide6.QtCore import Qt, Signal, QPoint, QEvent
from PySide6.QtGui import QAction, QFont, QColor, QCursor, QKeyEvent

from app.database.models import Project


class ProjectTable(QWidget):
    """项目列表表格"""

    open_local = Signal(int)
    open_nas = Signal(int)
    edit_project = Signal(int)
    delete_project = Signal(int)
    manage_episodes = Signal(int, str)
    status_changed = Signal(int, str)          # project_id, new_status
    date_changed = Signal(int, str, str)       # project_id, field, new_date
    delete_pressed = Signal(int)               # project_id, Delete key
    refresh_needed = Signal()

    COLUMNS = ["编号", "名称", "状态", "开始时间", "交付时间", "分集分配", "本地路径", "NAS路径", "备注"]

    COL_NO = 0
    COL_NAME = 1
    COL_STATUS = 2
    COL_START = 3
    COL_DELIVERY = 4
    COL_EPISODES = 5
    COL_LOCAL = 6
    COL_NAS = 7
    COL_NOTES = 8

    STATUSES = ["待开始", "进行中", "已完成", "已交付"]

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)
        self.table.doubleClicked.connect(self._on_double_click)
        self.table.cellClicked.connect(self._on_cell_clicked)
        self.table.setMouseTracking(True)
        self.table.setSortingEnabled(True)
        self.table.installEventFilter(self)

        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.setSortIndicatorShown(True)
        header.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_EPISODES, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_LOCAL, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_NAS, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_NOTES, QHeaderView.Stretch)

        layout.addWidget(self.table)

    # ─── 数据加载 ─────────────────────────────────────

    def load_projects(self, projects: list[Project], episode_summaries: dict[int, str]):
        self.table.setRowCount(0)
        for proj in projects:
            row = self.table.rowCount()
            self.table.insertRow(row)

            no_item = QTableWidgetItem(proj.project_no or "")
            no_item.setToolTip("点击复制编号")
            self.table.setItem(row, self.COL_NO, no_item)

            name_item = QTableWidgetItem(proj.name)
            name_item.setToolTip("点击复制名称")
            self.table.setItem(row, self.COL_NAME, name_item)

            status_item = QTableWidgetItem(proj.status or "待开始")
            self._color_status(status_item, proj.status)
            status_item.setToolTip("点击切换状态")
            self.table.setItem(row, self.COL_STATUS, status_item)

            start_item = QTableWidgetItem(proj.start_date or "")
            start_item.setToolTip("点击修改开始时间")
            self.table.setItem(row, self.COL_START, start_item)

            delivery_item = QTableWidgetItem(proj.delivery_date or "")
            delivery_item.setToolTip("点击修改交付时间")
            self.table.setItem(row, self.COL_DELIVERY, delivery_item)

            self.table.setItem(row, self.COL_EPISODES,
                               QTableWidgetItem(episode_summaries.get(proj.id, "")))

            local_item = QTableWidgetItem(proj.local_path or "")
            if proj.local_path:
                local_item.setForeground(QColor("#1a73e8"))
                f = QFont()
                f.setUnderline(True)
                local_item.setFont(f)
                local_item.setToolTip("点击打开本地目录")
            self.table.setItem(row, self.COL_LOCAL, local_item)

            nas_item = QTableWidgetItem(proj.nas_path or "")
            if proj.nas_path:
                nas_item.setForeground(QColor("#1a73e8"))
                f = QFont()
                f.setUnderline(True)
                nas_item.setFont(f)
                nas_item.setToolTip("点击打开NAS目录")
            self.table.setItem(row, self.COL_NAS, nas_item)

            self.table.setItem(row, self.COL_NOTES, QTableWidgetItem(proj.notes or ""))

            item = self.table.item(row, self.COL_NO)
            if item:
                item.setData(Qt.UserRole, proj.id)

    # ─── 样式 ─────────────────────────────────────────

    def _color_status(self, item: QTableWidgetItem, status: str):
        colors = {
            "待开始": Qt.gray,
            "进行中": Qt.blue,
            "已完成": Qt.darkGreen,
            "已交付": Qt.darkCyan,
        }
        c = colors.get(status)
        if c:
            item.setForeground(c)

    # ─── 选中项 ───────────────────────────────────────

    def _selected_id(self) -> int | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, self.COL_NO)
        return item.data(Qt.UserRole) if item else None

    def _selected_name(self) -> str:
        row = self.table.currentRow()
        if row < 0:
            return ""
        item = self.table.item(row, self.COL_NAME)
        return item.text() if item else ""

    # ─── 右键菜单 ─────────────────────────────────────

    def _context_menu(self, pos):
        proj_id = self._selected_id()
        if proj_id is None:
            return
        row = self.table.currentRow()
        local = self.table.item(row, self.COL_LOCAL).text() if self.table.item(row, self.COL_LOCAL) else ""
        nas = self.table.item(row, self.COL_NAS).text() if self.table.item(row, self.COL_NAS) else ""

        menu = QMenu(self)

        if local:
            menu.addAction("📁 打开本地目录", lambda: self.open_local.emit(proj_id))
        if nas:
            menu.addAction("🌐 打开NAS目录", lambda: self.open_nas.emit(proj_id))
        if local or nas:
            menu.addSeparator()

        menu.addAction("📋 管理分集", lambda: self.manage_episodes.emit(proj_id, self._selected_name()))
        menu.addSeparator()
        menu.addAction("✏️ 编辑项目", lambda: self.edit_project.emit(proj_id))
        menu.addAction("🗑️ 删除项目", lambda: self.delete_project.emit(proj_id))

        menu.exec(QCursor.pos())

    # ─── 单元格点击 ───────────────────────────────────

    def _on_cell_clicked(self, row, col):
        proj_id = self._selected_id()
        if proj_id is None:
            return

        # 编号 / 名称 → 复制
        if col in (self.COL_NO, self.COL_NAME):
            item = self.table.item(row, col)
            if item and item.text():
                QApplication.clipboard().setText(item.text())
                QToolTip.showText(
                    QCursor.pos(),
                    f"已复制: {item.text()}",
                    self.table,
                )
                return

        # 路径 → 打开目录
        if col == self.COL_LOCAL:
            item = self.table.item(row, col)
            if item and item.text():
                self.open_local.emit(proj_id)
            return
        if col == self.COL_NAS:
            item = self.table.item(row, col)
            if item and item.text():
                self.open_nas.emit(proj_id)
            return

        # 状态 → 弹出菜单选择
        if col == self.COL_STATUS:
            self._popup_status_menu(row, proj_id)
            return

        # 日期 → 弹出修改对话框
        if col in (self.COL_START, self.COL_DELIVERY):
            self._popup_date_editor(row, col, proj_id)
            return

    def _popup_status_menu(self, row, proj_id):
        current = self.table.item(row, self.COL_STATUS).text() if self.table.item(row, self.COL_STATUS) else ""
        menu = QMenu(self)
        for s in self.STATUSES:
            action = menu.addAction(s)
            action.setCheckable(True)
            if s == current:
                action.setChecked(True)
        chosen = menu.exec(QCursor.pos())
        if chosen and chosen.text() != current:
            self.status_changed.emit(proj_id, chosen.text())

    def _popup_date_editor(self, row, col, proj_id):
        from PySide6.QtWidgets import QDialog as QD, QVBoxLayout as QVL, QDateEdit, QDialogButtonBox
        from PySide6.QtCore import QDate

        dlg = QD(self)
        dlg.setWindowTitle("修改开始时间" if col == self.COL_START else "修改交付时间")
        layout = QVL(dlg)
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        current_text = self.table.item(row, col).text() if self.table.item(row, col) else ""
        if current_text:
            d = QDate.fromString(current_text, "yyyy-MM-dd")
            if d.isValid():
                date_edit.setDate(d)
        else:
            date_edit.setDate(QDate.currentDate())
        layout.addWidget(date_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)

        if dlg.exec():
            new_date = date_edit.date().toString("yyyy-MM-dd")
            field = "start_date" if col == self.COL_START else "delivery_date"
            self.date_changed.emit(proj_id, field, new_date)

    # ─── 双击 ─────────────────────────────────────────

    def _on_double_click(self, index):
        proj_id = self._selected_id()
        if proj_id is not None:
            self.manage_episodes.emit(proj_id, self._selected_name())

    # ─── 键盘事件 ─────────────────────────────────────

    def eventFilter(self, obj, event):
        if obj == self.table and event.type() == QEvent.KeyPress:
            key_event = event
            if key_event.key() == Qt.Key_Delete:
                proj_id = self._selected_id()
                if proj_id is not None:
                    self.delete_pressed.emit(proj_id)
                    return True
        return super().eventFilter(obj, event)
