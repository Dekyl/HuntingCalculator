from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class SessionResults(QWidget):
    """
    A widget that displays the results of the session, including total, total per hour, total taxed and total taxed per hour.
    """
    def __init__(self, default_font: QFont, results_default_style: str):
        """ Initialize the SessionResults widget.
            :param default_font: The default font to be used for the labels and input fields.
            :param results_default_style: The default style to be applied to the input fields.
        """
        super().__init__()

        results_layout = QGridLayout(self)
        self.setMaximumHeight(150)
        
        self.labels_result = [
            QLabel("Total"), 
            QLabel("Total/h"), 
            QLabel("Total Taxed"), 
            QLabel("Total Taxed/h")
        ]

        self.inputs_result: list[QLineEdit] = []

        for i in range(len(self.labels_result)):
            self.inputs_result.append(QLineEdit("0"))
            self.labels_result[i].setFont(default_font)
            self.inputs_result[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_result[i].setMinimumHeight(26)
            self.inputs_result[i].setFont(default_font)
            self.inputs_result[i].setStyleSheet(results_default_style)
            self.inputs_result[i].setReadOnly(True)

            results_layout.addWidget(self.labels_result[i], 0, i, Qt.AlignmentFlag.AlignBottom)
            results_layout.addWidget(self.inputs_result[i], 1, i, Qt.AlignmentFlag.AlignTop)

    def get_labels_result(self) -> list[QLabel]:
        """
        Get the labels that display the results of the session.
            :return: A list of QLabel widgets containing the results labels.
        """
        return self.labels_result

    def get_input_results(self) -> list[QLineEdit]:
        """
        Get the input fields that display the results of the session.
            :return: A list of QLineEdit widgets containing the results.
        """
        return self.inputs_result