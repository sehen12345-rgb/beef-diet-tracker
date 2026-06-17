from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QSpinBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from datetime import date
from data.beef_db import get_cuts, get_types, get_nutrition, PACK_SIZES
from data.database import add_food_log, get_food_logs, delete_food_log

MEAL_TYPES = ["아침", "점심", "저녁", "간식"]


class FoodLogTab(QWidget):
    def __init__(self, on_update=None):
        super().__init__()
        self.on_update = on_update
        self.today = date.today().isoformat()
        self._build_ui()
        self._load_logs()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("🍽️ 식단 기록")
        header.setObjectName("title")
        layout.addWidget(header)

        # 입력 카드
        card = QFrame()
        card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; padding: 10px; }")
        card_layout = QVBoxLayout(card)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("식사"))
        self.meal_combo = QComboBox()
        self.meal_combo.addItems(MEAL_TYPES)
        row1.addWidget(self.meal_combo)

        row1.addWidget(QLabel("부위"))
        self.cut_combo = QComboBox()
        self.cut_combo.addItems(get_cuts())
        self.cut_combo.currentTextChanged.connect(self._on_cut_change)
        row1.addWidget(self.cut_combo)

        row1.addWidget(QLabel("형태"))
        self.form_combo = QComboBox()
        row1.addWidget(self.form_combo)

        row1.addWidget(QLabel("중량"))
        self.weight_spin = QSpinBox()
        self.weight_spin.setRange(50, 500)
        self.weight_spin.setSingleStep(50)
        self.weight_spin.setValue(100)
        self.weight_spin.setSuffix(" g")
        self.weight_spin.valueChanged.connect(self._update_preview)
        row1.addWidget(self.weight_spin)

        card_layout.addLayout(row1)

        # 팩 단위 버튼
        pack_row = QHBoxLayout()
        pack_row.addWidget(QLabel("빠른선택:"))
        for size in PACK_SIZES:
            btn = QPushButton(f"{size}g 팩")
            btn.setObjectName("secondary")
            btn.setFixedWidth(80)
            btn.clicked.connect(lambda _, s=size: self.weight_spin.setValue(s))
            pack_row.addWidget(btn)
        pack_row.addStretch()
        card_layout.addLayout(pack_row)

        # 영양성분 미리보기
        self.preview_label = QLabel("칼로리: 0 kcal  |  단백질: 0 g  |  지방: 0 g")
        self.preview_label.setStyleSheet("color: #C9A84C; font-size: 13px; font-weight: bold;")
        card_layout.addWidget(self.preview_label)

        add_btn = QPushButton("+ 추가")
        add_btn.setFixedWidth(100)
        add_btn.clicked.connect(self._add_log)
        card_layout.addWidget(add_btn, alignment=Qt.AlignRight)

        layout.addWidget(card)

        # 오늘 기록 테이블
        layout.addWidget(QLabel("오늘 기록", styleSheet="color: #AAAAAA; font-size: 12px;"))
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["식사", "부위", "형태", "중량(g)", "칼로리", "단백질(g)", "지방(g)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        del_btn = QPushButton("선택 삭제")
        del_btn.setObjectName("secondary")
        del_btn.clicked.connect(self._delete_selected)
        layout.addWidget(del_btn, alignment=Qt.AlignRight)

        # 초기 form_combo 세팅
        self._on_cut_change(self.cut_combo.currentText())
        self._update_preview()

    def _on_cut_change(self, cut: str):
        self.form_combo.clear()
        self.form_combo.addItems(get_types(cut))
        self._update_preview()

    def _update_preview(self):
        cut  = self.cut_combo.currentText()
        form = self.form_combo.currentText()
        wt   = self.weight_spin.value()
        n = get_nutrition(cut, form, wt)
        self.preview_label.setText(
            f"칼로리: {n['칼로리']} kcal  |  단백질: {n['단백질']} g  |  지방: {n['지방']} g"
        )

    def _add_log(self):
        cut  = self.cut_combo.currentText()
        form = self.form_combo.currentText()
        wt   = self.weight_spin.value()
        meal = self.meal_combo.currentText()
        n = get_nutrition(cut, form, wt)
        add_food_log(self.today, meal, cut, form, wt, n["칼로리"], n["단백질"], n["지방"])
        self._load_logs()
        if self.on_update:
            self.on_update()

    def _load_logs(self):
        rows = get_food_logs(self.today)
        self.table.setRowCount(0)
        self._row_ids = []
        for row in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self._row_ids.append(row[0])
            for c, val in enumerate(row[2:]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

    def _delete_selected(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        log_id = self._row_ids[selected]
        delete_food_log(log_id)
        self._load_logs()
        if self.on_update:
            self.on_update()
