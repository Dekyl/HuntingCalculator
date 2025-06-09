from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtCore import QSize

from typing import Any

from gui.manage_widgets import ManagerWidgets
from gui.dialogs_user import show_dialog_confirmation, show_dialog_results, show_dialog_error
from gui.side_bar_widget import SideBarWidget
from gui.home_widget import HomeWidget
from gui.view_sessions_widget import ViewSessionsWidget
from gui.settings_widget import SettingsWidget
from gui.new_session_widget import NewSessionWidget
from controller.app_controller import AppController

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the main window of the Hunting Calculator application.
        """
        super().__init__()

        self.setWindowIcon(QIcon("./res/icons/matchlock.ico"))

        self.setWindowTitle("Hunting Calculator")
        self.resize(QSize(1800, 1000))
        self.setMinimumSize(QSize(400, 300))
        
        primary_screen = QGuiApplication.primaryScreen()
        if primary_screen is not None:
            screen_geometry = primary_screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

        # Create a main layout and widget for the window
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.setCentralWidget(main_widget)

        # Create the AppController instance to manage the application logic
        # This controller will handle interactions between the view and the model
        AppController(self)

        # Create the left-side menu and add it to the main layout
        self.side_bar_widget = SideBarWidget(self)

        # Create the ManagerWidgets instance to manage different widgets in the application
        manager = ManagerWidgets()
        self.stack = manager.get_stack()

        # Add the left-side menu and the main stack to the main layout
        main_layout.addWidget(self.side_bar_widget)
        main_layout.addWidget(self.stack, stretch=1)

        page_widgets: dict[str, QWidget] = { "home": HomeWidget(),
                                             "view_sessions": ViewSessionsWidget(),
                                             "settings": SettingsWidget() }

        for name, widget in page_widgets.items():
            ManagerWidgets.get_instance().add_page(name, widget)

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

    def create_new_session_widget(self, name_spot: str, spot_id_icon: str, no_market_items:list[str], items: dict[str, tuple[str, int]], 
            elixirs: dict[str, tuple[str, int]], elixirs_cost: str):
        """
        Create a new session widget for the specified hunting spot.
            :param name_spot: The name of the hunting spot.
            :param spot_id_icon: The ID of the icon associated with the hunting spot.
            :param no_market_items: A list of items that are not available on the market.
            :param items: A dictionary containing the prices of items for the hunting spot.
            :param elixirs: A dictionary containing the names and costs of elixirs for the hunting spot.
            :param elixirs_cost: The cost of elixirs for the hunting spot.
        """
        self.actual_session = NewSessionWidget(name_spot, spot_id_icon, items, elixirs, no_market_items, elixirs_cost)

    def update_exchange_hides_results(self, exchange_results: tuple[int, int, int]):
        """
        Update the results of the exchange hides operation.
            :param exchange_results: A tuple containing the results of the exchange operation.
        """
        self.actual_session.update_session_exchange_results(exchange_results)

    def set_ui_enabled(self, enabled: bool):
        """
        Enable or disable the main UI components of the application.
            :param enabled: A boolean indicating whether to enable or disable the UI.
        """
        self.side_bar_widget.set_left_widget_buttons_enabled(enabled)
        self.side_bar_widget.setEnabled(enabled)
        self.stack.setEnabled(enabled)

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