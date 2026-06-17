from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame)
from PyQt5.QtCore import Qt
from datetime import date, timedelta
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False
from data.database import get_weight_history, get_weekly_summary, get_setting


class ReportTab(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("📊 주간 리포트")
        header.setObjectName("title")
        layout.addWidget(header)

        refresh_btn = QPushButton("새로고침")
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(refresh_btn, alignment=Qt.AlignRight)

        # 이번 주 요약 카드
        self.summary_card = QFrame()
        self.summary_card.setStyleSheet(
            "QFrame { background-color: #2A2A2A; border-radius: 10px; padding: 10px; }"
        )
        self.summary_layout = QVBoxLayout(self.summary_card)
        layout.addWidget(self.summary_card)

        # 체중 변화 그래프
        weight_label = QLabel("체중 변화 (최근 30일)", styleSheet="color: #AAAAAA; font-size: 12px;")
        layout.addWidget(weight_label)

        self.weight_fig = Figure(figsize=(6, 2.5), facecolor="#2A2A2A")
        self.weight_canvas = FigureCanvas(self.weight_fig)
        layout.addWidget(self.weight_canvas)

        # 단백질 달성률 그래프
        protein_label = QLabel("이번 주 단백질 달성률", styleSheet="color: #AAAAAA; font-size: 12px;")
        layout.addWidget(protein_label)

        self.protein_fig = Figure(figsize=(6, 2), facecolor="#2A2A2A")
        self.protein_canvas = FigureCanvas(self.protein_fig)
        layout.addWidget(self.protein_canvas)

    def refresh(self):
        self._update_summary()
        self._draw_weight_chart()
        self._draw_protein_chart()

    def _update_summary(self):
        for i in reversed(range(self.summary_layout.count())):
            self.summary_layout.itemAt(i).widget().deleteLater()

        today = date.today()
        start = (today - timedelta(days=6)).isoformat()
        end = today.isoformat()
        rows = get_weekly_summary(start, end)

        goal_pro = int(get_setting("goal_protein", "150"))
        total_cal = sum(r[1] for r in rows)
        total_pro = sum(r[2] for r in rows)
        total_beef = sum(r[4] for r in rows)
        days = len(rows) or 1

        items = [
            ("이번 주 평균 칼로리", f"{int(total_cal/days)} kcal/일"),
            ("이번 주 평균 단백질", f"{round(total_pro/days, 1)} g/일"),
            ("이번 주 소고기 총량", f"{int(total_beef)} g"),
            ("단백질 목표 달성일", f"{sum(1 for r in rows if r[2] >= goal_pro)} / {len(rows)} 일"),
        ]

        row_layout = QHBoxLayout()
        for title, value in items:
            card = QFrame()
            card.setStyleSheet("QFrame { background-color: #3A3A3A; border-radius: 8px; padding: 8px; }")
            v = QVBoxLayout(card)
            t = QLabel(title)
            t.setStyleSheet("color: #AAAAAA; font-size: 11px;")
            t.setAlignment(Qt.AlignCenter)
            val = QLabel(value)
            val.setStyleSheet("color: #C9A84C; font-size: 16px; font-weight: bold;")
            val.setAlignment(Qt.AlignCenter)
            v.addWidget(t)
            v.addWidget(val)
            row_layout.addWidget(card)

        self.summary_layout.addLayout(row_layout)

    def _draw_weight_chart(self):
        self.weight_fig.clear()
        ax = self.weight_fig.add_subplot(111)
        ax.set_facecolor("#2A2A2A")
        self.weight_fig.patch.set_facecolor("#2A2A2A")

        history = get_weight_history(30)
        if len(history) < 2:
            ax.text(0.5, 0.5, "데이터가 부족합니다\n(최소 2일 이상 체중 기록 필요)",
                    ha="center", va="center", color="#AAAAAA", transform=ax.transAxes)
        else:
            dates = [r[0][5:] for r in history]  # MM-DD
            weights = [r[1] for r in history]
            ax.plot(dates, weights, color="#C9A84C", marker="o", linewidth=2, markersize=5)
            ax.fill_between(range(len(dates)), weights, min(weights)-0.5,
                            alpha=0.15, color="#C9A84C")
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=45, fontsize=9, color="#AAAAAA")
            ax.tick_params(axis="y", colors="#AAAAAA")
            ax.spines["bottom"].set_color("#3A3A3A")
            ax.spines["left"].set_color("#3A3A3A")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.set_ylabel("kg", color="#AAAAAA", fontsize=10)

        self.weight_fig.tight_layout()
        self.weight_canvas.draw()

    def _draw_protein_chart(self):
        self.protein_fig.clear()
        ax = self.protein_fig.add_subplot(111)
        ax.set_facecolor("#2A2A2A")
        self.protein_fig.patch.set_facecolor("#2A2A2A")

        today = date.today()
        start = (today - timedelta(days=6)).isoformat()
        rows = get_weekly_summary(start, today.isoformat())
        goal_pro = int(get_setting("goal_protein", "150"))

        if not rows:
            ax.text(0.5, 0.5, "이번 주 식단 기록이 없습니다",
                    ha="center", va="center", color="#AAAAAA", transform=ax.transAxes)
        else:
            days = [r[0][5:] for r in rows]
            proteins = [r[2] for r in rows]
            colors = ["#4CAF50" if p >= goal_pro else "#8B1A1A" for p in proteins]
            ax.bar(days, proteins, color=colors, width=0.5)
            ax.axhline(y=goal_pro, color="#C9A84C", linestyle="--", linewidth=1.5, label=f"목표 {goal_pro}g")
            ax.tick_params(colors="#AAAAAA")
            ax.spines["bottom"].set_color("#3A3A3A")
            ax.spines["left"].set_color("#3A3A3A")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.set_ylabel("단백질 (g)", color="#AAAAAA", fontsize=10)
            ax.legend(facecolor="#2A2A2A", labelcolor="#AAAAAA", fontsize=9)

        self.protein_fig.tight_layout()
        self.protein_canvas.draw()
