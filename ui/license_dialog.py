"""
라이선스 / 업그레이드 다이얼로그
- 체험판 상태 표시
- 라이선스 키 입력
- 구매 안내 (litt.ly 링크)
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDesktopServices
from PyQt5.QtCore import QUrl
from data.license import get_license_status, validate_key, save_license_key, is_premium

# 구매 페이지 URL (litt.ly 등으로 변경)
PURCHASE_URL = "https://litt.ly/beeftracker"


class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("라이선스 관리")
        self.setFixedSize(480, 380)
        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; color: #F5F5F5; }
            QLabel { color: #F5F5F5; }
            QLineEdit {
                background-color: #2A2A2A;
                color: #F5F5F5;
                border: 1px solid #3A3A3A;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 2px;
            }
            QPushButton {
                background-color: #8B1A1A;
                color: #FAF3E0;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A52020; }
            QPushButton#buy_btn {
                background-color: #C9A84C;
                color: #1E1E1E;
            }
            QPushButton#buy_btn:hover { background-color: #D4B460; }
            QFrame#card {
                background-color: #2A2A2A;
                border-radius: 10px;
            }
        """)
        self._build_ui()
        self._refresh_status()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # 타이틀
        title = QLabel("🥩 소고기 식단 트래커 라이선스")
        title.setFont(QFont("Malgun Gothic", 15, QFont.Bold))
        title.setStyleSheet("color: #C9A84C;")
        layout.addWidget(title)

        # 상태 카드
        status_card = QFrame()
        status_card.setObjectName("card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(16, 16, 16, 16)

        self.status_icon = QLabel("⏳")
        self.status_icon.setFont(QFont("Malgun Gothic", 32))
        self.status_icon.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_icon)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Malgun Gothic", 13, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)

        self.days_label = QLabel("")
        self.days_label.setAlignment(Qt.AlignCenter)
        self.days_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        status_layout.addWidget(self.days_label)

        layout.addWidget(status_card)

        # 라이선스 키 입력
        key_label = QLabel("라이선스 키 입력")
        key_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        layout.addWidget(key_label)

        key_row = QHBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("BEEF-XXXX-XXXX-XXXX")
        self.key_input.setMaxLength(19)
        key_row.addWidget(self.key_input)

        self.activate_btn = QPushButton("활성화")
        self.activate_btn.setFixedWidth(80)
        self.activate_btn.clicked.connect(self._activate)
        key_row.addWidget(self.activate_btn)
        layout.addLayout(key_row)

        # 구매 버튼
        buy_btn = QPushButton("🛒  프리미엄 구매하기")
        buy_btn.setObjectName("buy_btn")
        buy_btn.clicked.connect(self._open_purchase)
        layout.addWidget(buy_btn)

        # 안내 텍스트
        info = QLabel("구매 후 이메일로 발송되는 키를 입력하세요.\n문의: Instagram @beeftracker_kr")
        info.setStyleSheet("color: #666666; font-size: 11px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

    def _refresh_status(self):
        status = get_license_status()
        if status["plan"] == "premium":
            self.status_icon.setText("✅")
            self.status_label.setText("프리미엄 활성화됨")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: bold;")
            self.days_left_label_update("모든 기능 무제한 사용 중")
            self.activate_btn.setEnabled(False)
        elif status["plan"] == "free_trial":
            self.status_icon.setText("⏳")
            self.status_label.setText(f"무료 체험 중 — {status['days_left']}일 남음")
            self.status_label.setStyleSheet("color: #C9A84C; font-size: 13px; font-weight: bold;")
            self.days_left_label_update("체험판: 인스타 공유 시 워터마크 포함")
        else:
            self.status_icon.setText("🔒")
            self.status_label.setText("체험 기간 만료")
            self.status_label.setStyleSheet("color: #FF6B35; font-size: 13px; font-weight: bold;")
            self.days_left_label_update("프리미엄으로 업그레이드하여 계속 사용하세요")

    def days_left_label_update(self, text):
        self.days_label.setText(text)

    def _activate(self):
        key = self.key_input.text().strip().upper()
        if not key:
            QMessageBox.warning(self, "오류", "라이선스 키를 입력해주세요.")
            return
        if validate_key(key):
            save_license_key(key)
            QMessageBox.information(self, "성공", "🎉 프리미엄 활성화 완료!\n모든 기능을 사용하실 수 있습니다.")
            self._refresh_status()
        else:
            QMessageBox.warning(self, "오류", "유효하지 않은 라이선스 키입니다.\n구매 후 발급된 키를 확인해주세요.")

    def _open_purchase(self):
        QDesktopServices.openUrl(QUrl(PURCHASE_URL))
