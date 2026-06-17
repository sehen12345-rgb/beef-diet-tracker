import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox
from PyQt5.QtCore import QTimer
from ui.styles import DARK_STYLE
from ui.dashboard import DashboardTab
from ui.food_log import FoodLogTab
from ui.recommendation import RecommendTab
from ui.challenge import ChallengeTab
from ui.history import HistoryTab
from ui.shopping import ShoppingTab
from ui.report import ReportTab
from ui.share_tab import ShareTab
from ui.license_dialog import LicenseDialog
from data.database import init_db
from data.license import get_license_status, get_install_date


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
        self.share       = ShareTab()

        tabs.addTab(self.dashboard, "  대시보드  ")
        tabs.addTab(self.food_log,  "  식단 기록  ")
        tabs.addTab(self.recommend, "  오늘 뭐 먹을까  ")
        tabs.addTab(self.challenge, "  50일 챌린지  ")
        tabs.addTab(self.history,   "  히스토리  ")
        tabs.addTab(self.shopping,  "  장보기  ")
        tabs.addTab(self.report,    "  주간 리포트  ")
        tabs.addTab(self.share,     "  📲 공유하기  ")

        tabs.currentChanged.connect(self._on_tab_change)
        self.setCentralWidget(tabs)
        self._tabs = tabs

        # 시작 후 2초 뒤 라이선스 상태 알림
        QTimer.singleShot(2000, self._check_license_notice)

    def _on_food_update(self):
        self.dashboard.refresh()

    def _on_tab_change(self, index):
        tab = self._tabs.widget(index)
        if hasattr(tab, "refresh"):
            tab.refresh()

    def _check_license_notice(self):
        status = get_license_status()
        if status["plan"] == "expired":
            msg = QMessageBox(self)
            msg.setWindowTitle("체험 기간 만료")
            msg.setText(
                "⏰ 14일 무료 체험이 종료되었습니다.\n\n"
                "프리미엄으로 업그레이드하면\n"
                "• 모든 기능 무제한 사용\n"
                "• 인스타 공유 카드 워터마크 없음\n"
                "• 향후 업데이트 무료 제공"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            upgrade_btn = msg.addButton("🛒 지금 업그레이드", QMessageBox.AcceptRole)
            msg.exec_()
            if msg.clickedButton() == upgrade_btn:
                dlg = LicenseDialog(self)
                dlg.exec_()

        elif status["plan"] == "free_trial" and status["days_left"] <= 3:
            msg = QMessageBox(self)
            msg.setWindowTitle("체험 기간 곧 종료")
            msg.setText(
                f"⚠️ 무료 체험 기간이 {status['days_left']}일 남았습니다.\n\n"
                "지금 업그레이드하면 계속 사용하실 수 있어요!"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            upgrade_btn = msg.addButton("🛒 업그레이드", QMessageBox.AcceptRole)
            msg.exec_()
            if msg.clickedButton() == upgrade_btn:
                dlg = LicenseDialog(self)
                dlg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    init_db()
    get_install_date()  # 최초 실행일 기록
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
