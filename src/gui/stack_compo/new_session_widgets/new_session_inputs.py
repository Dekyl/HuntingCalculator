import os
from typing import Optional, Any

from PySide6.QtWidgets import (
    QWidget, 
    QGridLayout, 
    QLabel, 
    QLineEdit, 
    QHBoxLayout
)
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt

from gui.aux_components import SmartLabel
from controllers.app_controller import AppController
from gui.dialogs.dialogs_user import show_dialog_type
from config.config import res_abs_paths
from logic.data_classes.new_session_data import NewSessionData
from logic.data_classes.session_input_callbacks import SessionInputCallbacks
from logic.data_classes.session_results import SessionResultsData
from config.config import settings_json

class SessionInputs(QWidget):
    def __init__(self, new_session: NewSessionData, default_font: QFont, qtooltip_style: str, default_style: str, session_input_callbacks: SessionInputCallbacks):
        """
        Initialize the SessionInputs widget with the provided parameters.
            :param new_session: An instance of NewSessionData containing the parameters for the new session.
            :param default_font: The default font to be used for the labels and input fields.
            :param qtooltip_style: The style for tooltips in the application.
            :param default_style: The default style to be applied to the input fields.
            :param session_input_callbacks: An instance of SessionInputCallbacks containing methods to get labels and
        """
        super().__init__()

        inputs_layout = QGridLayout(self)

        self.labels_icons_input: list[tuple[Optional[QIcon], QLabel, Optional[QLabel]]] = []
        self.controller = AppController.get_instance()  # Get the instance of the AppController
        self.new_session = new_session  # Store the new session data
        self.session_input_callbacks = session_input_callbacks  # Store the callbacks for getting labels and inputs

        assert self.new_session.items is not None, "Items must be provided in the new session data."
        for i, (id, (item_name, price)) in enumerate(self.new_session.items.items()):
            icon = QIcon(res_abs_paths[id]) if os.path.exists(res_abs_paths[id]) else QIcon(res_abs_paths["not_found_ico"])

            label = SmartLabel(f"{item_name} (0.00%)")
            label.setFont(default_font)
            label.setStyleSheet(f"""
                {qtooltip_style}
            """)

            price_value = QLabel(str(f"{price:,}"))
            price_value.setContentsMargins(15, 0, 0, 0)
            price_value.setFont(default_font)
            price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self.labels_icons_input.append((icon, label, price_value))

        assert self.new_session.no_market_items is not None, "No market items must be provided in the new session data."
        for no_market_item in self.new_session.no_market_items:
            label = SmartLabel(f"{no_market_item} (0.00%)")
            label.setMinimumHeight(50)
            label.setFont(default_font)
            label.setStyleSheet(f"""
                {qtooltip_style}
            """)

            if "breath of narcion" in no_market_item.lower():
                icon = QIcon(res_abs_paths["56221"]) if os.path.exists(res_abs_paths["56221"]) else QIcon(res_abs_paths["not_found_ico"]) # 56221 is the ID for Breath of Narcion
            else:
                no_market_item_lower_replace = no_market_item.lower().replace(" ", "_")
                icon = QIcon(res_abs_paths[no_market_item_lower_replace]) if os.path.exists(res_abs_paths[no_market_item_lower_replace]) else QIcon(res_abs_paths["not_found_ico"])

            price_value = QLabel("0")
            price_value.setContentsMargins(15, 0, 0, 0)
            price_value.setFont(default_font)
            price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.labels_icons_input.append((icon, label, price_value))

        label = SmartLabel("Hours")
        label.setMinimumHeight(50)
        label.setFont(default_font)
        label.setStyleSheet(f"""
            {qtooltip_style}
        """)

        self.labels_icons_input.append((None, label, None))

        # Data input fields
        self.line_edit_inputs: dict[str, QLineEdit] = {}
        # Column where to place next element
        col = 0

        for i, (icon, label, price) in enumerate(self.labels_icons_input):
            new_data_input = QLineEdit()
            name_without_percent = self.session_input_callbacks.get_no_name_percent(label.text()) # Get the name without the percentage

            if (new_session.auto_calculate_best_profit and 
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
                new_data_input.setStyleSheet(default_style)
                # Connects each input with callback function that updates the results of the new session
                new_data_input.textChanged.connect(self.update_session_results)
            
            new_data_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_data_input.setMinimumHeight(26)
            new_data_input.setFont(default_font)

            self.line_edit_inputs[name_without_percent] = new_data_input

            row_offset = (i // 7) * 3  # Calculate the row offset based on the group of 7 (3 rows per group)

            icon_label_widget = QWidget()
            icon_label_layout = QHBoxLayout(icon_label_widget)
            icon_label_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            if icon:
                icon_label = QLabel()
                icon_label.setPixmap(icon.pixmap(30, 30))
                icon_label_layout.addWidget(icon_label)

            label.setFont(default_font)
            icon_label_layout.addWidget(label)

            inputs_layout.addWidget(icon_label_widget, row_offset, col, Qt.AlignmentFlag.AlignTop)
            if price is not None:
                inputs_layout.addWidget(price, row_offset + 1, col, Qt.AlignmentFlag.AlignTop)
            inputs_layout.addWidget(new_data_input, row_offset + 2, col, Qt.AlignmentFlag.AlignTop)
            
            col +=1
            if col == 7:
                col = 0

    def update_session_results(self):
        """
        Update the results of the new session based on the input data.
        This method collects the input data, calculates the results, and updates the labels and input fields accordingly.
        """
        data_input: dict[str, tuple[str, str]] = {}
        # Calculate the results based on the input data
        all_inputs_filled: bool = True
        save_button = self.session_input_callbacks.get_save_button()

        for i, (_, label, price) in enumerate(self.labels_icons_input):
            name_no_percent = self.session_input_callbacks.get_no_name_percent(label.text()) # Get the name without the percentage
            amount = self.line_edit_inputs[name_no_percent].text()
            data_input[name_no_percent] = (price.text() if price else "", amount)

            if amount == "":
                all_inputs_filled = False
                if save_button.isEnabled():
                    save_button.setEnabled(False)

        assert self.new_session.lightstone_costs is not None, "Lightstone costs must be provided in the new session data."
        assert self.new_session.imperfect_lightstone_costs is not None, "Imperfect lightstone costs must be provided in the new session data."

        session_results = SessionResultsData(
            self.new_session.name_spot,
            value_pack=self.new_session.value_pack,
            market_tax=self.new_session.market_tax,
            extra_profit=self.new_session.extra_profit,
            data_input=data_input,
            elixirs_cost=self.new_session.elixirs_cost,
            auto_calculate_best_profit=self.new_session.auto_calculate_best_profit,
            lightstone_costs=self.new_session.lightstone_costs,
            imperfect_lightstone_costs=self.new_session.imperfect_lightstone_costs
        )

        res_data = self.controller.get_session_results_controller(session_results)
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

        input_results = self.session_input_callbacks.get_input_results()
        
        input_results[0].setText(str(f"{results_tot:,}"))
        input_results[1].setText(str(f"{results_tot_h:,}"))
        input_results[2].setText(str(f"{results_tax:,}"))
        input_results[3].setText(str(f"{results_tax_h:,}"))

        elixirs_cost_line_edit = self.session_input_callbacks.get_elixirs_cost_line_edit()

        # Update the elixirs cost input field with the new elixirs cost
        elixirs_cost_line_edit.setText(new_elixirs_cost)

        if all_inputs_filled:
            save_button.setEnabled(True) # Enable the save button after updating the results

    def reupdate_item_amounts(self, res_data: dict[str, Any]):
        """
        Reupdate the item amounts in the input fields based on the provided results data.
            :param res_data: A dictionary containing the results data, where keys are item names and values are their amounts.
        """
        for name,( _, amount) in res_data.items():
            if name in self.line_edit_inputs and self.line_edit_inputs[name].text() != amount:
                self.line_edit_inputs[name].setText(amount)

    def get_labels_icons_input(self) -> list[tuple[Optional[QIcon], QLabel, Optional[QLabel]]]:
        """
        Get the labels and icons for the input fields.
            :return: A list of tuples containing the icon, label, and price label for each input field.
        """
        return self.labels_icons_input
    
    def get_line_edit_inputs(self) -> dict[str, QLineEdit]:
        """
        Get the line edit inputs for the input fields.
            :return: A dictionary where keys are item names without percentage and values are QLineEdit widgets.
        """
        return self.line_edit_inputs