import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from app.database.database import init_db
from app.ui.main_window import MainWindow


def main():
    try:
        init_db()

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except Exception:
        err = traceback.format_exc()
        print(err, file=sys.stderr)
        # 把错误写入文件方便查看
        with open("error.log", "w", encoding="utf-8") as f:
            f.write(err)
        # 尝试弹窗显示错误
        try:
            QMessageBox.critical(None, "启动失败", f"程序启动时出错：\n\n{err}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
