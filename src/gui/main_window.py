from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtGui import QIcon, QGuiApplication
from PyQt6.QtCore import QSize

from typing import Any

from gui.create_widgets import CreateWidgets
from gui.manage_widgets import ManagerWidgets
from gui.dialogs_user import show_dialog_confirmation, show_dialog_results, show_dialog_error_api
from controller.app_controller import AppController

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the main window of the Hunting Calculator application.
        """
        super().__init__()

        self.setWindowIcon(QIcon("./res/icons/matchlock.ico"))

        self.setWindowTitle("Hunting Calculator")
        self.resize(QSize(1800, 900))
        self.setMinimumSize(QSize(400, 300))
        
        primary_screen = QGuiApplication.primaryScreen()
        if primary_screen is not None:
            screen_geometry = primary_screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
        self.setStyleSheet("""
            QWidget {
            background-color: rgb(30, 30, 30);
            }
        """)

        manager = ManagerWidgets()
        self.stack = manager.get_stack()

        # Create a main layout for the window
        container = QWidget()
        main_layout = QHBoxLayout()
        container.setLayout(main_layout)

        # Create the AppController instance to manage the application logic
        # This controller will handle interactions between the view and the model
        AppController(self)

        # Create the CreateWidgets instance to manage the creation of widgets
        # This class will handle the creation of all static widgets in the application
        self.create_widgets = CreateWidgets(self)

        # Create the left-side menu and add it to the main layout
        self.left_widget = self.create_widgets.create_side_bar()
        main_layout.addWidget(self.left_widget)

        # Add stack to the main layout to swap between different widgets
        main_layout.addWidget(self.stack, stretch=1)

        # Set the central widget of the main window
        self.setCentralWidget(container)
        # Create and add all static widgets to the manager
        self.create_widgets.create_all_widgets()

    def show_dialog_confirmation(self, message: str, action: Any, confirm_action: str = "exit") -> bool:
        """
        Show a confirmation dialog before executing an action.
            :param message: The confirmation message to display.
            :param action: The action to execute if confirmed.
            :param confirm_action: The action that was confirmed, used to set the icon.
        """
        return show_dialog_confirmation(message, action, confirm_action)
    
    def show_dialog_results(self, message: str, confirm_action: str = "clean_results"):
        """
        Show a message box with the results of an action.
            :param message: The message to display in the results dialog.
            :param confirm_action: The action that was confirmed, used to set the icon.
        """
        show_dialog_results(message, confirm_action)

    def create_new_session_widget(self, name_spot: str, prices: list[tuple[str, int]], elixir_costs: list[tuple[str, int]]):
        """
        Create a new session widget for the specified hunting spot.
            :param name_spot: The name of the hunting spot.
            :param prices: A list of tuples containing item names and their prices.
            :param elixir_costs: A list of tuples containing elixir names and their costs.
        """
        self.create_widgets.create_new_session_widget(name_spot, prices, elixir_costs)

    def update_exchange_results(self, exchange_results: tuple[int, int, int]):
        """
        Update the exchange results displayed in the application.
            :param exchange_results: A tuple containing the exchange results (total, profit, loss).
        """
        self.create_widgets.update_exchange_results(exchange_results)

    def set_ui_enabled(self, enabled: bool):
        """
        Enable or disable the main UI components of the application.
            :param enabled: A boolean indicating whether to enable or disable the UI.
        """
        self.left_widget.setEnabled(enabled)
        self.stack.setEnabled(enabled)

    def show_dialog_error_api(self):
        """
        Show a dialog box indicating an error occurred while retrieving data from the API.
        """
        show_dialog_error_api()

    def close_window(self):
        """
        Close the main window and exit the application.
        """
        self.close()
        QGuiApplication.quit()