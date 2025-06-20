import os
from typing import Any, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QGridLayout, QLineEdit
)
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

from logic.data_classes.new_session_data import NewSessionData
from gui.manage_widgets import ManagerWidgets
from gui.dialogs.dialogs_user import show_dialog_type
from gui.aux_components import SmartLabel
from controller.app_controller import AppController
from config.config import res_abs_paths, item_icons_root, settings_json

class NewSessionWidget(QWidget):
    def __init__(self, new_session: NewSessionData):
        """
        Initialize the NewSessionWidget with the provided parameters.
            :param new_session: An instance of NewSessionData containing the parameters for the new session.
        """
        super().__init__()
        
        # Controller instance to handle the logic of the new session
        self.controller = AppController.get_instance()
        self.new_session = new_session

        # Main widget and layout for new session
        new_session_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # As NewSessionWidget is a customized QWidget, we need to set this attribute to apply styles
        self.setObjectName("sessionContainer")
        self.setStyleSheet("""
            #sessionContainer {
                background-color: rgb(80, 130, 0);
                border-radius: 8px;
            }            
            #sessionContainer * {
                background-color: rgb(80, 130, 0);
                color: black;
            }
        """)

        # Default font and style for the widgets
        self.default_font = QFont('Arial', 14)
        self.default_style = """
            QLineEdit, QLabel, QPushButton {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid black; 
                border-radius: 4px;
                color: black;
                padding: 2px;
            }
        """
        self.qtooltip_style = """
            QToolTip {
                background-color: rgb(30, 30, 30);;
                border: 1px solid rgb(120, 120, 120);
                color: rgb(220, 220, 220);
                border-radius: 6px;
                font-size: 14px;
            }
        """
        self.results_default_style = """
            QLineEdit, QLabel {
                background-color: rgba(255,255,255,0.05);
                border: 1px solid black;
                border-radius: 4px;
                color: rgba(0, 0, 0, 0.7);
            }
        """

        # Set the hunting spot title and icon
        title_widget = self.create_session_title_widget()
        # Create the input widget that contains the input fields for the new session
        inputs_widget = self.create_session_inputs_widget()
        # Create the widget that contains exchange hides widget and elixirs cost widget
        exchange_elixirs_widget = self.create_session_exchange_elixirs_widget()
        # Create the widget that allows saving the results
        save_button_widget = self.create_session_save_button_widget()
        # Create the results widget to display the results of the new session
        results_widget = self.create_session_results_widget()

        # Adds the previous widgets to the main layout
        new_session_layout.addWidget(title_widget)
        new_session_layout.addWidget(inputs_widget)
        new_session_layout.addWidget(exchange_elixirs_widget)
        new_session_layout.addWidget(results_widget)
        new_session_layout.addWidget(save_button_widget)

        ManagerWidgets.get_instance().add_page("new_session", self)
        ManagerWidgets.get_instance().set_page("new_session")

        self.green_exchange_line_edit.setFocus() # Set focus on the green exchange line edit by default

    def create_session_title_widget(self) -> QWidget:
        """
        Create the title widget for the new session.
            :return: A QWidget containing the title and icon for the new session.
        """
        # Session title widget and layout
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_widget.setMaximumHeight(80)
        title_widget.setObjectName("titleWidget")
        title_widget.setStyleSheet("""
            #titleWidget {
                padding: 10px;
            }
        """)

        # Hunting zone title and icon
        hunting_zone_icon = QIcon(f"{item_icons_root}{self.new_session.spot_id_icon}.png") if os.path.exists(f"{item_icons_root}{self.new_session.spot_id_icon}.png") else QIcon(res_abs_paths["not_found_ico"])
        hunting_zone_name = QLabel(self.new_session.name_spot)
        hunting_zone_name.setFont(QFont("Arial", 24))
        hunting_zone_name.setContentsMargins(0, 0, 50, 0) # Add right margin to title label so it stays in center of screen after adding icon and spacing it
        hunting_zone_icon_label = QLabel()
        hunting_zone_icon_label.setContentsMargins(0, 0, 10, 0)  # Add some space between the icon and the label (right margin)
        hunting_zone_icon_label.setPixmap(hunting_zone_icon.pixmap(50, 50))
        title_layout.addWidget(hunting_zone_icon_label)
        title_layout.addWidget(hunting_zone_name)

        return title_widget

    def create_session_inputs_widget(self,) -> QWidget:
        """
        Create the input widget for the new session.
            :return: A QWidget containing the input fields for the new session.
        """
        inputs_widget = QWidget()
        inputs_layout = QGridLayout(inputs_widget)

        self.labels_icons_input: list[tuple[Optional[QIcon], QLabel, Optional[QLabel]]] = []

        assert self.new_session.items is not None, "Items must be provided in the new session data."
        for i, (id, (item_name, price)) in enumerate(self.new_session.items.items()):
            icon = QIcon(f"{item_icons_root}{id}.png") if os.path.exists(f"{item_icons_root}{id}.png") else QIcon(res_abs_paths["not_found_ico"])

            label = SmartLabel(f"{item_name} (0.00%)")
            label.setFont(self.default_font)
            label.setStyleSheet(f"""
                {self.qtooltip_style}
            """)

            price_value = QLabel(str(f"{price:,}"))
            price_value.setContentsMargins(15, 0, 0, 0)
            price_value.setFont(self.default_font)
            price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.labels_icons_input.append((icon, label, price_value))

        assert self.new_session.no_market_items is not None, "No market items must be provided in the new session data."
        for no_market_item in self.new_session.no_market_items:
            label = SmartLabel(f"{no_market_item} (0.00%)")
            label.setMinimumHeight(50)
            label.setFont(self.default_font)
            label.setStyleSheet(f"""
                {self.qtooltip_style}
            """)

            if "breath of narcion" in no_market_item.lower():
                icon = QIcon(res_abs_paths["breath_of_narcion"]) if os.path.exists(res_abs_paths["breath_of_narcion"]) else QIcon(res_abs_paths["not_found_ico"])
            else:
                no_market_item_lower_replace = no_market_item.lower().replace(" ", "_")
                icon = QIcon(res_abs_paths[no_market_item_lower_replace]) if os.path.exists(res_abs_paths[no_market_item_lower_replace]) else QIcon(res_abs_paths["not_found_ico"])

            price_value = QLabel("0")
            price_value.setContentsMargins(15, 0, 0, 0)
            price_value.setFont(self.default_font)
            price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.labels_icons_input.append((icon, label, price_value))

        label = SmartLabel("Hours")
        label.setMinimumHeight(50)
        label.setFont(self.default_font)
        label.setStyleSheet(f"""
            {self.qtooltip_style}
        """)

        self.labels_icons_input.append((None, label, None))

        # Data input fields
        self.line_edit_inputs: dict[str, QLineEdit] = {}
        # Column where to place next element
        col = 0

        for i, (icon, label, price) in enumerate(self.labels_icons_input):
            new_data_input = QLineEdit()
            name_without_percent = self.get_no_name_percent(label.text()) # Get the name without the percentage

            if (self.new_session.auto_calculate_best_profit and 
                (name_without_percent.startswith("M. Sp.") or 
                 name_without_percent.startswith("M. St.") or 
                 name_without_percent.startswith("BMB:"))):
                
                new_data_input.setReadOnly(True)
                new_data_input.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(255, 255, 255, 0.05);
                        border: 1px solid black; 
                        border-radius: 4px;
                        color: black;
                        padding: 2px;
                    }
                """)
            else:
                new_data_input.setStyleSheet(self.default_style)
                # Connects each input with callback function that updates the results of the new session
                new_data_input.textChanged.connect(self.update_session_results)
            
            new_data_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_data_input.setMinimumHeight(26)
            new_data_input.setFont(self.default_font)

            self.line_edit_inputs[name_without_percent] = new_data_input

            row_offset = (i // 7) * 3  # Calculate the row offset based on the group of 7 (3 rows per group)

            icon_label_widget = QWidget()
            icon_label_layout = QHBoxLayout(icon_label_widget)
            icon_label_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            if icon:
                icon_label = QLabel()
                icon_label.setPixmap(icon.pixmap(30, 30))
                icon_label_layout.addWidget(icon_label)

            label.setFont(self.default_font)
            icon_label_layout.addWidget(label)

            inputs_layout.addWidget(icon_label_widget, row_offset, col, Qt.AlignmentFlag.AlignTop)
            if price is not None:
                inputs_layout.addWidget(price, row_offset + 1, col, Qt.AlignmentFlag.AlignTop)
            inputs_layout.addWidget(new_data_input, row_offset + 2, col, Qt.AlignmentFlag.AlignTop)
            
            col +=1
            if col == 7:
                col = 0

        return inputs_widget
    
    def on_exchange_hides(self, green_hides: str, blue_hides: str):
        """ Handle the exchange of hides when the input fields are changed.
            :param green_hides: The number of green hides to exchange.
            :param blue_hides: The number of blue hides to exchange.
        """
        exchange_results = self.controller.on_exchange_hides(green_hides, blue_hides)
        if exchange_results:
            self.update_session_exchange_results(exchange_results)

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

    def create_session_exchange_elixirs_widget(self) -> QWidget:
        """
        Create a widget that contains the exchange hides and elixirs cost widgets.
            :return: A QWidget containing the exchange hides and elixirs cost widgets.
        """
        # Create widget that contains exchange hides and elixirs cost widgets
        exchange_elixirs_widget = QWidget()
        exchange_elixirs_layout = QHBoxLayout(exchange_elixirs_widget)
        exchange_elixirs_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create exchange hides widget
        exchange_hides_widget = self.create_session_exchange_hides_widget()
        # Create elixirs cost widget
        elixirs_cost_widget = self.create_session_elixirs_cost_widget()

        exchange_elixirs_layout.addWidget(exchange_hides_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        exchange_elixirs_layout.addWidget(elixirs_cost_widget, alignment=Qt.AlignmentFlag.AlignRight)

        return exchange_elixirs_widget

    def create_session_results_widget(self) -> QWidget:
        """
        Create the results widget to display the results of the new session.
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
            self.inputs_result.append(QLineEdit("0"))
            self.labels_result[i].setFont(self.default_font)
            self.inputs_result[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_result[i].setMinimumHeight(26)
            self.inputs_result[i].setFont(self.default_font)
            self.inputs_result[i].setStyleSheet(self.results_default_style)
            self.inputs_result[i].setReadOnly(True)

            results_layout.addWidget(self.labels_result[i], 0, i, Qt.AlignmentFlag.AlignBottom)
            results_layout.addWidget(self.inputs_result[i], 1, i, Qt.AlignmentFlag.AlignTop)

        return results_widget

    def create_session_save_button_widget(self) -> QWidget:
        """
        Create the save button widget.
            :return: A QWidget containing the save button.
        """
        save_button_widget = QWidget()
        save_button_layout = QHBoxLayout(save_button_widget)

        # Button to save data in an excel file
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save") # Add tooltip to display text on hover
        self.save_button.setFont(self.default_font)
        self.save_button.setStyleSheet(f"""
            QPushButton:disabled {{
                background-color: rgba(255, 255, 255, 0.05); 
                border: 1px solid black; 
                border-radius: 6px;
                color: rgba(0, 0, 0, 0.6);
            }}
            QPushButton:enabled {{
                background-color: rgba(255, 255, 255, 0.2); 
                border: 1px solid black; 
                border-radius: 6px;
                color: rgba(0, 0, 0, 1);
            }}
            QPushButton:hover{{
                background-color: rgba(255,255,255,0.5);
            }}
            QPushButton:pressed{{
                background-color: rgba(255,255,255,0.7);
            }}
            {self.qtooltip_style}
        """)
        
        self.save_button.setEnabled(False) # Inits the save button as disabled, it will be enabled when the user inputs data
        self.save_button.setFixedSize(250, 50)
        self.save_button.clicked.connect(self.save_session_excel)

        save_button_layout.addWidget(self.save_button, alignment= Qt.AlignmentFlag.AlignCenter)

        return save_button_widget

    def update_session_exchange_results(self, res_exchange: tuple[int, int, int]):
        """
        Update the exchange results input field with the provided results.
            :param res_exchange: A tuple containing the exchange results (total, green hides, blue hides).
        """
        self.exchange_results_line_edit.setText(f"{res_exchange[0]} ({res_exchange[1]}, {res_exchange[2]})")

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
            total_res = int(self.inputs_result[0].text().replace(",", ""))
            total_res_h = int(self.inputs_result[1].text().replace(",", ""))
            taxed_res = int(self.inputs_result[2].text().replace(",", ""))
            taxed_res_h = int(self.inputs_result[3].text().replace(",", ""))
        except ValueError:
            show_dialog_type("Invalid data in results fields", "Invalid results data", "error", "no_action")
            return
        
        res_name: list[str] = []
        res_data: list[str] = []
        for i in range(len(self.labels_icons_input)):
            name = self.labels_icons_input[i][1].text()
            name_no_percent = self.get_no_name_percent(name)  # Get the name without the percentage
            inp = self.line_edit_inputs[name_no_percent].text() if name_no_percent in self.line_edit_inputs else ""
            if inp == "" or name == "":
                return
            res_name.append(name)
            res_data.append(inp)

        if not self.controller.save_session(self.new_session.name_spot, res_name, res_data, labels_res, total_res, total_res_h, taxed_res, taxed_res_h):
            show_dialog_type("Error saving data, invalid data.", "Error saving", "error", "no_action")
            return
        
        show_dialog_type("Session saved successfully", "Success saving", "info", "no_action")
        self.controller.change_page("home")  # Switch back to the home page after saving the session

    def get_no_name_percent(self, name: str) -> str:
        """
        Get the name without the percentage from the given name.
            :param name: The name to process.
            :return: The name without the percentage.
        """
        return name[:name.index('(') - 1] if '(' in name else name
    
    def reupdate_item_amounts(self, res_data: dict[str, Any]):
        """
        Reupdate the item amounts in the input fields based on the provided results data.
            :param res_data: A dictionary containing the results data, where keys are item names and values are their amounts.
        """
        for name,( _, amount) in res_data.items():
            if name in self.line_edit_inputs and self.line_edit_inputs[name].text() != amount:
                self.line_edit_inputs[name].setText(amount)
                
    def update_session_results(self):
        """
        Update the results of the new session based on the input data.
        This method collects the input data, calculates the results, and updates the labels and input fields accordingly.
        """
        data_input: dict[str, tuple[str, str]] = {}
        # Calculate the results based on the input data
        all_inputs_filled: bool = True
        for i, (_, label, price) in enumerate(self.labels_icons_input):
            name_no_percent = self.get_no_name_percent(label.text()) # Get the name without the percentage
            amount = self.line_edit_inputs[name_no_percent].text()
            data_input[name_no_percent] = (price.text() if price else "", amount)

            if amount == "":
                all_inputs_filled = False
                if self.save_button.isEnabled():
                    self.save_button.setEnabled(False)

        assert self.new_session.lightstone_costs is not None, "Lightstone costs must be provided in the new session data."
        assert self.new_session.imperfect_lightstone_costs is not None, "Imperfect lightstone costs must be provided in the new session data."
        res_data = self.controller.get_session_results(self.new_session.name_spot, self.new_session.value_pack, self.new_session.market_tax, self.new_session.extra_profit, data_input, self.new_session.elixirs_cost, self.new_session.auto_calculate_best_profit, self.new_session.lightstone_costs, self.new_session.imperfect_lightstone_costs)
        if res_data == -1:
            show_dialog_type("Error calculating results, please ensure all fields contain digits", "Calculate results", "error", "no_action")
            return
        if not res_data:
            show_dialog_type(f"Error calculating results, please ensure that '{settings_json}' exists in 'res' directory and there are no missing fields.", "Calculate results", "error", "no_action")
            return
        
        if isinstance(res_data, int):
            show_dialog_type("Error calculating results, please ensure that all input data is valid.", "Calculate results", "error", "no_action")
            return
        
        self.reupdate_item_amounts(res_data["new_data_input"])
        
        results_tot = res_data["total"]
        results_tot_h = res_data["total_h"]
        results_tax = res_data["taxed"]
        results_tax_h = res_data["taxed_h"]
        new_labels_input_text = res_data["new_labels_input_text"]
        new_elixirs_cost = res_data["elixirs_cost"]

        for i, (_, label, _) in enumerate(self.labels_icons_input):
            label.setText(new_labels_input_text[i])
        
        self.inputs_result[0].setText(str(f"{results_tot:,}"))
        self.inputs_result[1].setText(str(f"{results_tot_h:,}"))
        self.inputs_result[2].setText(str(f"{results_tax:,}"))
        self.inputs_result[3].setText(str(f"{results_tax_h:,}"))

        # Update the elixirs cost input field with the new elixirs cost
        self.elixirs_cost_line_edit.setText(new_elixirs_cost)

        if all_inputs_filled:
            self.save_button.setEnabled(True) # Enable the save button after updating the results