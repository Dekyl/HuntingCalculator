import os
from typing import Any, Callable

from PySide6.QtWidgets import (
    QWidget, 
    QHBoxLayout, 
    QPushButton, 
    QLabel, 
    QVBoxLayout, 
    QScrollArea, 
    QDialog, 
    QLineEdit, 
    QApplication
)
from PySide6.QtCore import (
    Qt, 
    QSize, 
    QPoint, 
    QEvent, 
    QObject
)
from PySide6.QtGui import (
    QIcon, 
    QFont, 
    QShortcut, 
    QKeySequence, 
    QMouseEvent
)

from config.config import res_abs_paths, scroll_bar_style
from controllers.app_controller import AppController
from gui.dialogs.dialogs_user import show_dialog_type

class SettingsElixirsWidget(QWidget):
    """
    A widget for managing elixir settings in the application.
    This widget allows users to add, search, and delete elixirs from their settings.
    """
    def __init__(self, setting_val: dict[str, Any], settings_actual_data: dict[str, tuple[str, Any]], on_settings_changed: Callable[[str, Any], None]):
        """
        Initialize the SettingsElixirsWidget with the provided parameters.
            :param setting_val: A dictionary containing the elixir settings (id: name).
            :param settings_actual_data: A dictionary containing the actual data of the settings.
            :param on_settings_changed: A callback function to notify when settings change.
        """
        super().__init__()
        app_instance = QApplication.instance()
        if app_instance:
            app_instance.installEventFilter(self) # Install event filter to capture mouse events
        else:
            raise RuntimeError("QApplication instance is not initialized.")

        self.elixirs_layout = QVBoxLayout(self)
        self.elixirs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.elixirs_layout.setSpacing(5)
        
        self.on_settings_changed = on_settings_changed  # Callback to notify when settings change
        self.settings_actual_data = settings_actual_data # Actual data of the settings
        self.controller = AppController.get_instance()  # Get the application controller instance
        self.matches_dialog = None  # Initialize matches_dialog attribute

        for id, name in setting_val.items():
            self.add_elixir_entry(name, id)

        self.create_search_elixir_line_edit() # Create the search line edit for elixirs
        self.create_esc_shortcut() # Create the ESC shortcut to close the dialog

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Event filter to handle mouse events on the settings widget. (It is used to close the matches dialog when clicking outside of it)
            :param obj: The object that received the event.
            :param event: The event that occurred.
            :return: True if the event was handled, False otherwise.
        """
        if event.type() == QEvent.Type.MouseButtonPress and hasattr(self, 'matches_dialog') and self.matches_dialog and self.matches_dialog.isVisible():
            if isinstance(event, QMouseEvent):
                click_pos = event.globalPos()
                # Si el clic NO está dentro del rectángulo global del diálogo, ciérralo
                if not self.matches_dialog.geometry().contains(click_pos):
                    self.matches_dialog.close()
                    return True  # Evento manejado
        return super().eventFilter(obj, event)

    def create_search_elixir_line_edit(self):
        """ Create a search line edit for elixirs.
            This line edit allows users to search for elixirs by name or ID.
        """
        self.search_elixir_line_edit = QLineEdit()
        self.search_elixir_line_edit.setFixedWidth(400)
        self.search_elixir_line_edit.setPlaceholderText("Elixir Name or ID")
        self.search_elixir_line_edit.setFont(QFont("Arial", 14))
        self.search_elixir_line_edit.setClearButtonEnabled(True)
        self.search_elixir_line_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgb(50, 50, 50);
                color: white;
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 8px;
            }
        """)

    def create_esc_shortcut(self):
        """ Create a shortcut for the Escape key to close the matches dialog.
            This allows users to quickly close the dialog without needing to click a close button.
        """
        self.esc_shortcut = QShortcut(QKeySequence("Escape"), self.search_elixir_line_edit)
        self.esc_shortcut.activated.connect(lambda: self.matches_dialog.close() if self.matches_dialog else None)

    def add_elixir_entry(self, elixir_id: str, elixir_name: str):
        """
        Add an entry for an elixir in the settings widget.
            :param elixir_id: The ID of the elixir.
            :param elixir_name: The name of the elixir.
        """
        elixirs_default_font = QFont("Arial", 12)
        elixir_labels_style = """
            QLabel {
                color: white;
                background-color: rgb(50, 50, 50);
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 8px;
            }
        """

        entry_elixir_widget = QWidget()
        entry_elixir_layout = QHBoxLayout(entry_elixir_widget)
        entry_elixir_layout.setContentsMargins(0, 2, 0, 2)
        entry_elixir_layout.setSpacing(10)

        button_delete_elixir = QPushButton()
        button_delete_elixir.setFont(elixirs_default_font)
        button_delete_elixir.setIcon(QIcon(res_abs_paths["delete_elixir"]) if os.path.exists(res_abs_paths["delete_elixir"]) else QIcon(res_abs_paths["not_found_ico"]))
        button_delete_elixir.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border-radius: 14px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgb(120, 60, 60);
            }
            QPushButton:pressed {
                background-color: rgb(160, 60, 60);
            }
        """)
        button_delete_elixir.setIconSize(QSize(25, 25))

        button_delete_elixir.clicked.connect(lambda _, widget=entry_elixir_widget, id=elixir_id: self.delete_elixir_entry(widget, id)) # type: ignore

        label_elixir = QLabel(f"{elixir_name} ({elixir_id})")
        label_elixir.setFont(elixirs_default_font)
        label_elixir.setStyleSheet(elixir_labels_style)

        entry_elixir_layout.addWidget(button_delete_elixir, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        entry_elixir_layout.addWidget(label_elixir, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.elixirs_layout.addWidget(entry_elixir_widget, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) # Add the elixir entry widget to the parent widget
        
    def search_elixir(self, text: str):
        """
        Search for elixirs by name or ID and update the elixir settings.
            :param text: The text to search for in the elixirs.
        """
        matches = self.controller.get_match_elixirs_controller(text)
        if matches is None:
            self.close_matches_dialog()  # Close previous dialog if exists
            return # Empty matches, do nothing
        self.show_elixir_matches(matches)

    def close_matches_dialog(self):
        """
        Close the matches dialog if it exists.
        This is used to ensure that the dialog is not duplicated when searching for elixirs.
        """
        if self.matches_dialog:
            self.matches_dialog.close()
            self.matches_dialog = None

    def show_elixir_matches(self, matches: dict[str, str] | str):
        """
        Show a dialog with the elixir matches found based on the search text.
            :param matches: A dictionary of elixir matches found (id: name) or a string indicating no matches found.
        """
        self.close_matches_dialog()  # Close previous dialog if exists

        # Create a dialog to show the elixir matches
        self.matches_dialog = QDialog(self)
        self.matches_dialog.setStyleSheet("""
            QDialog {
                border: 2px solid rgb(120, 120, 120);
                border-radius: 10px;
                background-color: rgb(30, 30, 30);
                padding: 5px;
            }
        """)
        
        self.matches_dialog.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{ 
                background-color: transparent;
                border: none;
            }}
            
            {scroll_bar_style}

            QScrollBar::sub-line:vertical {{ /* Up arrow */
                background: rgb(150, 150, 150);
                height: 25px;
                width: 25px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                border-radius: 5px;
                image: url("{res_abs_paths['up_arrow']}");
            }}

            QScrollBar::add-line:vertical {{ /* Down arrow */
                background: rgb(150, 150, 150);
                height: 25px;
                width: 25px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border-radius: 5px;
                image: url("{res_abs_paths['down_arrow']}");
            }}

            QScrollBar::sub-line:horizontal {{ /* Left arrow */
                background: rgb(150, 150, 150);
                height: 20px;
                width: 18px;
                subcontrol-position: left;
                subcontrol-origin: margin;
                border-radius: 5px;
                image: url("{res_abs_paths['left_arrow']}");
            }}
            
            QScrollBar::add-line:horizontal {{ /* Right arrow */
                background: rgb(150, 150, 150);
                height: 20px;
                width: 18px;
                subcontrol-position: right;
                subcontrol-origin: margin;
                border-radius: 5px;
                image: url("{res_abs_paths['right_arrow']}");
            }}
        """)

        content_widget = QWidget()
        matches_layout = QVBoxLayout(content_widget)

        if isinstance(matches, str):
            # If matches is a string, it means no matches were found
            no_matches_label = QLabel(matches)
            no_matches_label.setStyleSheet("""
                color: white;
                font-size: 16px;
                padding: 10px;
            """)
            no_matches_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            matches_layout.addWidget(no_matches_label)

        else:
            for id, name in matches.items():
                match_button = QPushButton(f"{name} ({id})")
                match_button.setFont(QFont("Arial", 12))
                match_button.setMinimumHeight(30)
                match_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.2);
                        border: 1px solid rgba(255, 255, 255, 0.5);
                        border-radius: 6px;
                        color: rgb(220, 220, 220);
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.5);
                    }
                    QPushButton:pressed {
                        background-color: rgba(255, 255, 255, 0.7);
                    }
                    QToolTip {
                        background-color: rgb(30, 30, 30);;
                        border: 1px solid rgb(120, 120, 120);
                        border-radius: 6px;
                        font-size: 14px;
                    }              
                """)

                match_button.clicked.connect(lambda _, elixir_name=name, elixir_id=id: self.update_elixirs_list(elixir_name, elixir_id)) # type: ignore
                matches_layout.addWidget(match_button)

        scroll_area.setWidget(content_widget)

        dialog_layout = QVBoxLayout(self.matches_dialog)
        dialog_layout.addWidget(scroll_area)

        self.matches_dialog.adjustSize()
        self.matches_dialog.setMaximumHeight(200)
        self.matches_dialog.setMinimumWidth(500)

        if self.search_elixir_line_edit:
            height_search_line = self.search_elixir_line_edit.height()
            global_pos = self.search_elixir_line_edit.mapToGlobal(QPoint(0, height_search_line))
            offset_x = (self.matches_dialog.width() - self.search_elixir_line_edit.width()) // 2  # Center the dialog horizontally below the search line edit 
            offset_y = 20
            self.matches_dialog.move(global_pos.x() - offset_x, global_pos.y() + offset_y)  # Position dialog below the search line edit
        
        self.matches_dialog.show() # Show dialog with matches

    def get_search_elixir_input(self) -> QLineEdit:
        """ Get the search line edit for elixirs.
            :return: The QLineEdit widget used for searching elixirs.
        """
        return self.search_elixir_line_edit
    
    def update_elixirs_list(self, elixir_name: str, elixir_id: str):
        """
        Update the elixirs list with the selected elixir from the matches dialog.
            :param elixir_name: The name of the elixir to add.
            :param elixir_id: The ID of the elixir to add.
        """
        id_entry_json, elixirs_dict = self.settings_actual_data['Elixirs'] # Get the actual elixirs list

        if elixir_id in elixirs_dict:
            self.close_matches_dialog()  # Close previous dialog if exists
            show_dialog_type(f"{elixir_name} ({elixir_id}) is already in the list.", "Add elixir", "info", "no_action")
            return # If the elixir ID is already in the dict, do nothing

        elixirs_dict[elixir_id] = elixir_name # Add the new elixir to the list
        self.settings_actual_data['Elixirs'] = (id_entry_json, elixirs_dict)

        self.add_elixir_entry(elixir_id, elixir_name) # Add the new elixir entry to the UI

        self.search_elixir_line_edit.setText("") # Clear the search line edit to show the updated elixirs list
        self.matches_dialog.close() if self.matches_dialog else None # Close the dialog with matches

        self.on_settings_changed('Elixirs', elixirs_dict) # Notify that the settings have changed

    def delete_elixir_entry(self, entry_elixir_widget: QWidget, elixir_name: str):
        """
        Delete an elixir entry from the settings widget.
            :param entry_elixir_widget: The widget representing the elixir entry to be deleted.
            :param elixir_name: The name of the elixir to be deleted.
        """
        self.elixirs_layout.removeWidget(entry_elixir_widget)
        entry_elixir_widget.setParent(None)
        entry_elixir_widget.deleteLater()

        self.settings_actual_data['Elixirs'][1].pop(elixir_name, None)  # Remove the elixir from the settings data
        self.on_settings_changed('Elixirs', self.settings_actual_data['Elixirs'][1])  # Trigger settings change