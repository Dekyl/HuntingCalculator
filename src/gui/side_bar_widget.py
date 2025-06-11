import os
from typing import Callable

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QDialog, QMainWindow
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QTimer, QSize, Qt

from gui.manage_widgets import ManagerWidgets
from gui.settings_widget import SettingsWidget
from gui.aux_components import QHLine
from controller.app_controller import AppController

class SideBarWidget(QWidget):
    """
    A widget that serves as a sidebar for the main application window.
    It contains buttons for navigation and actions such as home, new session, view sessions, clean sessions, settings, and exit.
    This class is a singleton and should be accessed via the get_instance method.
    """
    _instance = None  # Singleton instance of SideBarWidget

    def __init__(self, view: QMainWindow | None = None):
        """
        Initialize the SideBarWidget with a reference to the main application window.
            :param view: The QMainWindow instance that this sidebar will be associated with."""
        # If view is None, raise an error
        if view is None:
            raise ValueError("View must be a QMainWindow instance.")
        # Ensure the view is a QMainWindow instance
        if SideBarWidget._instance is not None:
            raise Exception("This class is a singleton!")
        SideBarWidget._instance = self

        super().__init__()  # Initialize the QWidget

        self.parent_window = view  # Parent QMainWindow for the widgets
        self.controller = AppController.get_instance()
        self.button_icon_size = QSize(20, 20) # Default icon size for buttons
        self.res_icons = {
            "home": "res/icons/home.ico",
            "new session": "res/icons/new_session.ico",
            "view sessions": "res/icons/view_sessions.ico",
            "clean sessions": "res/icons/clean_sessions.ico",
            "settings": "res/icons/settings.ico",
            "exit": "res/icons/exit_app.ico"
        }

        left_layout = QVBoxLayout(self)
        self.setContentsMargins(0, 0, 5, 0) # Sidebar margin with the main window
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # As SideBarWidget is a customized QWidget, we need to set this attribute to apply styles
        self.setStyleSheet("""
            background-color: rgb(30, 30, 30);
            border-right: 2px solid rgb(120, 120, 120);
        """)

        self.manager_widgets = ManagerWidgets.get_instance()
        buttons_side_bar: list[tuple[str, Callable[..., None]]] = [
            ("Home", lambda: self.manager_widgets.set_page("home")),
            ("New session", lambda: self.show_spots_list_widget()),
            ("View sessions", lambda: self.manager_widgets.set_page("view_sessions")),
            ("Clean sessions", lambda: self.controller.on_clean_sessions_button() if self.controller else None),
            ("Settings", lambda: self.create_settings_widget()),
            ("Exit", lambda: self.controller.on_exit_button() if self.controller else None)
        ]

        self.left_widget_buttons: dict[str, QPushButton] = {} # Store buttons for later use
        for i, (text, action) in enumerate(buttons_side_bar):
            button_side_bar = QPushButton()
            self.left_widget_buttons[text.lower().replace(' ', '_')] = button_side_bar
            if not os.path.exists(self.res_icons[text.lower()]):
                button_side_bar.setIcon(QIcon("res/icons/not_found.ico"))
            else:
                button_side_bar.setIcon(QIcon(self.res_icons[text.lower()])) # Set an icon based on the side bar button text

            button_side_bar.setIconSize(self.button_icon_size) # Set a default icon size
            button_side_bar.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.7);
                }
                QToolTip {
                    background-color: rgb(30, 30, 30);;
                    border: 1px solid rgb(120, 120, 120);
                    border-radius: 3px;
                }
            """)
            button_side_bar.setToolTip(f"{text}") # Add tooltip to display text on hover
            button_side_bar.setFont(QFont("Arial", 12))
            button_side_bar.setMinimumHeight(50)
            button_side_bar.setMinimumWidth(50)
            button_side_bar.clicked.connect(action) # type: ignore
            left_layout.addWidget(button_side_bar)

            if i < len(buttons_side_bar) - 1:
                left_layout.addWidget(QHLine())
                
        # Add stretch to the bottom of the layout to push buttons to the top
        left_layout.addStretch()

    def create_settings_widget(self):
        """
        Create and display the settings widget in the manager widgets.
        This method initializes the SettingsWidget and adds it to the manager widgets.
        """
        self.manager_widgets.add_page("settings", SettingsWidget())  # Add the settings widget to the manager
        self.manager_widgets.set_page("settings")  # Switch to the settings page

    def set_left_widget_buttons_enabled(self, enabled: bool):
        """
        Set the enabled state of all buttons in the left-side menu.
            :param enabled: True to enable all buttons, False to disable them.
        """
        for name in self.left_widget_buttons.keys():
            self.set_left_widget_button_enabled(name, enabled)

    def set_left_widget_button_enabled(self, button_name: str, enabled: bool):
        """
        Set the enabled state of a button in the left-side menu.
            :param button_name: The name of the button to enable or disable.
            :param enabled: True to enable the button, False to disable it.
        """
        self.left_widget_buttons[button_name].setEnabled(enabled)
        if enabled:
            self.left_widget_buttons[button_name].setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.7);
                }
                QToolTip {
                    background-color: rgb(30, 30, 30);;
                    border: 1px solid rgb(120, 120, 120);
                    border-radius: 3px;
                }
            """)
        else:
            self.left_widget_buttons[button_name].setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.7);
                }
                QToolTip {
                    background-color: rgb(30, 30, 30);;
                    border: 1px solid rgb(120, 120, 120);
                    border-radius: 3px;
                }
            """)
        if not enabled:
            QTimer.singleShot(75000, lambda: self.set_left_widget_button_enabled(button_name, True))  # type: ignore
    
    def show_spots_list_widget(self):
        """
        Display a list of buttons, each representing a spot. When a button is clicked,
        the new_session widget is opened for the selected spot.
        """
        spots = self.controller.get_spots_list() if self.controller else [] # Assume this method retrieves the list of spots

        if not spots:
            return # Exit if there are no spots available

        # Create a widget to hold the list of buttons
        spots_dialog = QDialog(self.parent_window)
        spots_dialog.setStyleSheet("""
            QDialog {
                border: 2px solid rgb(120, 120, 120);
                border-radius: 10px;
                background-color: rgb(30, 30, 30);
            }
        """)
        spots_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        # Center the dialog on the parent window
        button = self.parent_window.sender()  # Get the button that triggered the dialog
        if button is not None:
            if isinstance(button, QWidget):
                button_geometry = button.geometry()
            else:
                return  # Exit if the sender is not a QWidget
            button = button_geometry.topLeft()
            parent_geometry = self.parent_window.geometry()
            dialog_width = 200
            dialog_height = 280
            x = button.x() + parent_geometry.x() + button_geometry.width() + 25  # Position to the right of the button
            y = button.y() + parent_geometry.y() + 5
            spots_dialog.setGeometry(x, y, dialog_width, dialog_height)

        spots_layout = QVBoxLayout(spots_dialog)

        for spot in spots:
            button = QPushButton(spot)
            button.setFont(QFont("Arial", 12))
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 6px;
                    color: rgb(220, 220, 220);
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.7);
                }
            """)
            button.setMinimumHeight(50)

            # Takes spot value the moment lambda is defined, not when button is clicked
            # This is necessary to avoid late binding issues in lambda functions
            # Calls open_new_session_for_spot with the selected spot when the button is clicked
            # Closes the dialog after opening the new session
            button.clicked.connect(lambda _, s=spot: (AppController.get_instance().select_new_session(s), spots_dialog.accept()))  # type: ignore
            spots_layout.addWidget(button)

        spots_dialog.exec()

    @staticmethod
    def get_instance() -> "SideBarWidget":
        """
        Get the singleton instance of SideBarWidget.
            :return: The singleton instance of SideBarWidget.
        """
        if SideBarWidget._instance is None:
            raise Exception("SideBarWidget instance not created. Call SideBarWidget.")
        return SideBarWidget._instance