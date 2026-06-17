from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QProgressBar, QPushButton, QSpinBox,
                             QDoubleSpinBox, QGridLayout)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import date
from data.database import get_daily_totals, get_setting, save_weight, save_setting


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.today = date.today().isoformat()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # 헤더
        header = QLabel("🥩 오늘의 소고기 식단")
        header.setObjectName("title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        date_label = QLabel(f"📅 {self.today}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        layout.addWidget(date_label)

        # 목표 설정 카드
        goal_card = self._make_card()
        goal_layout = QGridLayout(goal_card)
        goal_layout.addWidget(self._label("목표 체중 (kg)", "#AAAAAA"), 0, 0)
        goal_layout.addWidget(self._label("목표 칼로리 (kcal)", "#AAAAAA"), 0, 2)
        goal_layout.addWidget(self._label("목표 단백질 (g)", "#AAAAAA"), 0, 4)

        self.goal_weight = QDoubleSpinBox()
        self.goal_weight.setRange(30, 200)
        self.goal_weight.setValue(float(get_setting("goal_weight", "65")))
        self.goal_weight.setSuffix(" kg")

        self.goal_cal = QSpinBox()
        self.goal_cal.setRange(500, 5000)
        self.goal_cal.setValue(int(get_setting("goal_calories", "1800")))
        self.goal_cal.setSuffix(" kcal")

        self.goal_protein = QSpinBox()
        self.goal_protein.setRange(30, 300)
        self.goal_protein.setValue(int(get_setting("goal_protein", "150")))
        self.goal_protein.setSuffix(" g")

        save_btn = QPushButton("저장")
        save_btn.setFixedWidth(70)
        save_btn.clicked.connect(self._save_goals)

        goal_layout.addWidget(self.goal_weight, 1, 0)
        goal_layout.addWidget(self.goal_cal,    1, 2)
        goal_layout.addWidget(self.goal_protein, 1, 4)
        goal_layout.addWidget(save_btn, 1, 6)
        layout.addWidget(goal_card)

        # 오늘 수치 카드
        stats_layout = QHBoxLayout()
        self.cal_card  = self._stat_card("칼로리", "0", "kcal")
        self.pro_card  = self._stat_card("단백질", "0", "g")
        self.fat_card  = self._stat_card("지방", "0", "g")
        self.beef_card = self._stat_card("소고기 섭취", "0", "g")
        stats_layout.addWidget(self.cal_card[0])
        stats_layout.addWidget(self.pro_card[0])
        stats_layout.addWidget(self.fat_card[0])
        stats_layout.addWidget(self.beef_card[0])
        layout.addLayout(stats_layout)

        # 진행률 바
        prog_card = self._make_card()
        prog_layout = QVBoxLayout(prog_card)
        prog_layout.addWidget(self._label("칼로리 달성률", "#AAAAAA"))
        self.cal_bar = QProgressBar()
        prog_layout.addWidget(self.cal_bar)
        prog_layout.addWidget(self._label("단백질 달성률", "#AAAAAA"))
        self.pro_bar = QProgressBar()
        self.pro_bar.setObjectName("progress_green")
        prog_layout.addWidget(self.pro_bar)
        layout.addWidget(prog_card)

        # 오늘 체중 입력
        weight_card = self._make_card()
        w_layout = QHBoxLayout(weight_card)
        w_layout.addWidget(self._label("오늘 체중", "#AAAAAA"))
        self.today_weight = QDoubleSpinBox()
        self.today_weight.setRange(30, 200)
        self.today_weight.setSuffix(" kg")
        self.today_weight.setValue(float(get_setting("last_weight", "70")))
        w_btn = QPushButton("기록")
        w_btn.setFixedWidth(70)
        w_btn.clicked.connect(self._save_weight)
        w_layout.addWidget(self.today_weight)
        w_layout.addWidget(w_btn)
        w_layout.addStretch()
        layout.addWidget(weight_card)

        layout.addStretch()

    def _stat_card(self, title, value, unit):
        card = self._make_card()
        v_layout = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        t.setAlignment(Qt.AlignCenter)
        val = QLabel(value)
        val.setObjectName("value_big")
        val.setAlignment(Qt.AlignCenter)
        u = QLabel(unit)
        u.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        u.setAlignment(Qt.AlignCenter)
        v_layout.addWidget(t)
        v_layout.addWidget(val)
        v_layout.addWidget(u)
        return card, val

    def _make_card(self):
        f = QFrame()
        f.setObjectName("card")
        f.setStyleSheet("QFrame#card { background-color: #2A2A2A; border-radius: 10px; }")
        return f

    def _label(self, text, color="#F5F5F5"):
        l = QLabel(text)
        l.setStyleSheet(f"color: {color};")
        return l

    def _save_goals(self):
        save_setting("goal_weight", str(self.goal_weight.value()))
        save_setting("goal_calories", str(self.goal_cal.value()))
        save_setting("goal_protein", str(self.goal_protein.value()))
        self.refresh()

    def _save_weight(self):
        save_weight(self.today, self.today_weight.value())
        save_setting("last_weight", str(self.today_weight.value()))

    def refresh(self):
        totals = get_daily_totals(self.today)
        goal_cal = int(get_setting("goal_calories", "1800"))
        goal_pro = int(get_setting("goal_protein", "150"))

        self.cal_card[1].setText(str(int(totals["칼로리"])))
        self.pro_card[1].setText(str(round(totals["단백질"], 1)))
        self.fat_card[1].setText(str(round(totals["지방"], 1)))
        self.beef_card[1].setText(str(int(totals["소고기_g"])))

        cal_pct = min(int(totals["칼로리"] / goal_cal * 100), 100)
        pro_pct = min(int(totals["단백질"] / goal_pro * 100), 100)
        self.cal_bar.setValue(cal_pct)
        self.pro_bar.setValue(pro_pct)
        self.cal_bar.setFormat(f"  {cal_pct}%  ({int(totals['칼로리'])}/{goal_cal} kcal)")
        self.pro_bar.setFormat(f"  {pro_pct}%  ({round(totals['단백질'],1)}/{goal_pro} g)")
        self.cal_bar.setTextVisible(True)
        self.pro_bar.setTextVisible(True)
        self.cal_bar.setStyleSheet("QProgressBar { color: #F5F5F5; text-align: center; }")
        self.pro_bar.setStyleSheet("QProgressBar { color: #F5F5F5; text-align: center; } QProgressBar::chunk { background-color: #4CAF50; border-radius: 5px; }")
