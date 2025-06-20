from typing import Any, Callable

from PySide6.QtWidgets import QMessageBox, QCheckBox, QFileDialog
from PySide6.QtGui import QIcon

from config.config import saved_sessions_folder, res_abs_paths

def show_dialog_confirmation(message: str, action: Any, confirm_action: str = "exit") -> bool:
    """
    Show a confirmation dialog before executing an action.
        :param message: The confirmation message to display.
        :param action: The action to execute if confirmed.
        :param confirm_action: The action that was confirmed, used to set the icon.
    """
    msg_box = QMessageBox()
    if confirm_action == "exit":
        msg_box.setWindowIcon(QIcon(res_abs_paths["exit_ico"]))
    elif confirm_action == "clean_sessions":
        msg_box.setWindowIcon(QIcon(res_abs_paths["clean_sessions_ico"]))
    else:
        msg_box.setWindowIcon(QIcon(res_abs_paths["not_found_ico"]))

    msg_box.setWindowTitle("Confirm Action")
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    checkbox = QCheckBox("Don't show this message again")
    checkbox.setText("Don't show this message again")
    msg_box.setStyleSheet("""
        QLabel {
            min-width: 300px;
            min-height: 50px;
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

def show_dialog_type(msg: str, title: str, type: str = "info", action: str = "no_action"):
    """
    Show a dialog with a specific type of message.
        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param type: The type of message, can be "error", "warning", "question", or "info".
        :param action: The action that triggered the dialog, used to set the icon.
    """
    dialog = QMessageBox()

    dialog.setWindowTitle(title)
    if type == "error":
        dialog.setIcon(QMessageBox.Icon.Critical)
    elif type == "warning":
        dialog.setIcon(QMessageBox.Icon.Warning)
    elif type == "question":
        dialog.setIcon(QMessageBox.Icon.Question)
    else:
        dialog.setIcon(QMessageBox.Icon.Information)

    dialog.setWindowIcon(QIcon(res_abs_paths["matchlock_ico"]))

    actions: dict[str, Callable [[], None]] = {
        "clean_sessions": lambda: dialog.setWindowIcon(QIcon(res_abs_paths["clean_sessions_ico"])),
        "no_action": lambda: dialog.setWindowIcon(QIcon(res_abs_paths["matchlock_ico"]))
    }
    actions[action]() if action in actions else dialog.setWindowIcon(QIcon(res_abs_paths["not_found_ico"]))

    dialog.setText(msg)
    dialog.setStyleSheet("""
        QLabel {
            padding: 5px;
            font-size: 14px;
        }
        QPushButton {
            min-width: 70px; 
            min-height: 20px;
            font-size: 14px;
        }
    """)
    dialog.addButton(QMessageBox.StandardButton.Ok)
    dialog.exec()

def show_dialog_view_session() -> str:
    """
    Show a dialog to choose a file.
        This function opens a file dialog to allow the user to select a file.
        :return: The selected file path or an empty string if no file was selected.
    """
    options = QFileDialog.Option(0)
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Select Session",
        saved_sessions_folder,
        "XLSX (*.xlsx)",
        options=options
    )

    return file_path if file_path else ""