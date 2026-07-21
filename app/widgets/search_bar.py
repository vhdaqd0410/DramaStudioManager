from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QComboBox, QPushButton
from PySide6.QtCore import Signal


class SearchBar(QWidget):
    search_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("searchBar")

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("🔍  搜索项目名称 / 编号...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(32)

        self.status_filter = QComboBox()
        self.status_filter.setObjectName("statusFilter")
        self.status_filter.addItems(["全部状态", "待开始", "进行中", "已完成", "已交付"])
        self.status_filter.setMinimumHeight(32)
        self.status_filter.setFixedWidth(100)

        self.btn_search = QPushButton("搜索")
        self.btn_search.setObjectName("btnSearch")
        self.btn_search.setMinimumHeight(32)
        self.btn_search.setFixedWidth(60)

        self.btn_reset = QPushButton("重置")
        self.btn_reset.setObjectName("btnReset")
        self.btn_reset.setMinimumHeight(32)
        self.btn_reset.setFixedWidth(60)

        layout.addWidget(self.search_input, 1)
        layout.addWidget(self.status_filter)
        layout.addWidget(self.btn_search)
        layout.addWidget(self.btn_reset)

        self.setLayout(layout)

        self.search_input.returnPressed.connect(self._emit_search)
        self.btn_search.clicked.connect(self._emit_search)
        self.btn_reset.clicked.connect(self._reset)

    def _emit_search(self):
        self.search_requested.emit(self.search_input.text().strip())

    def _reset(self):
        self.search_input.clear()
        self.status_filter.setCurrentIndex(0)
        self.search_requested.emit("")

    def get_status_filter(self) -> str:
        return self.status_filter.currentText()
