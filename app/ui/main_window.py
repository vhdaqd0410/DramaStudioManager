from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QMessageBox, QStatusBar, QLabel, QApplication,
)
from PySide6.QtCore import Qt

from app.services.project_service import ProjectService
from app.services.episode_service import EpisodeService
from app.database.models import Project
from app.utils.file_utils import open_in_explorer
from app.widgets.search_bar import SearchBar
from app.widgets.project_table import ProjectTable
from app.widgets.month_sidebar import MonthSidebar
from app.ui.project_dialog import ProjectDialog
from app.ui.episode_dialog import EpisodeDialog


# ── 全局样式表 ──────────────────────────────────────

STYLESHEET = """
/* 全局 */
QMainWindow {
    background-color: #f0f2f5;
}
QWidget#centralWidget {
    background-color: #f0f2f5;
}

/* 搜索栏 */
QWidget#searchBar {
    background: #ffffff;
    border-radius: 8px;
    padding: 10px 14px;
}
QLineEdit#searchInput {
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 13px;
    background: #ffffff;
}
QLineEdit#searchInput:focus {
    border-color: #4f8ef7;
}
QComboBox#statusFilter {
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
    background: #ffffff;
}
QPushButton#btnSearch {
    background: #4f8ef7;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
}
QPushButton#btnSearch:hover {
    background: #3b7de6;
}
QPushButton#btnReset {
    background: #ffffff;
    color: #555;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    font-size: 13px;
}
QPushButton#btnReset:hover {
    background: #f5f5f5;
}

/* 侧边栏 */
QWidget#sidebarTitle {
    font-size: 14px;
    font-weight: bold;
    color: #333;
    padding: 14px 0;
    background: #ffffff;
    border-bottom: 1px solid #e8eaed;
}
QListWidget#monthList {
    background: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    outline: none;
    padding: 4px;
}
QListWidget#monthList::item {
    padding: 10px 12px;
    border-radius: 6px;
    margin: 2px 4px;
    color: #444;
}
QListWidget#monthList::item:selected {
    background: #e8f0fe;
    color: #1a73e8;
    font-weight: bold;
}
QListWidget#monthList::item:hover:!selected {
    background: #f5f7fa;
}

/* 表格 */
QTableWidget {
    background: #ffffff;
    border: none;
    border-radius: 8px;
    gridline-color: #f0f0f0;
    font-size: 13px;
}
QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #f0f2f5;
}
QTableWidget::item:selected {
    background: #e8f0fe;
    color: #333;
}
QHeaderView::section {
    background: #f8f9fb;
    color: #555;
    font-weight: bold;
    font-size: 12px;
    padding: 8px 10px;
    border: none;
    border-bottom: 2px solid #e8eaed;
}

/* 底部操作栏 */
QWidget#bottomBar {
    background: #ffffff;
    border-radius: 8px;
    padding: 8px 14px;
}
QPushButton#btnAdd {
    background: #4f8ef7;
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
    padding: 8px 18px;
}
QPushButton#btnAdd:hover {
    background: #3b7de6;
}
QPushButton#btnRefresh {
    background: #ffffff;
    color: #555;
    border: 1px solid #d0d5dd;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton#btnRefresh:hover {
    background: #f5f5f5;
}
QLabel#statsLabel {
    color: #888;
    font-size: 13px;
}

/* 状态栏 */
QStatusBar {
    background: #f8f9fb;
    color: #888;
    font-size: 12px;
    border-top: 1px solid #e8eaed;
}

/* 分割器 */
QSplitter::handle {
    background: transparent;
    width: 4px;
}

/* 对话框通用 */
QDialog {
    background: #ffffff;
}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drama Studio Manager — 短剧项目管理")
        self.resize(1280, 760)
        self.setMinimumSize(1000, 560)

        # ── 应用全局样式 ──
        self.setStyleSheet(STYLESHEET)

        # ── 中心区域：侧边栏 + 内容 ──
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # 左侧月份侧边栏
        self.month_sidebar = MonthSidebar()
        root_layout.addWidget(self.month_sidebar)

        # 右侧内容区
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        # 搜索栏
        self.search_bar = SearchBar()
        content_layout.addWidget(self.search_bar)

        # 项目表格
        self.project_table = ProjectTable()
        content_layout.addWidget(self.project_table, 1)

        # 底部操作栏
        bottom = QWidget()
        bottom.setObjectName("bottomBar")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_add = QPushButton("＋ 新增项目")
        self.btn_add.setObjectName("btnAdd")
        self.btn_edit_sel = QPushButton("✏️ 编辑")
        self.btn_edit_sel.setObjectName("btnRefresh")
        self.btn_edit_sel.setToolTip("编辑选中的项目")
        self.btn_del_sel = QPushButton("🗑 删除")
        self.btn_del_sel.setObjectName("btnRefresh")
        self.btn_del_sel.setToolTip("删除选中的项目")
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.setObjectName("btnRefresh")
        self.status_label = QLabel("")
        self.status_label.setObjectName("statsLabel")

        bottom_layout.addWidget(self.btn_add)
        bottom_layout.addWidget(self.btn_edit_sel)
        bottom_layout.addWidget(self.btn_del_sel)
        bottom_layout.addWidget(self.btn_refresh)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.status_label)
        content_layout.addWidget(bottom)

        root_layout.addWidget(content, 1)

        # 状态栏
        self._status = QStatusBar()
        self.setStatusBar(self._status)

        # ── 当前月份过滤 ──
        self._current_month = ""

        # ── 信号绑定 ──
        self.month_sidebar.month_selected.connect(self._on_month_selected)
        self.search_bar.search_requested.connect(self._on_search)
        self.btn_add.clicked.connect(self._add_project)
        self.btn_edit_sel.clicked.connect(self._edit_selected)
        self.btn_del_sel.clicked.connect(self._delete_selected)
        self.btn_refresh.clicked.connect(self._refresh)
        self.project_table.edit_project.connect(self._edit_project)
        self.project_table.delete_project.connect(self._delete_project)
        self.project_table.open_local.connect(self._open_local)
        self.project_table.open_nas.connect(self._open_nas)
        self.project_table.manage_episodes.connect(self._manage_episodes)
        self.project_table.status_changed.connect(self._on_status_changed)
        self.project_table.date_changed.connect(self._on_date_changed)
        self.project_table.delete_pressed.connect(self._delete_project)

        self._refresh()

    # ── 分集摘要 ──

    def _build_episode_summaries(self, projects: list[Project]) -> dict[int, str]:
        summaries = {}
        for proj in projects:
            eps = EpisodeService.get_by_project(proj.id)
            if eps:
                merged = EpisodeService.merge_by_editor(eps)
                summaries[proj.id] = ", ".join(
                    f"{m['editor_name']}:{m['ranges']}" for m in merged
                )
            else:
                summaries[proj.id] = ""
        return summaries

    # ── 刷新 ──

    def _refresh(self):
        keyword = self.search_bar.search_input.text().strip()
        all_projects = ProjectService.get_all(keyword=keyword)

        # 月份过滤
        if self._current_month:
            projects = [
                p for p in all_projects
                if p.start_date and p.start_date.startswith(self._current_month)
            ]
        else:
            projects = all_projects

        # 状态过滤
        status_filter = self.search_bar.get_status_filter()
        if status_filter != "全部状态":
            projects = [p for p in projects if p.status == status_filter]

        # 更新侧边栏（基于全量数据不含关键词过滤的统计）
        sidebar_base = ProjectService.get_all()
        self.month_sidebar.build_months(sidebar_base)
        self.month_sidebar.select_month(self._current_month)

        summaries = self._build_episode_summaries(projects)
        self.project_table.load_projects(projects, summaries)

        month_label = f"「{self._current_month}」" if self._current_month else ""
        self.status_label.setText(f"共 {len(projects)} 个项目 {month_label}")
        self._status.showMessage(f"共 {len(projects)} 个项目")

    # ── 月份选择 ──

    def _on_month_selected(self, month_key: str):
        self._current_month = month_key
        self._refresh()

    # ── 搜索 ──

    def _on_search(self, keyword: str):
        self._refresh()

    # ── 项目 CRUD ──

    def _add_project(self):
        # 第一步：选择NAS目录，自动识别编号和名称
        from PySide6.QtWidgets import QFileDialog
        from app.utils.file_utils import parse_project_name
        import os

        path = QFileDialog.getExistingDirectory(self, "选择项目NAS目录（取消则手动填写）")
        defaults = {}
        if path:
            folder_name = os.path.basename(path)
            parsed = parse_project_name(folder_name)
            if parsed:
                defaults = {
                    "project_no": parsed["project_no"],
                    "name": parsed["name"],
                    "nas_path": path,
                }

        dlg = ProjectDialog(self, defaults=defaults if defaults else None)
        if dlg.exec():
            ProjectService.create(dlg.get_data())
            self._refresh()
            self._status.showMessage("项目创建成功")

    def _edit_project(self, proj_id: int):
        project = ProjectService.get_by_id(proj_id)
        if not project:
            return
        dlg = ProjectDialog(self, project)
        if dlg.exec():
            ProjectService.update(proj_id, dlg.get_data())
            self._refresh()
            self._status.showMessage("项目已更新")

    def _delete_project(self, proj_id: int):
        project = ProjectService.get_by_id(proj_id)
        if not project:
            return
        reply = QMessageBox.warning(
            self, "确认删除",
            f"确定要删除项目「{project.name}」吗？\n该操作会同时删除所有分集分配记录，不可恢复。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            ProjectService.delete(proj_id)
            self._refresh()
            self._status.showMessage(f"已删除项目「{project.name}」")

    def _open_local(self, proj_id: int):
        project = ProjectService.get_by_id(proj_id)
        if not project or not project.local_path:
            QMessageBox.information(self, "提示", "该项目未设置本地路径")
            return
        if not open_in_explorer(project.local_path):
            QMessageBox.warning(self, "提示", f"路径不存在或无法打开：\n{project.local_path}")

    def _open_nas(self, proj_id: int):
        project = ProjectService.get_by_id(proj_id)
        if not project or not project.nas_path:
            QMessageBox.information(self, "提示", "该项目未设置NAS路径")
            return
        if not open_in_explorer(project.nas_path):
            QMessageBox.warning(self, "提示", f"路径不存在或无法打开：\n{project.nas_path}")

    def _manage_episodes(self, proj_id: int, proj_name: str):
        dlg = EpisodeDialog(self, project_id=proj_id, project_name=proj_name)
        dlg.exec()
        self._refresh()

    def _on_status_changed(self, proj_id: int, new_status: str):
        ProjectService.update(proj_id, {"status": new_status})
        self._refresh()
        self._status.showMessage(f"状态已更新为「{new_status}」")

    def _on_date_changed(self, proj_id: int, field: str, new_date: str):
        ProjectService.update(proj_id, {field: new_date})
        label = "开始时间" if field == "start_date" else "交付时间"
        self._refresh()
        self._status.showMessage(f"{label}已更新为 {new_date}")

    # ── 底部按钮：编辑 / 删除选中项目 ──

    def _edit_selected(self):
        proj_id = self.project_table._selected_id()
        if proj_id is None:
            QMessageBox.information(self, "提示", "请先在表格中选择一个项目")
            return
        self._edit_project(proj_id)

    def _delete_selected(self):
        proj_id = self.project_table._selected_id()
        if proj_id is None:
            QMessageBox.information(self, "提示", "请先在表格中选择一个项目")
            return
        self._delete_project(proj_id)
