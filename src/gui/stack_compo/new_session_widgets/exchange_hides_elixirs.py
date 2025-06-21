from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from controllers.app_controller import AppController

class ExchangeHidesElixirs(QWidget):
    """ 
    A widget that contains the exchange hides and elixirs cost input fields and results of the exchange.
    This widget allows the user to input the number of green and blue hides to exchange and displays the results of the exchange, 
    as well as the cost of elixirs.
    """
    def __init__(self, default_font: QFont, default_style: str, results_default_style: str):
        """ Initialize the ExchangeHidesElixirs widget.
            :param default_font: The default font to be used for the labels and input fields.
            :param default_style: The default style to be applied to the input fields.
            :param results_default_style: The default style to be applied to the results input fields.
        """
        super().__init__()
        self.controller = AppController.get_instance()  # Controller instance to handle the logic of the new session
        self.default_font = default_font
        self.default_style = default_style
        self.results_default_style = results_default_style

        # Create widget that contains exchange hides and elixirs cost widgets
        exchange_elixirs_layout = QHBoxLayout(self)
        exchange_elixirs_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create exchange hides widget
        exchange_hides_widget = self.create_session_exchange_hides_widget()
        # Create elixirs cost widget
        elixirs_cost_widget = self.create_session_elixirs_cost_widget()

        exchange_elixirs_layout.addWidget(exchange_hides_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        exchange_elixirs_layout.addWidget(elixirs_cost_widget, alignment=Qt.AlignmentFlag.AlignRight)

    def create_session_exchange_hides_widget(self) -> QWidget:
        """
        Create a widget that contains the exchange hides input fields and results of the exchange.
            :param font: The font to be used for the labels and input fields.
            :return: A QWidget containing the exchange hides input fields and results of the exchange.
        """
        # Create widget that contains exchange hides input fields widget and results of the exchange
        exchange_widget = QWidget()
        exchange_widget.setContentsMargins(0, 0, 200, 0)
        exchange_layout = QVBoxLayout(exchange_widget)

        # Create a widget that contains the exchange hides input fields
        exchange_input_widget = QWidget()
        exchange_input_layout = QGridLayout(exchange_input_widget)

        green_exchange_label = QLabel("Green Hides Exchange")
        green_exchange_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        green_exchange_label.setFont(self.default_font)
        green_exchange_label.setContentsMargins(0, 0, 25, 0)

        blue_exchange_label = QLabel("Blue Hides Exchange")
        blue_exchange_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blue_exchange_label.setFont(self.default_font)
        blue_exchange_label.setContentsMargins(25, 0, 0, 0)

        self.green_exchange_line_edit = QLineEdit()
        self.green_exchange_line_edit.setFont(self.default_font)
        self.green_exchange_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_exchange_line_edit.setMinimumHeight(26)
        self.green_exchange_line_edit.setStyleSheet(self.default_style)
        self.green_exchange_line_edit.setMinimumWidth(220)
        self.green_exchange_line_edit.setContentsMargins(25, 0, 0, 0)
        
        blue_exchange_line_edit = QLineEdit()
        blue_exchange_line_edit.setFont(self.default_font)
        blue_exchange_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        blue_exchange_line_edit.setMinimumHeight(26)
        blue_exchange_line_edit.setStyleSheet(self.default_style)
        blue_exchange_line_edit.setMinimumWidth(220)
        blue_exchange_line_edit.setContentsMargins(25, 0, 0, 0)

        # Connects each input field with the function that resolves the request
        self.green_exchange_line_edit.textChanged.connect(lambda greens: self.on_exchange_hides(greens, blue_exchange_line_edit.text())) # type: ignore
        blue_exchange_line_edit.textChanged.connect(lambda blues: self.on_exchange_hides(self.green_exchange_line_edit.text(), blues)) # type: ignore

        exchange_input_layout.addWidget(green_exchange_label, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        exchange_input_layout.addWidget(blue_exchange_label, 0, 1, Qt.AlignmentFlag.AlignBottom)
        exchange_input_layout.addWidget(self.green_exchange_line_edit, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        exchange_input_layout.addWidget(blue_exchange_line_edit, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Adds the results of the exchange hides
        results_exchange_label = QLabel("Results Exchange")
        results_exchange_label.setFont(self.default_font)
        
        self.exchange_results_line_edit = QLineEdit()
        self.exchange_results_line_edit.setReadOnly(True)
        self.exchange_results_line_edit.setFont(self.default_font)
        self.exchange_results_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exchange_results_line_edit.setMinimumHeight(26)
        self.exchange_results_line_edit.setStyleSheet(self.default_style)
        self.exchange_results_line_edit.setMaximumWidth(220)

        exchange_layout.addWidget(exchange_input_widget, 0, Qt.AlignmentFlag.AlignCenter)
        exchange_layout.addWidget(results_exchange_label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        exchange_layout.addWidget(self.exchange_results_line_edit, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        return exchange_widget

    def on_exchange_hides(self, green_hides: str, blue_hides: str):
        """ Handle the exchange of hides when the input fields are changed.
            :param green_hides: The number of green hides to exchange.
            :param blue_hides: The number of blue hides to exchange.
        """
        exchange_results = self.controller.on_exchange_hides_controller(green_hides, blue_hides)
        if exchange_results:
            self.update_session_exchange_hides(exchange_results)

    def create_session_elixirs_cost_widget(self) -> QWidget:
        """
        Create a widget that contains the elixirs cost input field and label.
            :return: A QWidget containing the elixirs cost input field and label.
        """
        elixirs_cost_widget = QWidget()
        elixirs_cost_widget.setContentsMargins(200, 9, 0, 0) # Add some space at the top of the widget to align it with the exchange hides widget
        elixirs_cost_layout = QVBoxLayout(elixirs_cost_widget)
        elixirs_cost_layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
        
        elixirs_cost_label = QLabel("Elixirs Cost")
        elixirs_cost_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elixirs_cost_label.setFont(self.default_font)

        self.elixirs_cost_line_edit = QLineEdit("0")
        self.elixirs_cost_line_edit.setStyleSheet(self.results_default_style)
        self.elixirs_cost_line_edit.setFont(self.default_font)
        self.elixirs_cost_line_edit.setReadOnly(True)
        self.elixirs_cost_line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        elixirs_cost_layout.addWidget(elixirs_cost_label)
        elixirs_cost_layout.addWidget(self.elixirs_cost_line_edit)
        
        return elixirs_cost_widget

    def update_session_exchange_hides(self, res_exchange: tuple[int, int, int]):
        """
        Update the exchange results input field with the provided results.
            :param res_exchange: A tuple containing the exchange results (total, green hides, blue hides).
        """
        self.exchange_results_line_edit.setText(f"{res_exchange[0]} ({res_exchange[1]}, {res_exchange[2]})")

    def focus_green_exchange_line_edit(self):
        """ 
        Focus the green exchange line edit input field.
        This method is called to set the focus on the green exchange line edit input field when the widget is initialized.
        """
        if self.green_exchange_line_edit:
            self.green_exchange_line_edit.setFocus() # Set focus on the green exchange line edit by default

    def get_elixirs_cost_line_edit(self) -> QLineEdit:
        """
        Get the elixirs cost line edit input field.
            :return: The QLineEdit widget for elixirs cost.
        """
        return self.elixirs_cost_line_edit
