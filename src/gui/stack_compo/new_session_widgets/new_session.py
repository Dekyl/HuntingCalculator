from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt

from logic.data_classes.new_session_data import NewSessionData
from logic.data_classes.save_session_callbacks import SaveSessionCallbacks
from logic.data_classes.session_input_callbacks import SessionInputCallbacks
from gui.manage_widgets import ManagerWidgets
from controllers.app_controller import AppController
from . import *

class NewSession(QWidget):
    """
    A widget that allows the user to create a new session for a specific hunting spot.
    This widget initializes the necessary components for a new session, including input fields, results display, and save functionality.
    """
    def __init__(self, new_session: NewSessionData):
        """
        Initialize the NewSession widget with the provided parameters.
            :param new_session: An instance of NewSessionData containing the parameters for the new session.
        """
        super().__init__()
        
        # Controller instance to handle the logic of the new session
        self.controller = AppController.get_instance()

        # Main widget and layout for new session
        new_session_layout = QVBoxLayout(self)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) # As NewSession is a customized QWidget, we need to set this attribute to apply styles
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
        default_font = QFont('Arial', 14)
        default_style = """
            QLineEdit, QLabel, QPushButton {
                background-color: rgba(255, 255, 255, 0.4);
                border: 1px solid black; 
                border-radius: 4px;
                color: black;
                padding: 2px;
            }
        """
        qtooltip_style = """
            QToolTip {
                background-color: rgb(30, 30, 30);;
                border: 1px solid rgb(120, 120, 120);
                color: rgb(220, 220, 220);
                border-radius: 6px;
                font-size: 14px;
            }
        """
        results_default_style = """
            QLineEdit, QLabel {
                background-color: rgba(255,255,255,0.05);
                border: 1px solid black;
                border-radius: 4px;
                color: rgba(0, 0, 0, 0.7);
            }
        """   

        # Set the hunting spot title and icon
        title_widget = create_session_title_widget(new_session.name_spot, new_session.spot_id_icon)

        session_inputs_callbacks = SessionInputCallbacks(
            get_no_name_percent = self.get_no_name_percent,
            get_save_button = self.get_save_button,
            get_input_results = self.get_input_results,
            get_elixirs_cost_line_edit = self.get_elixirs_cost_line_edit
        )

        # Create the input widget that contains the input fields for the new session
        self.inputs_widget = SessionInputs(new_session, default_font, qtooltip_style, default_style, session_inputs_callbacks)
        # Create the widget that contains exchange hides widget and elixirs cost widget
        self.exchange_hides_elixirs_widget = ExchangeHidesElixirs(default_font, default_style, results_default_style)
        # Create the results widget to display the results of the new session
        self.results_widget = SessionResults(default_font, results_default_style)

        save_session_callbacks = SaveSessionCallbacks(
            get_labels_result = self.get_labels_result,
            get_inputs_result = self.get_input_results,
            get_labels_icons_input = self.get_labels_icons_input,
            get_line_edit_inputs = self.get_line_edit_inputs,
            get_no_name_percent = self.get_no_name_percent
        )

        # Create the widget that allows saving the results
        self.save_button_widget = SaveSessionButton(new_session.name_spot, default_font, qtooltip_style, save_session_callbacks)

        # Adds the previous widgets to the main layout
        new_session_layout.addWidget(title_widget)
        new_session_layout.addWidget(self.inputs_widget)
        new_session_layout.addWidget(self.exchange_hides_elixirs_widget)
        new_session_layout.addWidget(self.results_widget)
        new_session_layout.addWidget(self.save_button_widget)

        ManagerWidgets.get_instance().add_page("new_session", self)
        ManagerWidgets.get_instance().set_page("new_session")

        #self.exchange_hides_elixirs_widget.focus_green_exchange_line_edit()

    def get_no_name_percent(self, name: str) -> str:
        """
        Get the name without the percentage from the given name.
            :param name: The name to process.
            :return: The name without the percentage.
        """
        return name[:name.index('(') - 1] if '(' in name else name

    def get_labels_result(self) -> list[QLabel]:
        """
        Get the labels that display the results of the session.
            :return: A list of QLabel widgets containing the results labels.
        """
        return self.results_widget.get_labels_result()

    def get_input_results(self) -> list[QLineEdit]:
        """
        Get the input fields that display the results of the session.
            :return: A list of QLineEdit widgets containing the results.
        """
        return self.results_widget.get_input_results()
    
    def get_labels_icons_input(self) -> list[tuple[Optional[QIcon], QLabel, Optional[QLabel]]]:
        """
        Get the labels and icons input from the inputs widget.
            :return: A list of tuples containing the icon (if any), label, and optional additional label.
        """
        return self.inputs_widget.get_labels_icons_input()
    
    def get_line_edit_inputs(self) -> dict[str, QLineEdit]:
        """
        Get the line edit inputs from the inputs widget.
            :return: A dictionary where keys are input names and values are QLineEdit widgets.
        """
        return self.inputs_widget.get_line_edit_inputs()

    def get_save_button(self) -> QPushButton:
        """
        Get the save button from the inputs widget.
            :return: The QPushButton used to save the session.
        """
        return self.save_button_widget.get_save_button()
    
    def get_elixirs_cost_line_edit(self) -> QLineEdit:
        """
        Get the line edit for elixirs cost from the exchange hides and elixirs widget.
            :return: The QLineEdit used to input the elixirs cost.
        """
        return self.exchange_hides_elixirs_widget.get_elixirs_cost_line_edit()