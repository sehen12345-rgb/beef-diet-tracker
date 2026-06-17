DARK_STYLE = """
QMainWindow, QWidget {
    background-color: #1E1E1E;
    color: #F5F5F5;
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
    font-size: 13px;
}

QTabWidget::pane {
    border: 1px solid #3A3A3A;
    background-color: #1E1E1E;
}

QTabBar::tab {
    background-color: #2A2A2A;
    color: #AAAAAA;
    padding: 10px 20px;
    border: none;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #8B1A1A;
    color: #FAF3E0;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #3A3A3A;
}

QPushButton {
    background-color: #8B1A1A;
    color: #FAF3E0;
    border: none;
    padding: 8px 18px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #A52020;
}

QPushButton:pressed {
    background-color: #6B1010;
}

QPushButton#secondary {
    background-color: #2A2A2A;
    color: #C9A84C;
    border: 1px solid #C9A84C;
}

QPushButton#secondary:hover {
    background-color: #3A3A3A;
}

QComboBox {
    background-color: #2A2A2A;
    color: #F5F5F5;
    border: 1px solid #3A3A3A;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 13px;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #2A2A2A;
    color: #F5F5F5;
    selection-background-color: #8B1A1A;
}

QSpinBox, QDoubleSpinBox {
    background-color: #2A2A2A;
    color: #F5F5F5;
    border: 1px solid #3A3A3A;
    padding: 6px 10px;
    border-radius: 4px;
    font-size: 13px;
}

QLabel#title {
    font-size: 20px;
    font-weight: bold;
    color: #C9A84C;
}

QLabel#subtitle {
    font-size: 15px;
    font-weight: bold;
    color: #FAF3E0;
}

QLabel#value_big {
    font-size: 28px;
    font-weight: bold;
    color: #C9A84C;
}

QLabel#value_green {
    font-size: 28px;
    font-weight: bold;
    color: #4CAF50;
}

QLabel#value_red {
    font-size: 28px;
    font-weight: bold;
    color: #FF6B35;
}

QFrame#card {
    background-color: #2A2A2A;
    border-radius: 10px;
    padding: 15px;
}

QProgressBar {
    background-color: #3A3A3A;
    border: none;
    border-radius: 5px;
    height: 12px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #8B1A1A;
    border-radius: 5px;
}

QProgressBar#progress_green::chunk {
    background-color: #4CAF50;
}

QTableWidget {
    background-color: #2A2A2A;
    color: #F5F5F5;
    gridline-color: #3A3A3A;
    border: none;
    font-size: 13px;
}

QTableWidget::item:selected {
    background-color: #8B1A1A;
}

QHeaderView::section {
    background-color: #3A3A3A;
    color: #C9A84C;
    padding: 6px;
    border: none;
    font-weight: bold;
}

QScrollBar:vertical {
    background-color: #2A2A2A;
    width: 8px;
}

QScrollBar::handle:vertical {
    background-color: #4A4A4A;
    border-radius: 4px;
}

QDateEdit {
    background-color: #2A2A2A;
    color: #F5F5F5;
    border: 1px solid #3A3A3A;
    padding: 6px 10px;
    border-radius: 4px;
}
"""
