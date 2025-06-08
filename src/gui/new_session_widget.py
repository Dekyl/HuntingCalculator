import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QGridLayout, QLineEdit
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

from gui.manage_widgets import ManagerWidgets
from gui.dialogs_user import show_dialog_error
from gui.aux_components import SmartLabel
from controller.app_controller import AppController

class NewSessionWidget(QWidget):
    def __init__(self, name_spot: str, id_icon: str, prices: list[tuple[str, int]], no_market_items: list[str], elixirs_cost: str):
        """
        Initialize the NewSessionWidget with the provided parameters.
            :param name_spot: The name of the hunting spot for the new session.
            :param id_icon: The ID of the icon associated with the hunting spot.
            :param prices: A list of tuples containing item names and their prices.
            :param no_market_items: A list of items that are not available in the market.
            :param elixirs_cost: The cost of elixirs per hour for the new session.
        """
        super().__init__()

        # Controller instance to handle the logic of the new session
        self.controller = AppController.get_instance()

        # Main widget and layout for new session
        new_session_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # As NewSessionWidget is a customized QWidget, we need to set this attribute to apply styles
        self.setStyleSheet("""
            background-color: rgb(80, 130, 0); color: black;
        """)

        # Font and style applied to a variety of components
        font = QFont('Arial', 14)
        style = "background-color: rgba(255,255,255,0.2); border: 1px solid black; border-radius: 4px"

        # Set the hunting spot title and icon
        title_widget = self.create_session_title_widget(name_spot, id_icon)
        # Create the input widget that contains the input fields for the new session
        inputs_widget = self.create_session_inputs_widget(prices, font, no_market_items, style)
        # Create the widget that contains exchange hides widget and elixirs cost widget
        exchange_elixirs_widget = self.create_session_exchange_elixirs_widget(font, style, elixirs_cost)
        # Create the widget that allows saving the results
        save_button_widget = self.create_session_save_button_widget(font)
        # Create the results widget to display the results of the new session
        results_widget = self.create_session_results_widget(font, style)

        # Adds the previous widgets to the main layout
        new_session_layout.addWidget(title_widget)
        new_session_layout.addWidget(inputs_widget)
        new_session_layout.addWidget(exchange_elixirs_widget)
        new_session_layout.addWidget(results_widget)
        new_session_layout.addWidget(save_button_widget)

        ManagerWidgets.get_instance().add_page("new_session", self)
        ManagerWidgets.get_instance().set_page("new_session")

    def create_session_title_widget(self, name_spot: str, id_icon: str) -> QWidget:
        """
        Create the title widget for the new session.
            :param name_spot: The name of the hunting spot for the new session.
            :param id_icon: The ID of the icon associated with the hunting spot.
            :return: A QWidget containing the title and icon for the new session.
        """
        # Session title widget and layout
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_widget.setMaximumHeight(80)

        # Hunting zone title and icon
        hunting_zone_icon = QIcon(f"res/icons/items/{id_icon}.png") if os.path.exists(f"res/icons/items/{id_icon}.png") else QIcon("res/icons/not_found.ico")
        hunting_zone_name = QLabel(name_spot)
        hunting_zone_name.setFont(QFont("Arial", 24))
        hunting_zone_name.setContentsMargins(0, 0, 50, 0) # Add right margin to title label so it stays in center of screen after adding icon and spacing it
        hunting_zone_icon_label = QLabel()
        hunting_zone_icon_label.setContentsMargins(0, 0, 10, 0)  # Add some space between the icon and the label (right margin)
        hunting_zone_icon_label.setPixmap(hunting_zone_icon.pixmap(50, 50))
        title_layout.addWidget(hunting_zone_icon_label)
        title_layout.addWidget(hunting_zone_name)

        return title_widget

    def create_session_inputs_widget(self, prices: list[tuple[str, int]], font: QFont, no_market_items: list[str], style: str) -> QWidget:
        """
        Create the input widget for the new session.
            :param prices: A list of tuples containing item names and their prices.
            :param font: The font to be used for the labels and input fields.
            :param no_market_items: A list of items that are not available in the market.
            :param style: The stylesheet to be applied to the input fields.
            :return: A QWidget containing the input fields for the new session.
        """
        inputs_widget = QWidget()
        inputs_layout = QGridLayout(inputs_widget)
        inputs_layout.setSpacing(10)

        self.labels_input: list[QLabel] = []
        price_values: list[QLabel] = []

        for item_name, price_value in prices:
            label = SmartLabel(f"{item_name} (0.00%)")
            label.setWordWrap(False)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setStyleSheet("""
                QToolTip { 
                    background-color: rgb(30, 30, 30);
                    color: rgb(220, 220, 220);
                    border: 1px solid rgb(220, 220, 220);
                }
            """)
            self.labels_input.append(label)
            price_value = QLabel(str(f"{price_value:,}"))
            price_value.setFont(font)
            price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            price_value.setMaximumHeight(20)
            price_values.append(price_value)

        for no_market_item in no_market_items:
            label = SmartLabel(f"{no_market_item} (0.00%)")
            label.setWordWrap(False)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setStyleSheet("""
                QToolTip {
                    background-color: rgb(30, 30, 30); 
                    color: rgb(220, 220, 220); 
                    border: 1px solid rgb(220, 220, 220); 
                }
            """)
            self.labels_input.append(label)

        self.labels_input.append(QLabel("Hours"))

        # Data input fields
        self.inputs_input: list[QLineEdit] = []
        # Column where to place next element
        col = 0

        for i in range(len(self.labels_input)):
            self.inputs_input.append(QLineEdit())
            self.labels_input[i].setFont(font)
            self.inputs_input[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_input[i].setMinimumHeight(30)
            self.inputs_input[i].setStyleSheet(style)
            # Connects each input with result outputs fields
            self.inputs_input[i].textChanged.connect(self.update_data) # type: ignore

            row_offset = (i // 7) * 3  # Calculate the row offset based on the group of 7 (3 rows per group)
            if i < len(price_values):
                inputs_layout.addWidget(self.labels_input[i], row_offset, col, Qt.AlignmentFlag.AlignBottom)
                inputs_layout.addWidget(price_values[i], row_offset + 1, col)
            else:
                inputs_layout.addWidget(self.labels_input[i], row_offset + 1, col, Qt.AlignmentFlag.AlignBottom)
            inputs_layout.addWidget(self.inputs_input[i], row_offset + 2, col, Qt.AlignmentFlag.AlignTop)
            
            col +=1
            if col == 7:
                col = 0

        return inputs_widget

    def create_session_exchange_hides_widget(self, font: QFont, style: str) -> QWidget:
        """
        Create a widget that contains the exchange hides input fields and results of the exchange.
            :param font: The font to be used for the labels and input fields.
            :param style: The stylesheet to be applied to the input fields.
            :return: A QWidget containing the exchange hides input fields and results of the exchange.
        """
        # Create widget that contains exchange hides input fields widget and results of the exchange
        exchange_widget = QWidget()
        exchange_layout = QVBoxLayout(exchange_widget)

        # Create a widget that contains the exchange hides input fields
        exchange_input_widget = QWidget()
        exchange_input_layout = QGridLayout(exchange_input_widget)

        green_exchange_label = QLabel("Green Hides Exchange")
        green_exchange_label.setFont(font)
        green_exchange_label.setContentsMargins(0, 0, 25, 0)

        blue_exchange_label = QLabel("Blue Hides Exchange")
        blue_exchange_label.setFont(font)
        blue_exchange_label.setContentsMargins(25, 0, 0, 0)

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

        exchange_input_layout.addWidget(green_exchange_label, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        exchange_input_layout.addWidget(blue_exchange_label, 0, 1, Qt.AlignmentFlag.AlignBottom)
        exchange_input_layout.addWidget(green_exchange_input, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        exchange_input_layout.addWidget(blue_exchange_input, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Adds the results of the exchange hides
        results_exchange_label = QLabel("Results Exchange")
        results_exchange_label.setFont(font)
        
        self.exchange_results_input = QLineEdit()
        self.exchange_results_input.setReadOnly(True)
        self.exchange_results_input.setFont(font)
        self.exchange_results_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exchange_results_input.setMinimumHeight(30)
        self.exchange_results_input.setStyleSheet("""
            background-color: rgba(255,255,255,0.2); border: 1px solid black; border-radius: 4px
        """)
        self.exchange_results_input.setMaximumWidth(220)

        exchange_layout.addWidget(exchange_input_widget, 0, Qt.AlignmentFlag.AlignCenter)
        exchange_layout.addWidget(results_exchange_label, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        exchange_layout.addWidget(self.exchange_results_input, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        return exchange_widget

    def create_session_elixirs_cost_widget(self, font: QFont, style: str, elixirs_cost: str) -> QWidget:
        return QWidget()

    def create_session_exchange_elixirs_widget(self, font: QFont, style: str, elixirs_cost: str) -> QWidget:
        """
        Create a widget that contains the exchange hides and elixirs cost widgets.
            :param font: The font to be used for the labels and input fields.
            :param style: The stylesheet to be applied to the input fields.
            :param elixirs_cost: The cost of elixirs per hour for the new session.
            :return: A QWidget containing the exchange hides and elixirs cost widgets.
        """
        # Create widget that contains exchange hides and elixirs cost widgets
        exchange_elixirs_widget = QWidget()
        exchange_elixirs_layout = QHBoxLayout(exchange_elixirs_widget)

        # Create exchange hides widget
        exchange_hides_widget = self.create_session_exchange_hides_widget(font, style)
        # Create elixirs cost widget
        elixirs_cost_widget = self.create_session_elixirs_cost_widget(font, style, elixirs_cost)

        exchange_elixirs_layout.addWidget(exchange_hides_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        exchange_elixirs_layout.addWidget(elixirs_cost_widget, alignment=Qt.AlignmentFlag.AlignRight)

        return exchange_elixirs_widget

    def create_session_results_widget(self, font: QFont, style: str) -> QWidget:
        """
        Create the results widget to display the results of the new session.
            :param font: The font to be used for the labels and input fields.
            :param style: The stylesheet to be applied to the input fields.
            :return: A QWidget containing the results of the new session.
        """
        results_widget = QWidget()
        results_layout = QGridLayout(results_widget)
        results_widget.setMaximumHeight(150)
        
        self.labels_result = [
            QLabel("Total"), 
            QLabel("Total/h"), 
            QLabel("Total Taxed"), 
            QLabel("Total Taxed/h")
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

            results_layout.addWidget(self.labels_result[i], 0, i, Qt.AlignmentFlag.AlignBottom)
            results_layout.addWidget(self.inputs_result[i], 1, i, Qt.AlignmentFlag.AlignTop)

        return results_widget

    def create_session_save_button_widget(self, font: QFont) -> QWidget:
        """
        Create the save button widget.
            :param font: The font to be used for the button.
            :return: A QWidget containing the save button.
        """
        save_button_widget = QWidget()
        save_button_layout = QHBoxLayout(save_button_widget)

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
        self.save_button.clicked.connect(self.save_session_excel) # type: ignore

        save_button_layout.addWidget(self.save_button, alignment= Qt.AlignmentFlag.AlignCenter)

        return save_button_widget

    def update_session_exchange_results(self, res_exchange: tuple[int, int, int]):
        """
        Update the exchange results input field with the provided results.
            :param res_exchange: A tuple containing the exchange results (total, green hides, blue hides).
        """
        self.exchange_results_input.setText(f"{res_exchange[0]} ({res_exchange[1]}, {res_exchange[2]})")

    def update_session_results(self):
        """
        Update the results input fields with the calculated results.
        This method retrieves the total money, total money per hour, total taxed, and total profit per hour,
        and updates the corresponding input fields with these values.
        """
        self.inputs_result[0].setText(str(f"{self.results_tot:,}"))
        self.inputs_result[1].setText(str(f"{self.results_tot_h:,}"))
        self.inputs_result[2].setText(str(f"{self.results_tax:,}"))
        self.inputs_result[3].setText(str(f"{self.results_tax_h:,}"))

    def save_session_excel(self):
        """
        Save the current session data to an Excel file.
        This method collects the input data, results, and labels, and saves them to an Excel file.
        If an error occurs during the saving process, it displays an error message dialog.
        """
        labels_res: list[str] = []

        for i in range(len(self.labels_result)):
            labels_res.append(self.labels_result[i].text())

        try:
            total_res = int(self.inputs_result[0].text())
            total_res_h = int(self.inputs_result[1].text())
            taxed_res = int(self.inputs_result[2].text())
            taxed_res_h = int(self.inputs_result[3].text())
        except ValueError:
            show_dialog_error("Error: Invalid data in results fields")
            return

        if self.controller.save_session(self.labels_input_text, self.data_input, labels_res, total_res, total_res_h, taxed_res, taxed_res_h) == -1:
            show_dialog_error("Error saving data, wrong data")
        
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
        
        self.update_session_results()
        self.save_button.setDisabled(False)