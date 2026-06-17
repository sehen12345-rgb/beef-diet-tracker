"""
공유 탭 — 인스타그램용 카드 이미지 생성 및 저장
"""
import os
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont

from data.database import get_daily_totals, get_weight_history, get_setting, get_active_challenge, get_challenge_days
from data.license import is_premium, get_license_status
from ui.license_dialog import LicenseDialog


class _CardWorker(QThread):
    done = pyqtSignal(object)  # PIL Image

    def __init__(self, mode, data, premium):
        super().__init__()
        self.mode = mode
        self.data = data
        self.premium = premium

    def run(self):
        from ui.share_card import create_feed_card, create_story_card
        d = self.data
        fn = create_feed_card if self.mode == "feed" else create_story_card
        img = fn(
            protein=d["protein"], protein_goal=d["protein_goal"],
            calories=d["calories"], calorie_goal=d["calorie_goal"],
            fat=d["fat"], beef_g=d["beef_g"],
            weight_kg=d["weight_kg"],
            day_str=d["day_str"],
            is_premium=self.premium,
            challenge_day=d["challenge_day"],
        )
        self.done.emit(img)


class ShareTab(QWidget):
    def __init__(self):
        super().__init__()
        self._img = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        # 타이틀 행
        title_row = QHBoxLayout()
        title = QLabel("📲  인스타그램 공유 카드")
        title.setObjectName("title")
        title_row.addWidget(title)
        title_row.addStretch()

        status = get_license_status()
        if status["plan"] != "premium":
            badge = QLabel(f"⏳ 무료 체험 {status['days_left']}일 남음")
            badge.setStyleSheet(
                "background:#C9A84C; color:#1E1E1E; padding:4px 10px;"
                "border-radius:6px; font-weight:bold; font-size:12px;"
            )
            title_row.addWidget(badge)
            upgrade_btn = QPushButton("🔓 프리미엄 업그레이드")
            upgrade_btn.setObjectName("secondary")
            upgrade_btn.clicked.connect(self._open_license)
            title_row.addWidget(upgrade_btn)

        layout.addLayout(title_row)

        # 설명
        desc = QLabel(
            "오늘의 식단 데이터로 인스타그램 공유용 이미지를 만들어요.\n"
            "피드(1:1)  /  스토리·릴스(9:16) 두 가지 사이즈를 지원합니다."
        )
        desc.setStyleSheet("color:#AAAAAA; font-size:12px;")
        layout.addWidget(desc)

        # 컨트롤 행
        ctrl_row = QHBoxLayout()

        type_label = QLabel("카드 종류:")
        type_label.setStyleSheet("color:#F5F5F5;")
        ctrl_row.addWidget(type_label)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["📷  피드 (1:1  1080×1080)", "📱  스토리 / 릴스 (9:16  1080×1920)"])
        self.type_combo.setFixedWidth(300)
        ctrl_row.addWidget(self.type_combo)

        ctrl_row.addStretch()

        gen_btn = QPushButton("✨  카드 생성")
        gen_btn.clicked.connect(self._generate)
        ctrl_row.addWidget(gen_btn)

        save_btn = QPushButton("💾  이미지 저장")
        save_btn.setObjectName("secondary")
        save_btn.clicked.connect(self._save)
        ctrl_row.addWidget(save_btn)

        layout.addLayout(ctrl_row)

        # 프리뷰 영역
        preview_frame = QFrame()
        preview_frame.setObjectName("card")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel("카드 생성 버튼을 눌러주세요")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color:#666666; font-size:13px;")
        self.preview_label.setMinimumHeight(400)
        preview_layout.addWidget(self.preview_label)

        layout.addWidget(preview_frame, 1)

        # 무료버전 안내
        if not is_premium():
            watermark_notice = QLabel(
                "ℹ️  무료 체험 중에는 공유 카드에 워터마크가 포함됩니다. "
                "프리미엄으로 업그레이드하면 워터마크 없이 깔끔한 카드를 만들 수 있어요."
            )
            watermark_notice.setStyleSheet(
                "background:#2A2A2A; color:#C9A84C; padding:10px 14px;"
                "border-radius:8px; font-size:12px;"
            )
            watermark_notice.setWordWrap(True)
            layout.addWidget(watermark_notice)

    def _get_data(self) -> dict:
        today = date.today().isoformat()
        totals = get_daily_totals(today)

        # 목표 설정값
        protein_goal = float(get_setting("protein_goal", "150"))
        calorie_goal = float(get_setting("calorie_goal", "2000"))

        # 오늘 체중
        history = get_weight_history(1)
        weight_kg = history[0][1] if history else None

        # 챌린지 D+
        challenge_day = None
        ch = get_active_challenge()
        if ch:
            from datetime import date as d_
            start = d_.fromisoformat(ch[1])
            diff = (d_.today() - start).days + 1
            challenge_day = diff if 1 <= diff <= 50 else None

        return {
            "protein":      totals["단백질"],
            "protein_goal": protein_goal,
            "calories":     totals["칼로리"],
            "calorie_goal": calorie_goal,
            "fat":          totals["지방"],
            "beef_g":       totals["소고기_g"],
            "weight_kg":    weight_kg,
            "day_str":      date.today().strftime("%Y년 %m월 %d일"),
            "challenge_day": challenge_day,
        }

    def _generate(self):
        self.preview_label.setText("⏳  카드 생성 중...")
        mode = "feed" if self.type_combo.currentIndex() == 0 else "story"
        data = self._get_data()
        premium = is_premium()

        self._worker = _CardWorker(mode, data, premium)
        self._worker.done.connect(self._on_card_ready)
        self._worker.start()

    def _on_card_ready(self, img):
        self._img = img
        # PIL → QPixmap 변환
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        qimg = QImage()
        qimg.loadFromData(buf.read())
        pix = QPixmap.fromImage(qimg)

        # 프리뷰 크기에 맞게 축소
        pix = pix.scaled(
            self.preview_label.width() - 20,
            self.preview_label.height() - 20,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.preview_label.setPixmap(pix)

    def _save(self):
        if self._img is None:
            QMessageBox.information(self, "알림", "먼저 카드를 생성해주세요.")
            return

        default_name = f"beeftracker_{date.today().isoformat()}.png"
        path, _ = QFileDialog.getSaveFileName(
            self, "이미지 저장", default_name, "PNG 이미지 (*.png)"
        )
        if path:
            self._img.save(path, "PNG")
            QMessageBox.information(self, "저장 완료", f"저장되었어요!\n{path}")

    def _open_license(self):
        dlg = LicenseDialog(self)
        dlg.exec_()

    def refresh(self):
        pass
