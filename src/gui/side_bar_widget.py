import os
from typing import Callable, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QDialog, QMainWindow
from PySide6.QtGui import QFont, QIcon, QShortcut
from PySide6.QtCore import QSize, Qt

from gui.manage_widgets import ManagerWidgets
from gui.aux_components import QHLine
from controllers.app_controller import AppController
from config.config import res_abs_paths

class SideBarWidget(QWidget):
    """
    A widget that serves as a sidebar for the main application window.
    It contains buttons for navigation and actions such as home, new session, view sessions, clean sessions, settings, and exit.
    This class is a singleton and should be accessed via the get_instance method.
    """
    _instance = None  # Singleton instance of SideBarWidget

    def __init__(self, main_window: QMainWindow):
        """
        Initialize the SideBarWidget with a reference to the main application window.
            :param view: Implement of ViewInterface.
        """
        super().__init__()  # Initialize the QWidget
        
        if SideBarWidget._instance is not None:
            raise Exception("SideBarWidget is a singleton!")
        SideBarWidget._instance = self

        self.main_window = main_window

        self.controller = AppController.get_instance()
        self.button_icon_size = QSize(20, 20) # Default icon size for buttons

        left_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # As SideBarWidget is a customized QWidget, we need to set this attribute to apply styles
        self.setStyleSheet("""
            background-color: rgb(30, 30, 30);
            border: 2px solid rgb(120, 120, 120);
            border-radius: 8px;
        """)

        manager_widgets = ManagerWidgets.get_instance()
        buttons_side_bar: list[tuple[str, Callable[[QPushButton], None,], str]] = [
            ("Home", lambda _: manager_widgets.set_page("home"), "Ctrl+H"),
            ("New session", lambda btn: self.show_spots_list_widget(btn), "Ctrl+N"),
            ("View sessions", lambda _: self.controller.show_dialog_select_session_controller(), "Ctrl+A"),
            ("Clean sessions", lambda _: self.controller.clean_all_sessions_controller() if self.controller else None, "Ctrl+L"),
            ("Settings", lambda _: self.controller.create_settings_widget_controller() if self.controller else None, "Ctrl+G"),
            ("Exit", lambda _: self.controller.on_exit_button_controller() if self.controller else None, "Ctrl+Q")
        ]

        self.left_widget_buttons: dict[str, QPushButton] = {} # Store buttons for later use
        for i, (text, action, shortcut) in enumerate(buttons_side_bar):
            button_side_bar = QPushButton()
            text_low = text.lower().replace(' ', '_')
            self.left_widget_buttons[text_low] = button_side_bar
            
            if not os.path.exists(res_abs_paths[f"{text_low}_ico"]):
                button_side_bar.setIcon(QIcon(res_abs_paths["not_found_ico"]))
            else:
                button_side_bar.setIcon(QIcon(res_abs_paths[f"{text_low}_ico"])) # Set an icon based on the side bar button text

            button_side_bar.setIconSize(self.button_icon_size) # Set a default icon size
            button_side_bar.setStyleSheet("""
                QPushButton:enabled {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 6px;
                }
                QPushButton:disabled {
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
                    border-radius: 6px;
                    font-size: 14px;
                }
            """)
            button_side_bar.setToolTip(f"{text} ({shortcut})") # Add tooltip to display text on hover
            button_side_bar.setFont(QFont("Arial", 12))
            button_side_bar.setMinimumHeight(50)
            button_side_bar.setMinimumWidth(50)
            button_side_bar.clicked.connect(lambda _, b=button_side_bar, a=action: a(b)) # type: ignore
            left_layout.addWidget(button_side_bar)

            if i < len(buttons_side_bar) - 1:
                left_layout.addWidget(QHLine())
                
        # Add stretch to the bottom of the layout to push buttons to the top
        left_layout.addStretch()

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
    
    def show_spots_list_widget(self, button: QPushButton):
        """
        Display a list of buttons, each representing a spot. When a button is clicked,
        the new_session widget is opened for the selected spot.
            :param button: The button that triggered the dialog to show the spots list.
        """
        spots = self.controller.get_spots_list_controller() if self.controller else [] # Assume this method retrieves the list of spots

        if not spots:
            return # Exit if there is no 'spots' field

        # Create a dialog to hold the list of buttons
        spots_dialog = QDialog(self.main_window)
        spots_dialog.setStyleSheet("""
            QDialog {
                border: 2px solid rgb(120, 120, 120);
                border-radius: 10px;
                background-color: rgb(30, 30, 30);
            }
        """)
        spots_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        
        if button:
            button_geometry = button.geometry()
            button_position = button_geometry.topLeft()
            parent_geometry = self.main_window.geometry() if self.main_window else self.geometry()
            dialog_width = 200
            dialog_height = 320
            x = button_position.x() + parent_geometry.x() + button_geometry.width() + 25  # Position to the right of the button
            y = button_position.y() + parent_geometry.y() + 5
            spots_dialog.setGeometry(x, y, dialog_width, dialog_height)

        spots_layout = QVBoxLayout(spots_dialog)

        for i, spot in enumerate(spots):
            button = QPushButton(spot)
            button.setFont(QFont("Arial", 12))
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    border-radius: 6px;
                    color: rgb(220, 220, 220);
                    padding: 10px;
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
                    border-radius: 6px;
                    font-size: 14px;
                }              
            """)
            button.setToolTip(f"{spot} (Ctrl+{i+1})")  # Add tooltip to display spot name on hover
            button.setMinimumHeight(50)

            # Takes spot value the moment lambda is defined, not when button is clicked
            # This is necessary to avoid late binding issues in lambda functions
            # Calls open_new_session_for_spot with the selected spot when the button is clicked
            # Closes the dialog after opening the new session
            button.clicked.connect(lambda _, s=spot: (self.controller.select_new_session_controller(s), spots_dialog.accept())) # type: ignore

            # Create a keyboard shortcut for each button spot
            shortcut_view_sessions = QShortcut(f"Ctrl+{i+1}", spots_dialog)
            shortcut_view_sessions.activated.connect(button.click)
            
            spots_layout.addWidget(button)

        spots_dialog.exec()

    def get_left_widget_button(self, button_name: str) -> Optional[QPushButton]:
        """
        Get a button from the left-side menu by its name.
            :param button_name: The name of the button to retrieve.
            :return: The QPushButton instance corresponding to the given name.
        """
        return self.left_widget_buttons.get(button_name, None)

    @staticmethod
    def get_instance() -> "SideBarWidget":
        """
        Get the singleton instance of SideBarWidget.
            :return: The singleton instance of SideBarWidget.
        """
        if SideBarWidget._instance is None:
            raise Exception("SideBarWidget instance not created. Call SideBarWidget.")
        return SideBarWidget._instance