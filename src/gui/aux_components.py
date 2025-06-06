from PyQt6.QtWidgets import QFrame

class QHLine(QFrame):
    """
    A horizontal line widget that can be used to separate sections in a GUI.
    Inherits from QFrame and sets the frame shape to a horizontal line.
    """
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("background-color: 1px rgb(120, 120, 120);")

class QVLine(QFrame):
    """
    A vertical line widget that can be used to separate sections in a GUI.
    Inherits from QFrame and sets the frame shape to a vertical line.
    """
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("background-color: 1px rgb(120, 120, 120);")