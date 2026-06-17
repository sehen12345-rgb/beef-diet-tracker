from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QProgressBar, QPushButton, QSpinBox,
                             QDoubleSpinBox, QGridLayout, QComboBox, QScrollArea)
from PyQt5.QtCore import Qt
from datetime import date
from data.database import get_daily_totals, get_setting, save_weight, save_setting


def calc_goals(gender, age, height_cm, weight_kg, activity, goal):
    # BMR (Mifflin-St Jeor)
    if gender == "남성":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_map = {
        "거의 안 함 (좌식생활)": 1.2,
        "가벼운 운동 (주 1~3회)": 1.375,
        "보통 운동 (주 3~5회)": 1.55,
        "강도 높은 운동 (주 6~7회)": 1.725,
    }
    tdee = bmr * activity_map.get(activity, 1.375)

    goal_map = {"체중 감량": -300, "체중 유지": 0, "근육 증가": +300}
    target_cal = int(tdee + goal_map.get(goal, 0))

    # 단백질: 감량 시 체중 × 2.0g, 유지/증가 시 × 1.6g
    protein_ratio = 2.0 if goal == "체중 감량" else 1.6
    target_protein = int(weight_kg * protein_ratio)

    return target_cal, target_protein


class DashboardTab(QWidget):
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
        layout = QVBoxLayout(container)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)
        scroll.setWidget(container)

        # 헤더
        header = QLabel("🥩 오늘의 소고기 식단")
        header.setObjectName("title")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        date_label = QLabel(f"📅 {self.today}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        layout.addWidget(date_label)

        # ── 자동 계산기 카드 ──────────────────────────────
        calc_card = self._make_card()
        calc_layout = QVBoxLayout(calc_card)

        calc_title = QLabel("⚡ 내 목표 자동 계산")
        calc_title.setStyleSheet("color: #C9A84C; font-size: 14px; font-weight: bold;")
        calc_layout.addWidget(calc_title)

        hint = QLabel("키·몸무게·나이를 입력하면 칼로리·단백질 목표를 자동으로 계산해드려요")
        hint.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        hint.setWordWrap(True)
        calc_layout.addWidget(hint)

        row1 = QHBoxLayout()
        row1.addWidget(self._label("성별"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["남성", "여성"])
        self.gender_combo.setCurrentText(get_setting("gender", "남성"))
        row1.addWidget(self.gender_combo)

        row1.addWidget(self._label("나이"))
        self.age_spin = QSpinBox()
        self.age_spin.setRange(10, 100)
        self.age_spin.setValue(int(get_setting("age", "30")))
        self.age_spin.setSuffix(" 세")
        row1.addWidget(self.age_spin)

        row1.addWidget(self._label("키"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 250)
        self.height_spin.setValue(int(get_setting("height", "170")))
        self.height_spin.setSuffix(" cm")
        row1.addWidget(self.height_spin)

        row1.addWidget(self._label("현재 체중"))
        self.cur_weight_spin = QDoubleSpinBox()
        self.cur_weight_spin.setRange(30, 200)
        self.cur_weight_spin.setValue(float(get_setting("cur_weight", "70")))
        self.cur_weight_spin.setSuffix(" kg")
        row1.addWidget(self.cur_weight_spin)
        calc_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self._label("활동량"))
        self.activity_combo = QComboBox()
        self.activity_combo.addItems([
            "거의 안 함 (좌식생활)",
            "가벼운 운동 (주 1~3회)",
            "보통 운동 (주 3~5회)",
            "강도 높은 운동 (주 6~7회)",
        ])
        self.activity_combo.setCurrentText(get_setting("activity", "가벼운 운동 (주 1~3회)"))
        self.activity_combo.setMinimumWidth(200)
        row2.addWidget(self.activity_combo)

        row2.addWidget(self._label("목표"))
        self.goal_combo = QComboBox()
        self.goal_combo.addItems(["체중 감량", "체중 유지", "근육 증가"])
        self.goal_combo.setCurrentText(get_setting("diet_goal", "체중 감량"))
        row2.addWidget(self.goal_combo)
        calc_layout.addLayout(row2)

        self.calc_result = QLabel("")
        self.calc_result.setStyleSheet(
            "color: #4CAF50; font-size: 13px; font-weight: bold; padding: 6px 0;"
        )
        calc_layout.addWidget(self.calc_result)

        calc_btn = QPushButton("🔢 목표 자동 계산")
        calc_btn.clicked.connect(self._auto_calc)
        calc_layout.addWidget(calc_btn, alignment=Qt.AlignLeft)

        layout.addWidget(calc_card)

        # ── 목표 수동 조정 카드 ───────────────────────────
        goal_card = self._make_card()
        goal_grid = QGridLayout(goal_card)

        goal_grid.addWidget(self._label("목표 칼로리", "#AAAAAA"), 0, 0)
        goal_grid.addWidget(self._label("목표 단백질", "#AAAAAA"), 0, 2)
        goal_grid.addWidget(self._label("목표 체중", "#AAAAAA"), 0, 4)

        self.goal_cal = QSpinBox()
        self.goal_cal.setRange(500, 5000)
        self.goal_cal.setValue(int(get_setting("goal_calories", "1800")))
        self.goal_cal.setSuffix(" kcal")

        self.goal_protein = QSpinBox()
        self.goal_protein.setRange(30, 300)
        self.goal_protein.setValue(int(get_setting("goal_protein", "150")))
        self.goal_protein.setSuffix(" g")

        self.goal_weight = QDoubleSpinBox()
        self.goal_weight.setRange(30, 200)
        self.goal_weight.setValue(float(get_setting("goal_weight", "65")))
        self.goal_weight.setSuffix(" kg")

        save_btn = QPushButton("저장")
        save_btn.setFixedWidth(70)
        save_btn.clicked.connect(self._save_goals)

        goal_grid.addWidget(self.goal_cal,     1, 0)
        goal_grid.addWidget(self.goal_protein, 1, 2)
        goal_grid.addWidget(self.goal_weight,  1, 4)
        goal_grid.addWidget(save_btn,          1, 6)
        layout.addWidget(goal_card)

        # ── 오늘 수치 카드 4개 ────────────────────────────
        stats_layout = QHBoxLayout()
        self.cal_card  = self._stat_card("칼로리", "0", "kcal")
        self.pro_card  = self._stat_card("단백질", "0", "g")
        self.fat_card  = self._stat_card("지방", "0", "g")
        self.beef_card = self._stat_card("소고기 섭취", "0", "g")
        for card, _ in [self.cal_card, self.pro_card, self.fat_card, self.beef_card]:
            stats_layout.addWidget(card)
        layout.addLayout(stats_layout)

        # ── 진행률 바 ─────────────────────────────────────
        prog_card = self._make_card()
        prog_layout = QVBoxLayout(prog_card)
        prog_layout.addWidget(self._label("칼로리 달성률", "#AAAAAA"))
        self.cal_bar = QProgressBar()
        prog_layout.addWidget(self.cal_bar)
        prog_layout.addWidget(self._label("단백질 달성률", "#AAAAAA"))
        self.pro_bar = QProgressBar()
        prog_layout.addWidget(self.pro_bar)
        layout.addWidget(prog_card)

        # ── 오늘 체중 입력 ────────────────────────────────
        weight_card = self._make_card()
        w_layout = QHBoxLayout(weight_card)
        w_layout.addWidget(self._label("오늘 체중", "#AAAAAA"))
        self.today_weight = QDoubleSpinBox()
        self.today_weight.setRange(30, 200)
        self.today_weight.setSuffix(" kg")
        self.today_weight.setValue(float(get_setting("cur_weight", "70")))
        w_btn = QPushButton("기록")
        w_btn.setFixedWidth(70)
        w_btn.clicked.connect(self._save_weight)
        w_layout.addWidget(self.today_weight)
        w_layout.addWidget(w_btn)
        w_layout.addStretch()
        layout.addWidget(weight_card)

        layout.addStretch()

    def _auto_calc(self):
        cal, protein = calc_goals(
            self.gender_combo.currentText(),
            self.age_spin.value(),
            self.height_spin.value(),
            self.cur_weight_spin.value(),
            self.activity_combo.currentText(),
            self.goal_combo.currentText(),
        )
        self.goal_cal.setValue(cal)
        self.goal_protein.setValue(protein)
        self.calc_result.setText(
            f"✅ 권장 칼로리 {cal} kcal  |  권장 단백질 {protein} g  — 아래 저장 버튼을 눌러주세요!"
        )
        save_setting("gender",    self.gender_combo.currentText())
        save_setting("age",       str(self.age_spin.value()))
        save_setting("height",    str(self.height_spin.value()))
        save_setting("cur_weight", str(self.cur_weight_spin.value()))
        save_setting("activity",  self.activity_combo.currentText())
        save_setting("diet_goal", self.goal_combo.currentText())

    def _save_goals(self):
        save_setting("goal_calories", str(self.goal_cal.value()))
        save_setting("goal_protein",  str(self.goal_protein.value()))
        save_setting("goal_weight",   str(self.goal_weight.value()))
        self.refresh()

    def _save_weight(self):
        save_weight(self.today, self.today_weight.value())
        save_setting("cur_weight", str(self.today_weight.value()))

    def _stat_card(self, title, value, unit):
        card = self._make_card()
        v = QVBoxLayout(card)
        t = QLabel(title)
        t.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        t.setAlignment(Qt.AlignCenter)
        val = QLabel(value)
        val.setObjectName("value_big")
        val.setAlignment(Qt.AlignCenter)
        u = QLabel(unit)
        u.setStyleSheet("color: #AAAAAA; font-size: 11px;")
        u.setAlignment(Qt.AlignCenter)
        v.addWidget(t); v.addWidget(val); v.addWidget(u)
        return card, val

    def _make_card(self):
        f = QFrame()
        f.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        return f

    def _label(self, text, color="#F5F5F5"):
        l = QLabel(text)
        l.setStyleSheet(f"color: {color};")
        return l

    def refresh(self):
        totals   = get_daily_totals(self.today)
        goal_cal = int(get_setting("goal_calories", "1800"))
        goal_pro = int(get_setting("goal_protein",  "150"))

        self.cal_card[1].setText(str(int(totals["칼로리"])))
        self.pro_card[1].setText(str(round(totals["단백질"], 1)))
        self.fat_card[1].setText(str(round(totals["지방"], 1)))
        self.beef_card[1].setText(str(int(totals["소고기_g"])))

        cal_pct = min(int(totals["칼로리"] / goal_cal * 100), 100) if goal_cal else 0
        pro_pct = min(int(totals["단백질"] / goal_pro * 100), 100) if goal_pro else 0

        self.cal_bar.setValue(cal_pct)
        self.pro_bar.setValue(pro_pct)
        self.cal_bar.setStyleSheet(
            "QProgressBar { color: #F5F5F5; text-align: center; background: #3A3A3A; border-radius: 5px; height: 16px; }"
            "QProgressBar::chunk { background-color: #8B1A1A; border-radius: 5px; }"
        )
        self.pro_bar.setStyleSheet(
            "QProgressBar { color: #F5F5F5; text-align: center; background: #3A3A3A; border-radius: 5px; height: 16px; }"
            "QProgressBar::chunk { background-color: #4CAF50; border-radius: 5px; }"
        )
        self.cal_bar.setFormat(f"  {cal_pct}%  ({int(totals['칼로리'])} / {goal_cal} kcal)")
        self.pro_bar.setFormat(f"  {pro_pct}%  ({round(totals['단백질'],1)} / {goal_pro} g)")
        self.cal_bar.setTextVisible(True)
        self.pro_bar.setTextVisible(True)
