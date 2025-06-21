from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from logic.data_classes.save_session_callbacks import SaveSessionCallbacks
from logic.data_classes.save_session_data import SaveSessionData
from gui.dialogs.dialogs_user import show_dialog_type
from controllers.app_controller import AppController

class SaveSessionButton(QWidget):
    """
    Placeholder for NewSessionData class.
    This class should contain the necessary attributes and methods for managing a new session.
    """
    def __init__(self, name_spot: str, default_font: QFont, qtooltip_style: str, callbacks: SaveSessionCallbacks):
        """
        Initialize the SaveSessionButton widget.
            :param name_spot: The name of the hunting spot for which the session is being created.
            :param default_font: The default font to be used for the button.
            :param qtooltip_style: The style for tooltips in the application.
            :param callbacks: An instance of SaveSessionCallbacks containing methods to get labels and inputs.
        """
        super().__init__()
        save_button_layout = QHBoxLayout(self)

        # Button to save data in an excel file
        self.save_button = QPushButton("Save")
        self.save_button.setToolTip("Save") # Add tooltip to display text on hover
        self.save_button.setFont(default_font)
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
            {qtooltip_style}
        """)
        self.name_spot = name_spot
        self.controller = AppController.get_instance()  # Get the instance of the AppController
        self.callbacks = callbacks  # Store the callbacks for getting labels and inputs
        
        self.save_button.setEnabled(False) # Inits the save button as disabled, it will be enabled when the user inputs data
        self.save_button.setFixedSize(250, 50)
        self.save_button.clicked.connect(self.save_session_excel)

        save_button_layout.addWidget(self.save_button, alignment= Qt.AlignmentFlag.AlignCenter)

    def save_session_excel(self):
        """
        Save the current session data to an Excel file.
        This method collects the input data, results, and labels, and saves them to an Excel file.
        If an error occurs during the saving process, it displays an error message dialog.
        """
        labels_res: list[str] = []

        labels_result = self.callbacks.get_labels_result()  # Get the labels for results
        inputs_result = self.callbacks.get_inputs_result()  # Get the input fields for results

        for i in range(len(labels_result)):
            labels_res.append(labels_result[i].text())

        try:
            total_res = int(inputs_result[0].text().replace(",", ""))
            total_res_h = int(inputs_result[1].text().replace(",", ""))
            taxed_res = int(inputs_result[2].text().replace(",", ""))
            taxed_res_h = int(inputs_result[3].text().replace(",", ""))
        except ValueError:
            show_dialog_type("Invalid data in results fields", "Invalid results data", "error", "no_action")
            return
        
        res_name: list[str] = []
        res_data: list[str] = []

        labels_icons_input = self.callbacks.get_labels_icons_input()  # Get the labels and icons for inputs
        line_edit_inputs = self.callbacks.get_line_edit_inputs()  # Get the line edit inputs

        for i in range(len(labels_icons_input)):
            name = labels_icons_input[i][1].text()
            name_no_percent = self.callbacks.get_no_name_percent(name)  # Get the name without the percentage
            inp = line_edit_inputs[name_no_percent].text() if name_no_percent in line_edit_inputs else ""
            if inp == "" or name == "":
                return
            res_name.append(name)
            res_data.append(inp)

        session_data = SaveSessionData(self.name_spot, res_name, res_data, labels_res, total_res, total_res_h, taxed_res, taxed_res_h)
        if not self.controller.save_session(session_data):
            show_dialog_type("Error saving data, invalid data.", "Error saving", "error", "no_action")
            return
        
        show_dialog_type("Session saved successfully", "Success saving", "info", "no_action")
        self.controller.change_page("home")  # Switch back to the home page after saving the session

    def get_save_button(self) -> QPushButton:
        """
        Get the save button for saving the session data.
            :return: The QPushButton instance used to save the session data.
        """
        return self.save_button