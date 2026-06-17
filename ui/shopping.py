import webbrowser
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QScrollArea)
from PyQt5.QtCore import Qt
from datetime import date
from data.database import get_consumption_by_cut, get_setting
from data.beef_db import PACK_SIZES

SEARCH_URL = "https://search.shopping.naver.com/search/all?query={}"


class ShoppingTab(QWidget):
    def __init__(self):
        super().__init__()
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

        header = QLabel("🛒 이번 주 장보기")
        header.setObjectName("title")
        layout.addWidget(header)

        hint = QLabel("최근 4주 평균 소비량을 기반으로 이번 주 구매 목록을 자동으로 만들어드려요")
        hint.setStyleSheet("color: #AAAAAA; font-size: 12px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # 요약 카드
        self.summary_card = QFrame()
        self.summary_card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        self.summary_layout = QHBoxLayout(self.summary_card)
        layout.addWidget(self.summary_card)

        # 리스트 테이블
        layout.addWidget(QLabel("추천 구매 목록", styleSheet="color: #AAAAAA; font-size: 12px;"))
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["부위", "형태", "추천 구매량", "네이버 쇼핑"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setMaximumHeight(300)
        layout.addWidget(self.table)

        refresh_btn = QPushButton("🔄 목록 새로고침")
        refresh_btn.setFixedWidth(140)
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn)

        # 팁 카드
        tip_card = QFrame()
        tip_card.setStyleSheet("QFrame { background-color: #2A2A2A; border-radius: 10px; }")
        tip_layout = QVBoxLayout(tip_card)
        tip_title = QLabel("💡 구매 팁")
        tip_title.setStyleSheet("color: #C9A84C; font-size: 13px; font-weight: bold;")
        tip_layout.addWidget(tip_title)
        for tip in [
            "100g 팩은 냉동 보관 시 3개월까지 신선도 유지돼요",
            "주 1회 대량 구매 → 200g 팩이 단가가 낮아요",
            "부채살은 구이, 홍두깨살은 장조림·볶음에 최적이에요",
            "다짐육은 햄버거 패티·미트볼로 활용하면 식단이 지루하지 않아요",
        ]:
            t = QLabel(f"• {tip}")
            t.setStyleSheet("color: #AAAAAA; font-size: 12px;")
            t.setWordWrap(True)
            tip_layout.addWidget(t)
        layout.addWidget(tip_card)
        layout.addStretch()

    def refresh(self):
        for i in reversed(range(self.summary_layout.count())):
            w = self.summary_layout.itemAt(i).widget()
            if w: w.deleteLater()

        consumption = get_consumption_by_cut(weeks=4)
        total_g = sum(r[2] for r in consumption)
        weekly_avg = int(total_g / 4) if total_g else 0
        recommended = int(weekly_avg * 1.1)

        for title, val, color in [
            ("4주 평균 주간 소비", f"{weekly_avg} g", "#AAAAAA"),
            ("이번 주 추천 구매량", f"{recommended} g", "#C9A84C"),
            ("약", f"{recommended // 100} 팩 (100g 기준)", "#FAF3E0"),
        ]:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #3A3A3A; border-radius: 8px; }")
            v = QVBoxLayout(card); v.setContentsMargins(10, 8, 10, 8)
            t = QLabel(title); t.setStyleSheet("color:#888; font-size:11px;"); t.setAlignment(Qt.AlignCenter)
            vl = QLabel(val); vl.setStyleSheet(f"color:{color}; font-size:16px; font-weight:bold;"); vl.setAlignment(Qt.AlignCenter)
            v.addWidget(t); v.addWidget(vl)
            self.summary_layout.addWidget(card)

        self.table.setRowCount(0)
        self._links = []

        if not consumption:
            self.table.insertRow(0)
            msg = QTableWidgetItem("식단을 먼저 기록해주세요")
            msg.setTextAlignment(Qt.AlignCenter)
            msg.setForeground(Qt.gray)
            self.table.setItem(0, 0, msg)
            return

        for cut, form, total in consumption:
            ratio = total / (total_g or 1)
            rec_g = int(recommended * ratio)
            rec_g = max(rec_g, 100)

            r = self.table.rowCount()
            self.table.insertRow(r)
            for c, val in [(0, cut), (1, form), (2, f"{rec_g}g ({rec_g//100}팩)")]:
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(r, c, item)

            search_query = f"호주산 소고기 {cut} {form}"
            url = SEARCH_URL.format(search_query.replace(" ", "+"))
            self._links.append(url)

            btn = QPushButton("🔍 검색")
            btn.setStyleSheet(
                "QPushButton { background-color: #2A2A2A; color: #C9A84C; "
                "border: 1px solid #C9A84C; border-radius: 4px; padding: 4px 10px; font-size: 12px; }"
                "QPushButton:hover { background-color: #3A3A3A; }"
            )
            btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
            self.table.setCellWidget(r, 3, btn)
