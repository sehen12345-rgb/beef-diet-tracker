from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QScrollArea)
from PyQt5.QtCore import Qt
from datetime import date
from data.database import get_daily_totals, get_setting
from data.beef_db import BEEF_PRODUCTS, get_nutrition


def recommend_meals(remaining_cal, remaining_protein):
    results = []
    for cut, form, cal100, pro100, fat100 in BEEF_PRODUCTS:
        for weight in [100, 150, 200]:
            n = get_nutrition(cut, form, weight)
            if n["칼로리"] > remaining_cal + 50:
                continue
            score = 0
            if remaining_protein > 0:
                score += min(n["단백질"] / remaining_protein, 1.0) * 70
            if remaining_cal > 0:
                score += (1 - abs(n["칼로리"] - remaining_cal * 0.6) / (remaining_cal * 0.6 + 1)) * 30
            results.append((score, cut, form, weight, n))
    results.sort(reverse=True)
    seen = set()
    unique = []
    for item in results:
        key = (item[1], item[2])
        if key not in seen:
            seen.add(key)
            unique.append(item)
        if len(unique) >= 4:
            break
    return unique


class RecommendTab(QWidget):
    def __init__(self):
        super().__init__()
        self.today = date.today().isoformat()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        container = QWidget()
        self.layout_ = QVBoxLayout(container)
        self.layout_.setSpacing(14)
        self.layout_.setContentsMargins(20, 20, 20, 20)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        scroll.setWidget(container)

        header = QLabel("🤖 오늘 뭐 먹을까?")
        header.setObjectName("title")
        self.layout_.addWidget(header)

        hint = QLabel("남은 목표 기준으로 지금 먹기 좋은 소고기를 추천해드려요")
        hint.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        self.layout_.addWidget(hint)

        # 남은 목표 카드
        self.status_card = QFrame()
        self.status_card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        self.status_layout = QHBoxLayout(self.status_card)
        self.layout_.addWidget(self.status_card)

        # 추천 카드 영역
        self.rec_label = QLabel("추천 메뉴")
        self.rec_label.setStyleSheet("color: #AAAAAA; font-size: 12px; margin-top: 6px;")
        self.layout_.addWidget(self.rec_label)

        self.rec_container = QWidget()
        self.rec_layout = QVBoxLayout(self.rec_container)
        self.rec_layout.setSpacing(10)
        self.layout_.addWidget(self.rec_container)

        refresh_btn = QPushButton("🔄 새로고침")
        refresh_btn.setFixedWidth(120)
        refresh_btn.clicked.connect(self.refresh)
        self.layout_.addWidget(refresh_btn)
        self.layout_.addStretch()

    def refresh(self):
        self.today = date.today().isoformat()
        totals     = get_daily_totals(self.today)
        goal_cal   = int(get_setting("goal_calories", "1800"))
        goal_pro   = int(get_setting("goal_protein",  "150"))

        rem_cal = max(goal_cal - totals["칼로리"], 0)
        rem_pro = max(goal_pro - totals["단백질"], 0)

        # 상태 카드 갱신
        for i in reversed(range(self.status_layout.count())):
            w = self.status_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        for title, val, unit, color in [
            ("이미 섭취", int(totals["칼로리"]), "kcal", "#AAAAAA"),
            ("남은 칼로리", int(rem_cal), "kcal", "#C9A84C"),
            ("이미 섭취", round(totals["단백질"], 1), "g 단백질", "#AAAAAA"),
            ("남은 단백질", round(rem_pro, 1), "g", "#4CAF50"),
        ]:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #3A3A3A; border-radius: 8px; }")
            v = QVBoxLayout(card)
            v.setContentsMargins(10, 8, 10, 8)
            t = QLabel(title)
            t.setStyleSheet("color: #888; font-size: 11px;")
            t.setAlignment(Qt.AlignCenter)
            vl = QLabel(f"{val}")
            vl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold;")
            vl.setAlignment(Qt.AlignCenter)
            ul = QLabel(unit)
            ul.setStyleSheet("color: #888; font-size: 11px;")
            ul.setAlignment(Qt.AlignCenter)
            v.addWidget(t); v.addWidget(vl); v.addWidget(ul)
            self.status_layout.addWidget(card)

        # 추천 카드 갱신
        for i in reversed(range(self.rec_layout.count())):
            w = self.rec_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        if rem_pro <= 0 and rem_cal <= 0:
            done = QLabel("🎉 오늘 목표를 모두 달성했어요!")
            done.setStyleSheet("color: #4CAF50; font-size: 16px; font-weight: bold;")
            done.setAlignment(Qt.AlignCenter)
            self.rec_layout.addWidget(done)
            return

        recs = recommend_meals(rem_cal, rem_pro)
        for i, (score, cut, form, weight, n) in enumerate(recs):
            card = QFrame()
            card.setStyleSheet(
                "QFrame { background-color: #2A2A2A; border-radius: 10px; border-left: 4px solid #8B1A1A; }"
            )
            h = QHBoxLayout(card)
            h.setContentsMargins(14, 12, 14, 12)

            rank = QLabel(f"#{i+1}")
            rank.setStyleSheet("color: #C9A84C; font-size: 18px; font-weight: bold; min-width: 30px;")
            h.addWidget(rank)

            info = QVBoxLayout()
            name = QLabel(f"{cut}  {form}  {weight}g")
            name.setStyleSheet("color: #FAF3E0; font-size: 14px; font-weight: bold;")
            macros = QLabel(f"칼로리 {n['칼로리']} kcal  |  단백질 {n['단백질']}g  |  지방 {n['지방']}g")
            macros.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            info.addWidget(name)
            info.addWidget(macros)
            h.addLayout(info)
            h.addStretch()

            # 단백질 달성도 뱃지
            if rem_pro > 0:
                pct = min(int(n["단백질"] / rem_pro * 100), 100)
                badge_color = "#4CAF50" if pct >= 80 else "#C9A84C" if pct >= 50 else "#888"
                badge = QLabel(f"단백질 {pct}% 달성")
                badge.setStyleSheet(
                    f"color: {badge_color}; font-size: 11px; font-weight: bold; "
                    f"border: 1px solid {badge_color}; border-radius: 4px; padding: 2px 8px;"
                )
                h.addWidget(badge)

            self.rec_layout.addWidget(card)
