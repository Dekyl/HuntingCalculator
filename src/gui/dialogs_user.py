from PyQt6.QtWidgets import QMessageBox, QCheckBox
from PyQt6.QtGui import QIcon

from typing import Any, Callable

def show_dialog_confirmation(message: str, action: Any, confirm_action: str = "exit") -> bool:
    """
    Show a confirmation dialog before executing an action.
        :param message: The confirmation message to display.
        :param action: The action to execute if confirmed.
        :param confirm_action: The action that was confirmed, used to set the icon.
    """
    msg_box = QMessageBox()
    if confirm_action == "exit":
        msg_box.setWindowIcon(QIcon("res/icons/exit_app.ico"))
    elif confirm_action == "clean_results":
        msg_box.setWindowIcon(QIcon("res/icons/clean_results.ico"))
    else:
        msg_box.setWindowIcon(QIcon("res/icons/not_found.ico"))

    msg_box.setWindowTitle("Confirm Action")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    checkbox = QCheckBox("Don't show this message again")
    checkbox.setText("Don't show this message again")
    msg_box.setStyleSheet("""
        QLabel {
            min-width: 300px;
            min-height: 100px;
            font-size: 14px;
        }
        QCheckBox {
            min-width: 300px;
            min-height: 30px;
            font-size: 14px;
        }
        QPushButton {
            min-width: 70px;
            min-height: 20px;
            font-size: 14px;
        }
    """)
    msg_box.setCheckBox(checkbox)

    reply = msg_box.exec()
    if reply == QMessageBox.StandardButton.Yes:
        if checkbox.isChecked():
            action()
            return False # Do not show the confirmation dialog again
        action()
    return True

def show_dialog_results(message: str, confirm_action: str, res: int):
    """
    Show a message box with the results of an action.
        :param message: The message to display in the results dialog.
        :param confirm_action: The action that was confirmed, used to set the icon.
        :param res: The result of the action, used to determine the icon type.
            -1 for error, 0 for success, 1 for no actions taken.
    """
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Results Action")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setStyleSheet("""
        QLabel {
            font-size: 14px;
        }
        QPushButton {
            min-width: 70px; 
            min-height: 20px; 
            font-size: 14px;
        }
    """)

    if res == -1:
        msg_box.setIcon(QMessageBox.Icon.Critical)
    elif res == 0:
        msg_box.setIcon(QMessageBox.Icon.Information)
    elif res == 1:
        msg_box.setIcon(QMessageBox.Icon.Question)

    confirm_actions: dict[str, Callable [[], None]] = {
        "clean_sessions": lambda: msg_box.setWindowIcon(QIcon("res/icons/clean_sessions.ico"))
    }
    confirm_actions[confirm_action]() if confirm_action in confirm_actions else msg_box.setWindowIcon(QIcon("res/icons/not_found.ico"))

    msg_box.exec()

def show_dialog_error(msg: str):
    """
    Show a dialog box indicating an error occurred while fetching data from the API.
        This function displays a message box with an error icon and a message indicating that there was an error fetching data from the API.
        :param msg: The error message to display.
    """
    dialog = QMessageBox()
    dialog.setWindowTitle("Error")
    dialog.setWindowIcon(QIcon("./res/icons/matchlock.ico"))
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setText(msg)
    dialog.setStyleSheet("""
        QLabel {
            font-size: 14px;
        }
        QPushButton {
            font-size: 14px;
        }
    """)
    dialog.addButton(QMessageBox.StandardButton.Ok)
    dialog.exec()