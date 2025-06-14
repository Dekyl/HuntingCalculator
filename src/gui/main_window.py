from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtGui import QIcon, QGuiApplication, QShortcut
from PySide6.QtCore import QSize

from typing import Any

from gui.manage_widgets import ManagerWidgets
from gui.side_bar_widget import SideBarWidget
from gui.settings_widget import SettingsWidget
from gui.home_widget import HomeWidget
from gui.view_sessions_widget import ViewSessionsWidget
from gui.new_session_widget import NewSessionWidget
from gui.dialogs_user import show_dialog_error, show_dialog_confirmation, show_dialog_results
from controller.app_controller import AppController

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the main window of the Hunting Calculator application.
        """
        super().__init__()

        self.setWindowIcon(QIcon("./res/icons/matchlock.ico"))
        self.setWindowTitle("Hunting Calculator")
        self.resize(QSize(1800, 1020))
        self.setMinimumSize(QSize(400, 300))
        
        primary_screen = QGuiApplication.primaryScreen()
        if primary_screen:
            screen_geometry = primary_screen.availableGeometry()  # Use availableGeometry so the taskbar is not included
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

        # Create a main layout and widget for the window
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(main_widget)

        # Create the ManagerWidgets instance to manage different widgets in the application
        self.manager = ManagerWidgets()

        # Create the AppController instance to manage the application logic
        # This controller will handle interactions between the view and the model
        self.controller = AppController(self)

        # Create the left-side menu and add it to the main layout
        self.side_bar_widget = SideBarWidget(self)

        stack = self.manager.get_stack()

        # Add the left-side menu and the main stack to the main layout
        main_layout.addWidget(self.side_bar_widget)
        main_layout.addWidget(stack, stretch=1)

        page_widgets: dict[str, QWidget] = { "home": HomeWidget(),
                                             "view_sessions": ViewSessionsWidget(),
                                            }

        for name, widget in page_widgets.items():
            self.manager.add_page(name, widget)

        self.create_shortcuts()

    def create_shortcuts(self):
        """
        Create keyboard shortcuts for various actions in the application.
        """
        shortcut_home = QShortcut("Ctrl+H", self)
        shortcut_home.activated.connect(lambda: self.manager.set_page("home"))

        shortcut_new_session = QShortcut("Ctrl+N", self)
        new_session_button = self.side_bar_widget.get_left_widget_button("new_session")
        shortcut_new_session.activated.connect(new_session_button.click if new_session_button else None)

        shortcut_view_sessions = QShortcut("Ctrl+A", self)
        shortcut_view_sessions.activated.connect(lambda: self.manager.set_page("view_sessions"))

        shortcut_clean_sessions = QShortcut("Ctrl+L", self)
        shortcut_clean_sessions.activated.connect(lambda: self.controller.on_clean_sessions_button() if self.controller else None)

        shortcut_settings = QShortcut("Ctrl+G", self)
        shortcut_settings.activated.connect(lambda: self.create_settings_widget())

        shortcut_exit = QShortcut("Ctrl+Q", self)
        shortcut_exit.activated.connect(self.close_window)

    def show_dialog_confirmation(self, message: str, action: Any, confirm_action: str = "exit") -> bool:
        """
        Show a confirmation dialog before executing an action.
            :param message: The confirmation message to display.
            :param action: The action to execute if confirmed.
            :param confirm_action: The action that was confirmed, used to set the icon.
        """
        return show_dialog_confirmation(message, action, confirm_action)
    
    def show_dialog_results(self, message: str, confirm_action: str, res: int):
        """
        Show a message box with the results of an action.
            :param message: The message to display in the results dialog.
            :param confirm_action: The action that was confirmed, used to set the icon.
            :param res: The result of the action, used to determine the icon and message.
        """
        show_dialog_results(message, confirm_action, res)

    def update_exchange_hides_results(self, exchange_results: tuple[int, int, int]):
        """
        Update the results of the exchange hides operation.
            :param exchange_results: A tuple containing the results of the exchange operation.
        """
        self.actual_session.update_session_exchange_results(exchange_results)

    def create_new_session_widget(self, name_spot: str, value_pack: bool, market_tax: float, extra_profit: bool, spot_id_icon: str, no_market_items:list[str], items: dict[str, tuple[str, int]], elixirs_cost: str):
        """
        Create a new session widget for the specified hunting spot.
            :param name_spot: The name of the hunting spot.
            :param value_pack: A boolean indicating whether the value pack is active.
            :param market_tax: The market tax rate for the hunting spot.
            :param extra_profit: Extra profit percentage applied or not.
            :param spot_id_icon: The ID of the icon associated with the hunting spot.
            :param no_market_items: A list of items that are not available on the market.
            :param items: A dictionary containing the prices of items for the hunting spot.
            :param elixirs_cost: The cost of elixirs for the hunting spot.
        """
        self.actual_session = NewSessionWidget(name_spot, value_pack, market_tax, extra_profit, spot_id_icon, items, no_market_items, elixirs_cost)

    def create_settings_widget(self):
        """
        Create and display the settings widget in the application.
        This method initializes the settings widget and adds it to the manager.
        """
        self.manager.add_page("settings", SettingsWidget())  # Add the settings widget to the manager
        self.manager.set_page("settings")  # Switch to the settings page
       
    def set_ui_enabled(self, enabled: bool):
        """
        Enable or disable the main UI components of the application.
            :param enabled: A boolean indicating whether to enable or disable the UI.
        """
        self.side_bar_widget.set_left_widget_buttons_enabled(enabled)

    def show_dialog_error(self, msg: str):
        """
        Show an error dialog with the specified message.
            :param msg: The error message to display.
        """
        show_dialog_error(msg)

    def set_session_button_enabled(self, enabled: bool):
        """
        Enable or disable the session button in the left-side menu.
            :param enabled: A boolean indicating whether to enable or disable the new session button.
        """
        self.side_bar_widget.set_left_widget_button_enabled("new_session", enabled)

    def close_window(self):
        """
        Close the main window and exit the application.
        """
        self.close()
        QGuiApplication.quit()