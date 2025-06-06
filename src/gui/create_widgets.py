import os
from typing import Callable

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMainWindow, QHBoxLayout, QLabel, QGridLayout, QLineEdit
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QDialog

from gui.manage_widgets import ManagerWidgets
from gui.dialogs_user import show_dialog_error_saving
from gui.aux_components import QHLine
from controller.app_controller import AppController

class CreateWidgets:
    """
    A class to create various widgets for the application.
    This class provides methods to create main, check result, settings, and new session widgets.
    """
    _instance = None  # Singleton instance of CreateWidgets

    def __init__(self, view: QMainWindow | None = None):
        """
        Initialize the CreateWidgets instance.
            :param view: The main window of the application, should be a QMainWindow instance.
        """
        # If view is None, raise an error
        if view is None:
            raise ValueError("View must be a QMainWindow instance.")
        # Ensure the view is a QMainWindow instance
        if CreateWidgets._instance is not None:
            raise Exception("This class is a singleton!")
        CreateWidgets._instance = self

        self.button_icon_size = QSize(20, 20) # Default icon size for buttons
        self.parent = view  # Parent QMainWindow for the widgets
        self.controller = AppController.get_instance()
        self.res_icons = {
            "home": "res/icons/home.ico",
            "new session": "res/icons/new_session.ico",
            "view results": "res/icons/view_results.ico",
            "clean results": "res/icons/clean_results.ico",
            "settings": "res/icons/settings.ico",
            "exit": "res/icons/exit_app.ico"
        }

    def create_home_widget(self) -> QWidget:
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: rgb(30, 30, 30);")
        
        return main_widget

    def create_check_result_widget(self) -> QWidget:
        check_result_widget = QWidget()
        check_result_layout = QVBoxLayout()
        check_result_widget.setLayout(check_result_layout)
        check_result_widget.setStyleSheet("background-color: rgb(30, 30, 30);")

        return check_result_widget

    def create_settings_widget(self) -> QWidget:
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_widget.setLayout(settings_layout)
        settings_widget.setStyleSheet("background-color: rgb(30, 30, 30);")

        return settings_widget

    def create_new_session_widget(self, name_spot: str, prices: list[tuple[str, int]], elixir_costs: list[tuple[str, int]]):
        """
        Create the new session widget.
            :param name_spot: The name of the hunting spot for the new session.
            :param prices: A dictionary containing the prices of items for the new session.
            :param elixir_costs: A dictionary containing the costs of elixirs for the new session.
        """
        # Main widget and layout
        new_session_widget = QWidget()
        new_session_layout = QVBoxLayout()
        new_session_widget.setLayout(new_session_layout)
        new_session_widget.setStyleSheet("background-color: rgb(90,146,0); color: black;")

        # Session title widget and layout
        title_widget = QWidget()
        title_layout = QHBoxLayout()

        title_widget.setLayout(title_layout)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_widget.setMaximumHeight(80)
        title_widget.setContentsMargins(0, 30, 0, 0)

        hunting_zone = QLabel(name_spot)
        hunting_zone.setFont(QFont("Arial", 24))
        title_layout.addWidget(hunting_zone)

        # Inputs, exchange and results fields
        inputs_widget = QWidget()
        inputs_layout = QGridLayout()
        inputs_widget.setLayout(inputs_layout)

        exchange_widget = QWidget()
        exchange_widget.setMaximumHeight(70)
        exchange_layout = QGridLayout()
        exchange_widget.setLayout(exchange_layout)

        exchange_results_widget = QWidget()
        exchange_results_widget.setMaximumHeight(70)
        exchange_results_layout = QGridLayout()
        exchange_results_widget.setLayout(exchange_results_layout)

        results_widget = QWidget()
        results_widget.setMaximumHeight(150)
        results_layout = QGridLayout()
        results_widget.setLayout(results_layout)

        font = QFont('Arial', 14)

        # Button to save data in an excel file
        self.save_button = QPushButton("Save")
        self.save_button.setFont(font)
        self.save_button.setStyleSheet("""
            QPushButton{
                background-color: rgba(255,255,255,0.2); 
                border: 1px solid black; 
                border-radius: 6px
            }
            QPushButton:hover{
                background-color: rgba(255,255,255,0.5);
            }"""
        )
        
        self.save_button.setDisabled(True)
        self.save_button.setFixedSize(250, 50)
        self.save_button.clicked.connect(self.save_excel) # type: ignore
        save_but_widget = QWidget()
        save_but_widget.setFixedHeight(100)
        save_but_lay = QHBoxLayout()

        save_but_widget.setLayout(save_but_lay)
        save_but_widget.setContentsMargins(0, 0, 0, 100)
        save_but_lay.addWidget(self.save_button, alignment= Qt.AlignmentFlag.AlignCenter)

        # Adds the previous widgets to the main layout
        new_session_layout.addWidget(title_widget)
        new_session_layout.addWidget(inputs_widget)
        new_session_layout.addWidget(exchange_widget)
        new_session_layout.addWidget(exchange_results_widget)
        new_session_layout.addWidget(results_widget)
        new_session_layout.addWidget(save_but_widget)

        self.labels_input: list[QLabel] = []
        price_values: list[QLabel] = []

        for item_name, price_value in prices:
            self.labels_input.append(QLabel(f"{item_name} (0.00%)"))
            price_value = QLabel(str(f"{price_value:,}"))
            price_value.setFont(font)
            price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            price_value.setMaximumHeight(20)
            price_values.append(price_value)
        self.labels_input.append(QLabel("Hours"))

        # Data input fields
        self.inputs_input: list[QLineEdit] = []
        # Column where to place next element
        col = 0
        # Stylesheet used in all textfields
        style = "background-color: rgba(255,255,255,0.2); border: 1px solid black; border-radius: 4px"

        for i in range(len(self.labels_input)):
            self.inputs_input.append(QLineEdit())
            self.labels_input[i].setFont(font)
            self.inputs_input[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_input[i].setMinimumHeight(30)
            self.inputs_input[i].setStyleSheet(style)
            # Connects each input with result outputs fields
            self.inputs_input[i].textChanged.connect(self.update_data) # type: ignore

            if i < 7:
                inputs_layout.addWidget(self.labels_input[i], 0, col, Qt.AlignmentFlag.AlignBottom)
                if i < len(price_values):
                    inputs_layout.addWidget(price_values[i], 1, col)
                inputs_layout.addWidget(self.inputs_input[i], 2, col, Qt.AlignmentFlag.AlignTop)
            elif i < 14:
                inputs_layout.addWidget(self.labels_input[i], 3, col, Qt.AlignmentFlag.AlignBottom)
                if i < len(price_values):
                    inputs_layout.addWidget(price_values[i], 4, col)
                inputs_layout.addWidget(self.inputs_input[i], 5, col, Qt.AlignmentFlag.AlignTop)
            elif i < 21:
                inputs_layout.addWidget(self.labels_input[i], 6, col, Qt.AlignmentFlag.AlignBottom)
                if i < 19:
                    if i < len(price_values):
                        inputs_layout.addWidget(price_values[i], 7, col)
                inputs_layout.addWidget(self.inputs_input[i], 8, col, Qt.AlignmentFlag.AlignTop)
            else:
                inputs_layout.addWidget(self.labels_input[i], 9, col, Qt.AlignmentFlag.AlignBottom)
                inputs_layout.addWidget(self.inputs_input[i], 11, col, Qt.AlignmentFlag.AlignTop)
            
            col +=1
            if col == 7:
                col = 0

        # Exchange hides section
        green_exchange = QLabel("Green Hides Exchange")
        exchange_layout.addWidget(green_exchange, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        green_exchange.setFont(font)
        green_exchange.setContentsMargins(0, 0, 25, 0)

        blue_exchange = QLabel("Blue Hides Exchange")
        exchange_layout.addWidget(blue_exchange, 0, 1, Qt.AlignmentFlag.AlignBottom)
        blue_exchange.setFont(font)
        blue_exchange.setContentsMargins(25, 0, 0, 0)

        green_exchange_input = QLineEdit()
        green_exchange_input.setFont(font)
        green_exchange_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        green_exchange_input.setMinimumHeight(30)
        green_exchange_input.setStyleSheet(style)
        green_exchange_input.setMinimumWidth(220)
        green_exchange_input.setContentsMargins(0, 0, 25, 0)
        
        blue_exchange_input = QLineEdit()
        blue_exchange_input.setFont(font)
        blue_exchange_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blue_exchange_input.setMinimumHeight(30)
        blue_exchange_input.setStyleSheet(style)
        blue_exchange_input.setMinimumWidth(220)
        blue_exchange_input.setContentsMargins(25, 0, 0, 0)

        # Connects each input field with the function that resolves the request
        green_exchange_input.textChanged.connect(lambda: self.controller.on_exchange_hides(green_exchange_input.text(), blue_exchange_input.text())) # type: ignore
        blue_exchange_input.textChanged.connect(lambda: self.controller.on_exchange_hides(green_exchange_input.text(), blue_exchange_input.text())) # type: ignore

        exchange_layout.addWidget(green_exchange_input, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        exchange_layout.addWidget(blue_exchange_input, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        results_exchange = QLabel("Results Exchange")
        results_exchange.setFont(font)
        exchange_results_layout.addWidget(results_exchange, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        
        self.exchange_results_input = QLineEdit()
        self.exchange_results_input.setReadOnly(True)
        self.exchange_results_input.setFont(font)
        self.exchange_results_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exchange_results_input.setMinimumHeight(30)
        self.exchange_results_input.setStyleSheet("background-color: rgba(255,255,255,0.2); border: 1px solid black; border-radius: 4px")
        self.exchange_results_input.setMaximumWidth(220)
        exchange_results_layout.addWidget(self.exchange_results_input, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.labels_result = [
            QLabel("Total Money"), 
            QLabel("Total Money/h"), 
            QLabel("Total Taxed"), 
            QLabel("Total Profit/h")
        ]
        
        self.inputs_result: list[QLineEdit] = []

        for i in range(len(self.labels_result)):
            self.inputs_result.append(QLineEdit())
            self.labels_result[i].setFont(font)
            self.inputs_result[i].setFont(font)
            self.inputs_result[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_result[i].setMinimumHeight(30)
            self.inputs_result[i].setStyleSheet(style)
            self.inputs_result[i].setReadOnly(True)

            results_layout.addWidget(self.labels_result[i], 2, i, Qt.AlignmentFlag.AlignBottom)
            results_layout.addWidget(self.inputs_result[i], 3, i, Qt.AlignmentFlag.AlignTop)

        ManagerWidgets.get_instance().add_page("new_session", new_session_widget)
        ManagerWidgets.get_instance().set_page("new_session")

    def update_exchange_results(self, res_exchange: tuple[int, int, int]):
        """
        Update the exchange results input field with the provided results.
            :param res_exchange: A tuple containing the exchange results (total, green hides, blue hides).
        """
        self.exchange_results_input.setText(f"{res_exchange[0]} ({res_exchange[1]}, {res_exchange[2]})")

    def update_results(self):
        """
        Update the results input fields with the calculated results.
        This method retrieves the total money, total money per hour, total taxed, and total profit per hour,
        and updates the corresponding input fields with these values.
        """
        self.inputs_result[0].setText(str(f"{self.results_tot:,}"))
        self.inputs_result[1].setText(str(f"{self.results_tot_h:,}"))
        self.inputs_result[2].setText(str(f"{self.results_tax:,}"))
        self.inputs_result[3].setText(str(f"{self.results_tax_h:,}"))

    def save_excel(self):
        """
        Save the current session data to an Excel file.
        This method collects the input data, results, and labels, and saves them to an Excel file.
        If an error occurs during the saving process, it displays an error message dialog.
        """
        labels_res: list[str] = []

        for i in range(len(self.labels_result)):
            labels_res.append(self.labels_result[i].text())

        if self.controller.save_results(self.labels_input_text, self.data_input, labels_res, self.results_tot, self.results_tot_h, self.results_tax, self.results_tax_h) == -1:
            show_dialog_error_saving()
        
    def update_data(self):
        self.labels_input_text: list[str] = []
        self.data_input: list[str] = []

        for i in range(len(self.inputs_input)):
            self.labels_input_text.append(self.labels_input[i].text())
            self.data_input.append(self.inputs_input[i].text())

        res_data = self.controller.get_results(self.data_input)
        self.results_tot = res_data["results_tot"]
        self.results_tot_h = res_data["results_h"]
        self.results_tax = res_data["results_taxed"]
        self.results_tax_h = res_data["results_taxed_h"]

        gains_per_item = self.controller.get_gains_per_item()
        results_tot_percentage = self.controller.get_results_tot_percentage()

        for i in range(len(self.labels_input)-1):
            new_label_text = self.controller.get_percentage_item(self.labels_input[i].text(), gains_per_item[i], results_tot_percentage)
            self.labels_input_text[i] = new_label_text
            self.labels_input[i].setText(new_label_text)

        self.save_button.setDisabled(False)
        #self.show_results()

    def create_all_widgets(self):
        """
        Create all necessary widgets and add them to the ManagerWidgets instance.
        This method initializes the home widget, check result widget, settings widget,
        """
        widgets = { "home": self.create_home_widget(),
                    "view_results": self.create_check_result_widget(),
                    "settings": self.create_settings_widget() }

        for name, widget in widgets.items():
            ManagerWidgets.get_instance().add_page(name, widget)

    def show_spots_list_widget(self):
        """
        Display a list of buttons, each representing a spot. When a button is clicked,
        the new_session widget is opened for the selected spot.
        """
        spots = self.controller.get_spots_list() if self.controller else [] # Assume this method retrieves the list of spots

        if not spots:
            return # Exit if there are no spots available

        # Create a widget to hold the list of buttons
        spots_dialog = QDialog(self.parent)
        spots_dialog.setStyleSheet("""
            QDialog {
            border: 2px solid rgb(120, 120, 120);
            border-radius: 10px;
            background-color: rgb(30, 30, 30);
            }
        """)
        spots_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        # Center the dialog on the parent window
        button = self.parent.sender()  # Get the button that triggered the dialog
        if button is not None:
            if isinstance(button, QWidget):
                button_geometry = button.geometry()
            else:
                return  # Exit if the sender is not a QWidget
            button = button_geometry.topLeft()
            parent_geometry = self.parent.geometry()
            dialog_width = 200
            dialog_height = 350
            x = button.x() + parent_geometry.x() + button_geometry.width() + 25  # Position to the right of the button
            y = button.y() + parent_geometry.y() + 5
            spots_dialog.setGeometry(x, y, dialog_width, dialog_height)

        spots_layout = QVBoxLayout(spots_dialog)
        spots_dialog.setLayout(spots_layout)

        for spot in spots:
            button = QPushButton(spot)
            button.setFont(QFont("Arial", 12))
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid black;
                    border-radius: 6px;
                    color: white;
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
    
    def create_side_bar(self) -> QWidget:
        """
        Create the left-side menu bar with buttons for navigation.
            :return: The left-side menu widget.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(200)
        left_widget.setStyleSheet("""
            background-color: rgb(30, 30, 30);
            border-right: 1px solid rgb(120, 120, 120);
        """)

        buttons: list[tuple[str, Callable[..., None]]] = [
            ("Home", lambda: ManagerWidgets.get_instance().set_page("home")),
            ("New session", lambda: self.show_spots_list_widget()),
            ("View results", lambda: ManagerWidgets.get_instance().set_page("view_results")),
            ("Clean results", lambda: self.controller.on_clean_results_button() if self.controller else None),
            ("Settings", lambda: ManagerWidgets.get_instance().set_page("settings")),
            ("Exit", lambda: self.controller.on_exit_button() if self.controller else None)
        ]

        for i, (text, action) in enumerate(buttons):
            button = QPushButton()
            if not os.path.exists(self.res_icons[text.lower()]):
                button.setIcon(QIcon("res/icons/not_found.ico"))
            else:
                button.setIcon(QIcon(self.res_icons[text.lower()]))  # Set an icon based on the button text

            button.setIconSize(self.button_icon_size)  # Set a default icon size
            button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 1px solid black;
                    border-radius: 6px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.5);
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.7);
                }
            """)
            button.setToolTip(f"{text}")  # Add tooltip to display text on hover
            button.setFont(QFont("Arial", 12))
            button.setMinimumHeight(50)
            button.setMinimumWidth(50)
            button.clicked.connect(action) # type: ignore
            left_layout.addWidget(button)

            if i < len(buttons) - 1:
                left_layout.addWidget(QHLine())
                
        left_layout.addStretch()
        return left_widget
    
    @staticmethod
    def get_instance() -> "CreateWidgets":
        """
        Get the singleton instance of ManagerWidgets.
            :return: The singleton instance of ManagerWidgets.
        """
        if CreateWidgets._instance is None:
            raise Exception("CreateWidgets instance not created. Call CreateWidgets.")
        return CreateWidgets._instance