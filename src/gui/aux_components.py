from PySide6.QtWidgets import QFrame, QLabel, QLineEdit
from PySide6.QtGui import QMouseEvent
from PySide6.QtCore import Qt

class QHLine(QFrame):
    """
    A horizontal line widget that can be used to separate sections in a GUI.
    Inherits from QFrame and sets the frame shape to a horizontal line.
    """
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            background-color: 1px rgb(120, 120, 120);
        """)

class QVLine(QFrame):
    """
    A vertical line widget that can be used to separate sections in a GUI.
    Inherits from QFrame and sets the frame shape to a vertical line.
    """
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            background-color: 1px rgb(120, 120, 120);
        """)

class SmartLabel(QLabel):
    """
    A QLabel that automatically updates its tooltip to match its text.
    Inherits from QLabel and overrides the setText method to update the tooltip.
    """
    def __init__(self, text: str = ""):
        """
        Initialize the SmartLabel with optional text.
            :param text: The initial text to display in the label.
        """
        super().__init__(text)
        self.setToolTip(text)
    
    def setText(self, a0: str | None):
        """
        Set the text of the label and update the tooltip.
            :param text: The text to display in the label.
        """
        text = a0 if a0 is not None else ""
        super(SmartLabel, self).setText(text)
        self.setToolTip(text)

class NoClickLineEdit(QLineEdit):
    """
    A QLineEdit that does not allow user interaction, effectively making it a read-only text display.
    Inherits from QLineEdit and overrides mouse events to prevent editing.
    """
    def __init__(self, text: str = ""):
        super().__init__(text)
        self.setReadOnly(True)
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(50, 50, 50, 0.6);
                border: 1px solid rgb(100, 100, 100);
                border-radius: 4px;
                color: white;
                font-size: 16px;
            }
            QToolTip {
                background-color: rgb(30, 30, 30);
                border: 1px solid rgb(120, 120, 120);
                color: rgb(220, 220, 220);
                border-radius: 6px;
                font-size: 14px;
            }
        """)
        self.setMaximumWidth(80)
        self.setReadOnly(True)
        self.setToolTip(f"{text}")
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def mousePressEvent(self, event: QMouseEvent):
        event.ignore()  # Ignore mouse press events to prevent editing

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        event.ignore()  # Ignore double-click events to prevent editing

    def mouseReleaseEvent(self, event: QMouseEvent):
        event.ignore()  # Ignore mouse release events to prevent editing
    