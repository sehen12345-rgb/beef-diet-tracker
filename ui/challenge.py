from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QGridLayout, QSpinBox,
                             QScrollArea, QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from datetime import date, timedelta
from data.database import (create_challenge, get_active_challenge,
                           get_challenge_days, sync_challenge_daily, get_setting)


class ChallengeTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        container = QWidget()
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setSpacing(14)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        scroll.setWidget(container)

        header = QLabel("🔥 50일 챌린지")
        header.setObjectName("title")
        self.main_layout.addWidget(header)

        # 챌린지 시작 카드
        start_card = QFrame()
        start_card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        start_layout = QVBoxLayout(start_card)

        start_title = QLabel("새 챌린지 시작")
        start_title.setStyleSheet("color: #C9A84C; font-size: 13px; font-weight: bold;")
        start_layout.addWidget(start_title)

        row = QHBoxLayout()
        row.addWidget(QLabel("시작일", styleSheet="color:#AAAAAA;"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        row.addWidget(self.start_date)

        row.addWidget(QLabel("단백질 목표", styleSheet="color:#AAAAAA;"))
        self.ch_protein = QSpinBox()
        self.ch_protein.setRange(50, 300)
        self.ch_protein.setValue(int(get_setting("goal_protein", "150")))
        self.ch_protein.setSuffix(" g/일")
        row.addWidget(self.ch_protein)

        start_btn = QPushButton("🚀 챌린지 시작!")
        start_btn.clicked.connect(self._start_challenge)
        row.addWidget(start_btn)
        row.addStretch()
        start_layout.addLayout(row)
        self.main_layout.addWidget(start_card)

        # 현재 챌린지 상태 (동적)
        self.status_card = QFrame()
        self.status_card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        self.status_layout = QVBoxLayout(self.status_card)
        self.main_layout.addWidget(self.status_card)

        # 50칸 그리드
        grid_label = QLabel("50일 진행 현황", styleSheet="color:#AAAAAA; font-size:12px;")
        self.main_layout.addWidget(grid_label)

        self.grid_frame = QFrame()
        self.grid_frame.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; padding: 10px; }")
        self.grid_layout = QGridLayout(self.grid_frame)
        self.grid_layout.setSpacing(6)
        self.main_layout.addWidget(self.grid_frame)

        self.main_layout.addStretch()

    def _start_challenge(self):
        ch = get_active_challenge()
        if ch:
            reply = QMessageBox.question(self, "챌린지 재시작",
                "기존 챌린지를 종료하고 새로 시작할까요?",
                QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return

        start = self.start_date.date().toString("yyyy-MM-dd")
        end = (date.fromisoformat(start) + timedelta(days=49)).isoformat()
        goal = self.ch_protein.value()
        create_challenge(start, end, goal)
        self.refresh()

    def refresh(self):
        # 상태 카드 초기화
        for i in reversed(range(self.status_layout.count())):
            w = self.status_layout.itemAt(i).widget()
            if w: w.deleteLater()

        # 그리드 초기화
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w: w.deleteLater()

        ch = get_active_challenge()
        if not ch:
            no_ch = QLabel("아직 챌린지가 없어요. 위에서 시작해보세요!")
            no_ch.setStyleSheet("color: #AAAAAA; font-size: 13px;")
            no_ch.setAlignment(Qt.AlignCenter)
            self.status_layout.addWidget(no_ch)
            return

        ch_id, start_str, end_str, goal_protein = ch
        sync_challenge_daily(ch_id, goal_protein)

        today = date.today()
        start = date.fromisoformat(start_str)
        end   = date.fromisoformat(end_str)
        days_elapsed = (today - start).days + 1
        days_left = max((end - today).days, 0)
        total_days = (end - start).days + 1

        daily = get_challenge_days(ch_id, start_str, end_str)
        achieved_days = sum(1 for d in daily if d[1])

        # 스트릭 계산
        streak = 0
        for d in reversed(daily):
            if d[1]:
                streak += 1
            else:
                break

        # 상태 카드
        stats = [
            ("진행일",    f"{min(days_elapsed, 50)} / 50일", "#C9A84C"),
            ("달성일",    f"{achieved_days}일",              "#4CAF50"),
            ("연속 달성", f"{streak}일 🔥",                  "#FF6B35"),
            ("남은 날",   f"{days_left}일",                  "#AAAAAA"),
        ]
        row = QHBoxLayout()
        for title, val, color in stats:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #3A3A3A; border-radius: 8px; }")
            v = QVBoxLayout(card)
            v.setContentsMargins(10, 8, 10, 8)
            t = QLabel(title); t.setStyleSheet("color:#888; font-size:11px;"); t.setAlignment(Qt.AlignCenter)
            vl = QLabel(val);  vl.setStyleSheet(f"color:{color}; font-size:18px; font-weight:bold;"); vl.setAlignment(Qt.AlignCenter)
            v.addWidget(t); v.addWidget(vl)
            row.addWidget(card)
        self.status_layout.addLayout(row)

        # 달성률 바
        pct = int(achieved_days / 50 * 100)
        bar_label = QLabel(f"전체 달성률  {pct}%  ({achieved_days}/50일)")
        bar_label.setStyleSheet("color:#FAF3E0; font-size:12px; margin-top:6px;")
        self.status_layout.addWidget(bar_label)
        bar_bg = QFrame()
        bar_bg.setFixedHeight(14)
        bar_bg.setStyleSheet("QFrame { background-color: #3A3A3A; border-radius: 7px; }")
        bar_inner = QFrame(bar_bg)
        bar_inner.setFixedHeight(14)
        bar_inner.setFixedWidth(max(int(pct * 3.5), 8))
        bar_inner.setStyleSheet("QFrame { background-color: #8B1A1A; border-radius: 7px; }")
        self.status_layout.addWidget(bar_bg)

        # 50칸 그리드
        daily_map = {d[0]: d[1] for d in daily}
        for i in range(50):
            day_date = start + timedelta(days=i)
            day_str  = day_date.isoformat()
            achieved = daily_map.get(day_str, None)

            cell = QLabel(str(i + 1))
            cell.setFixedSize(44, 44)
            cell.setAlignment(Qt.AlignCenter)
            cell.setStyleSheet("font-size: 12px; font-weight: bold; border-radius: 6px; " + (
                "background-color: #4CAF50; color: #FFF;" if achieved == 1 else
                "background-color: #8B1A1A; color: #FFF;" if achieved == 0 else
                "background-color: #3A3A3A; color: #666;"
            ))
            if day_date == today:
                cell.setStyleSheet(cell.styleSheet() + " border: 2px solid #C9A84C;")
            cell.setToolTip(f"{day_str}\n{'✅ 달성' if achieved==1 else '❌ 미달성' if achieved==0 else '예정'}")
            self.grid_layout.addWidget(cell, i // 10, i % 10)

        # 범례
        legend = QHBoxLayout()
        for color, text in [("#4CAF50","달성"), ("#8B1A1A","미달성"), ("#3A3A3A","예정")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 14px;")
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #AAAAAA; font-size: 11px; margin-right: 10px;")
            legend.addWidget(dot); legend.addWidget(lbl)
        legend.addStretch()
        self.grid_layout.addLayout(legend, 5, 0, 1, 10)
