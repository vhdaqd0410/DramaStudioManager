from collections import Counter

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel
from PySide6.QtCore import Signal, Qt


class MonthSidebar(QWidget):
    """左侧月份归类侧边栏"""

    month_selected = Signal(str)  # emit 月份字符串，如 "2026-07"，空串表示全部

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题
        title = QLabel("📅 月份归类")
        title.setObjectName("sidebarTitle")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 列表
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("monthList")
        self.list_widget.currentRowChanged.connect(self._on_selection_changed)
        layout.addWidget(self.list_widget, 1)

        self._months = []  # [(label, key, count)]

    def build_months(self, projects: list):
        """根据项目列表构建月份条目"""
        # 统计每月项目数
        counter: Counter = Counter()
        for p in projects:
            if p.start_date and len(p.start_date) >= 7:
                counter[p.start_date[:7]] += 1
            else:
                counter["未设置"] += 1

        # 排序：最近月份在前
        sorted_months = sorted(
            [m for m in counter if m != "未设置"],
            reverse=True,
        )
        if "未设置" in counter:
            sorted_months.append("未设置")

        self._months.clear()
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        # "全部项目"
        total = len(projects)
        all_item = QListWidgetItem(f"  全部项目  ({total})")
        all_item.setData(Qt.UserRole, "")
        all_item.setToolTip("显示所有项目")
        self.list_widget.addItem(all_item)
        self._months.append(("全部项目", "", total))

        for m in sorted_months:
            count = counter[m]
            if m == "未设置":
                label = f"  ⚠ 未设置月份  ({count})"
            else:
                year, month = m.split("-")
                label = f"  {year}年{int(month):02d}月  ({count})"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, m)
            item.setToolTip(f"{label.strip()} — {count} 个项目")
            self.list_widget.addItem(item)
            self._months.append((label.strip(), m, count))

        # 默认选中"全部"（信号阻断中）
        self.list_widget.setCurrentRow(0)
        self.list_widget.blockSignals(False)

    def _on_selection_changed(self, row):
        if 0 <= row < len(self._months):
            self.month_selected.emit(self._months[row][1])

    def select_month(self, month_key: str):
        """外部设置选中月份（不触发信号）"""
        for i, (_, key, _) in enumerate(self._months):
            if key == month_key:
                self.list_widget.blockSignals(True)
                self.list_widget.setCurrentRow(i)
                self.list_widget.blockSignals(False)
                return
