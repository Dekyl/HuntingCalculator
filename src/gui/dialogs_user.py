from PyQt6.QtWidgets import QMessageBox, QCheckBox
from PyQt6.QtGui import QIcon

from typing import Any

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
    msg_box.setStyleSheet("QLabel{min-width: 200px; min-height: 100px;}")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    checkbox = QCheckBox("Don't show this message again")
    checkbox.setText("Don't show this message again")
    msg_box.setStyleSheet("""
        QLabel{min-width: 300px; min-height: 50px; font-size: 15px;}
        QCheckBox{min-width: 300px; min-height: 30px; font-size: 14px;}
        QPushButton{min-width: 70px; min-height: 20px; font-size: 14px;}
    """)
    msg_box.setCheckBox(checkbox)

    reply = msg_box.exec()
    if reply == QMessageBox.StandardButton.Yes:
        if checkbox.isChecked():
            action()
            return False # Do not show the confirmation dialog again
        action()
    return True

def show_dialog_results(message: str, confirm_action: str = "clean_results"):
    """
    Show a message box with the results of an action.
        :param message: The message to display in the results dialog.
        :param confirm_action: The action that was confirmed, used to set the icon.
    """
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Results Action")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg_box.setStyleSheet("""
        QLabel{min-width: 300px; min-height: 50px; font-size: 15px;}
        QPushButton{min-width: 70px; min-height: 20px; font-size: 14px;}
    """)
    
    if confirm_action == "clean_results":
        msg_box.setWindowIcon(QIcon("res/icons/clean_results.ico"))

    msg_box.exec()

def show_dialog_error_saving():
    """
    Show a dialog box indicating an error occurred while saving data.
        This function displays a message box with an error icon and a message indicating that there was an error saving data.
    """
    dialog = QMessageBox()
    dialog.setWindowTitle("Error")
    dialog.setWindowIcon(QIcon("./res/icons/matchlock.ico"))
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setText("Error saving data, wrong data")

    dialog.addButton(QMessageBox.StandardButton.Ok)

    dialog.exec()

def show_dialog_error_api():
    """
    Show a dialog box indicating an error occurred while fetching data from the API.
        This function displays a message box with an error icon and a message indicating that there was an error fetching data from the API.
    """
    dialog = QMessageBox()
    dialog.setWindowTitle("Error")
    dialog.setWindowIcon(QIcon("./res/icons/matchlock.ico"))
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setText("Error fetching data from API, please wait a little before trying again.")

    dialog.addButton(QMessageBox.StandardButton.Ok)

    dialog.exec()