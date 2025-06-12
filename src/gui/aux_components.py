from PySide6.QtWidgets import QFrame, QLabel

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
    