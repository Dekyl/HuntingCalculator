from PyQt6.QtWidgets import QWidget, QVBoxLayout

class ViewSessionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        _ = QVBoxLayout(self)
        self.setStyleSheet("""
            background-color: rgb(30, 30, 30);
        """)