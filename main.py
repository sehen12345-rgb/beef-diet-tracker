import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from ui.styles import DARK_STYLE
from ui.dashboard import DashboardTab
from ui.food_log import FoodLogTab
from ui.report import ReportTab
from data.database import init_db


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🥩 소고기 식단 트래커")
        self.setMinimumSize(900, 680)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        self.dashboard = DashboardTab()
        self.food_log  = FoodLogTab(on_update=self.dashboard.refresh)
        self.report    = ReportTab()

        tabs.addTab(self.dashboard, "  대시보드  ")
        tabs.addTab(self.food_log,  "  식단 기록  ")
        tabs.addTab(self.report,    "  주간 리포트  ")

        tabs.currentChanged.connect(self._on_tab_change)

        self.setCentralWidget(tabs)

    def _on_tab_change(self, index):
        if index == 0:
            self.dashboard.refresh()
        elif index == 2:
            self.report.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    init_db()
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
