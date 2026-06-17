from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QGridLayout, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from datetime import date
import calendar
from data.database import get_monthly_logs, get_food_logs, get_setting


class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self._year  = date.today().year
        self._month = date.today().month
        self._selected_date = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("📅 히스토리")
        header.setObjectName("title")
        layout.addWidget(header)

        # 월 네비게이션
        nav = QHBoxLayout()
        prev_btn = QPushButton("◀")
        prev_btn.setFixedWidth(40)
        prev_btn.clicked.connect(self._prev_month)
        next_btn = QPushButton("▶")
        next_btn.setFixedWidth(40)
        next_btn.clicked.connect(self._next_month)
        self.month_label = QLabel()
        self.month_label.setStyleSheet("color: #C9A84C; font-size: 15px; font-weight: bold;")
        self.month_label.setAlignment(Qt.AlignCenter)
        nav.addWidget(prev_btn)
        nav.addStretch()
        nav.addWidget(self.month_label)
        nav.addStretch()
        nav.addWidget(next_btn)
        layout.addLayout(nav)

        # 이달 통계 카드
        self.stats_card = QFrame()
        self.stats_card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        self.stats_layout = QHBoxLayout(self.stats_card)
        layout.addWidget(self.stats_card)

        # 캘린더
        self.cal_frame = QFrame()
        self.cal_frame.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; padding: 8px; }")
        self.cal_layout = QGridLayout(self.cal_frame)
        self.cal_layout.setSpacing(4)
        layout.addWidget(self.cal_frame)

        # 선택 날짜 상세
        self.detail_label = QLabel("날짜를 클릭하면 그날의 식단이 보여요")
        self.detail_label.setStyleSheet("color: #AAAAAA; font-size: 12px; margin-top: 6px;")
        layout.addWidget(self.detail_label)

        self.detail_table = QTableWidget(0, 5)
        self.detail_table.setHorizontalHeaderLabels(["식사", "부위", "형태", "중량(g)", "단백질(g)"])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.detail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.detail_table.setMaximumHeight(180)
        layout.addWidget(self.detail_table)

    def _prev_month(self):
        if self._month == 1:
            self._month = 12; self._year -= 1
        else:
            self._month -= 1
        self.refresh()

    def _next_month(self):
        if self._month == 12:
            self._month = 1; self._year += 1
        else:
            self._month += 1
        self.refresh()

    def refresh(self):
        self.month_label.setText(f"{self._year}년 {self._month}월")
        goal_pro = int(get_setting("goal_protein", "150"))

        rows = get_monthly_logs(self._year, self._month)
        day_data = {r[0]: r for r in rows}

        # 이달 통계
        for i in reversed(range(self.stats_layout.count())):
            w = self.stats_layout.itemAt(i).widget()
            if w: w.deleteLater()

        logged_days = len(rows)
        avg_cal  = int(sum(r[1] for r in rows) / logged_days) if logged_days else 0
        avg_pro  = round(sum(r[2] for r in rows) / logged_days, 1) if logged_days else 0
        hit_days = sum(1 for r in rows if r[2] >= goal_pro)

        for title, val, color in [
            ("기록한 날", f"{logged_days}일", "#C9A84C"),
            ("평균 칼로리", f"{avg_cal} kcal", "#FAF3E0"),
            ("평균 단백질", f"{avg_pro} g", "#4CAF50"),
            ("목표 달성일", f"{hit_days}일", "#FF6B35"),
        ]:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #3A3A3A; border-radius: 8px; }")
            v = QVBoxLayout(card); v.setContentsMargins(10, 8, 10, 8)
            t = QLabel(title); t.setStyleSheet("color:#888; font-size:11px;"); t.setAlignment(Qt.AlignCenter)
            vl = QLabel(val); vl.setStyleSheet(f"color:{color}; font-size:16px; font-weight:bold;"); vl.setAlignment(Qt.AlignCenter)
            v.addWidget(t); v.addWidget(vl)
            self.stats_layout.addWidget(card)

        # 캘린더 그리기
        for i in reversed(range(self.cal_layout.count())):
            w = self.cal_layout.itemAt(i).widget()
            if w: w.deleteLater()

        days_kor = ["월", "화", "수", "목", "금", "토", "일"]
        for col, d in enumerate(days_kor):
            lbl = QLabel(d)
            lbl.setStyleSheet("color: #C9A84C; font-size: 12px; font-weight: bold;")
            lbl.setAlignment(Qt.AlignCenter)
            self.cal_layout.addWidget(lbl, 0, col)

        cal = calendar.monthcalendar(self._year, self._month)
        today_str = date.today().isoformat()

        for row_i, week in enumerate(cal):
            for col_i, day in enumerate(week):
                if day == 0:
                    continue
                day_str = f"{self._year:04d}-{self._month:02d}-{day:02d}"
                data    = day_data.get(day_str)

                if data:
                    pro = data[2]
                    if pro >= goal_pro:
                        bg, fg = "#1A3A1A", "#4CAF50"
                    elif pro >= goal_pro * 0.5:
                        bg, fg = "#3A2A00", "#C9A84C"
                    else:
                        bg, fg = "#3A1A1A", "#FF6B35"
                else:
                    bg, fg = "#2A2A2A", "#666"

                btn = QPushButton(str(day))
                btn.setFixedSize(44, 44)
                border = "border: 2px solid #C9A84C;" if day_str == today_str else ""
                btn.setStyleSheet(
                    f"QPushButton {{ background-color: {bg}; color: {fg}; "
                    f"border-radius: 6px; font-size: 13px; font-weight: bold; {border} }}"
                    f"QPushButton:hover {{ background-color: #4A4A4A; }}"
                )
                btn.clicked.connect(lambda _, d=day_str: self._show_detail(d))
                self.cal_layout.addWidget(btn, row_i + 1, col_i)

    def _show_detail(self, day_str):
        self.detail_label.setText(f"📋 {day_str} 식단")
        logs = get_food_logs(day_str)
        self.detail_table.setRowCount(0)
        for row in logs:
            r = self.detail_table.rowCount()
            self.detail_table.insertRow(r)
            for c, val in enumerate([row[2], row[3], row[4], row[5], row[7]]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.detail_table.setItem(r, c, item)
