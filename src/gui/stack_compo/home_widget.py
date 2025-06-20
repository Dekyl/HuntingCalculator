from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from gui.aux_components import NoClickLineEdit
from config.config import res_abs_paths

class HomeWidget(QWidget):
    """Widget that displays the home page with a background image and command shortcuts."""
    def __init__(self):
        """Widget that displays the home page with a background image and command shortcuts."""
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        self.setStyleSheet("""
            background-color: rgb(30, 30, 30);
        """)

        label = QLabel()
        label.setPixmap(QPixmap(res_abs_paths['home_background']))
        label.setScaledContents(True)
        label.setContentsMargins(0, 50, 0, 50)

        main_layout.addWidget(label)
        main_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        labels = [
            "Plan your hunts efficiently.",
            "Track your progress and results."
        ]

        for text in labels:
            label = QLabel(text)
            label.setStyleSheet("""
                font-size: 18px; 
                color: white;
            """)
            main_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignHCenter)

        commands = {
            "Home": "Ctrl + H",
            "New session": "Ctrl + N",
            "View sessions": "Ctrl + A",
            "Clean sessions": "Ctrl + L",
            "Settings": "Ctrl + G",
            "Exit": "Ctrl + Q"
        } 

        commands_widget = QWidget()
        commands_layout = QVBoxLayout(commands_widget)
        commands_layout.setSpacing(15)
        commands_widget.setStyleSheet("""
            background-color: transparent;
        """)

        shortcuts_widget = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_widget)
        shortcuts_layout.setSpacing(15)
        shortcuts_widget.setStyleSheet("""
            background-color: transparent;
        """)

        for command, shortcut in commands.items():
            command_label = QLabel(f"{command}:")
            command_label.setStyleSheet("""
                font-size: 16px;
                color: white;
            """)
            commands_layout.addWidget(command_label, 0, Qt.AlignmentFlag.AlignRight)

            shortcut_input = NoClickLineEdit(shortcut)
            shortcut_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            shortcuts_layout.addWidget(shortcut_input, 0, Qt.AlignmentFlag.AlignLeft)

        all_commands_widget = QWidget()
        all_commands_layout = QHBoxLayout(all_commands_widget)
        all_commands_layout.setContentsMargins(0, 50, 0, 0)

        all_commands_layout.addWidget(commands_widget, 0, Qt.AlignmentFlag.AlignRight)
        all_commands_layout.addWidget(shortcuts_widget, 0, Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(all_commands_widget)
        main_layout.addStretch()
            