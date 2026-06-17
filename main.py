import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from ui.styles import DARK_STYLE
from ui.dashboard import DashboardTab
from ui.food_log import FoodLogTab
from ui.recommendation import RecommendTab
from ui.challenge import ChallengeTab
from ui.history import HistoryTab
from ui.shopping import ShoppingTab
from ui.report import ReportTab
from data.database import init_db


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🥩 소고기 식단 트래커")
        self.setMinimumSize(960, 720)

        tabs = QTabWidget()
        tabs.setDocumentMode(True)

        self.dashboard   = DashboardTab()
        self.food_log    = FoodLogTab(on_update=self._on_food_update)
        self.recommend   = RecommendTab()
        self.challenge   = ChallengeTab()
        self.history     = HistoryTab()
        self.shopping    = ShoppingTab()
        self.report      = ReportTab()

        tabs.addTab(self.dashboard, "  대시보드  ")
        tabs.addTab(self.food_log,  "  식단 기록  ")
        tabs.addTab(self.recommend, "  오늘 뭐 먹을까  ")
        tabs.addTab(self.challenge, "  50일 챌린지  ")
        tabs.addTab(self.history,   "  히스토리  ")
        tabs.addTab(self.shopping,  "  장보기  ")
        tabs.addTab(self.report,    "  주간 리포트  ")

        tabs.currentChanged.connect(self._on_tab_change)
        self.setCentralWidget(tabs)
        self._tabs = tabs

    def _on_food_update(self):
        self.dashboard.refresh()

    def _on_tab_change(self, index):
        tab = self._tabs.widget(index)
        if hasattr(tab, "refresh"):
            tab.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    init_db()
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
