from typing import Any
import os

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QLineEdit, 
    QHBoxLayout, 
    QCheckBox,
    QComboBox, 
    QPushButton, 
    QDialog, 
    QScrollArea
)
from PySide6.QtGui import QFont, QShortcut, QKeySequence, QMouseEvent, QIcon
from PySide6.QtCore import Qt, QTimer, QObject, QEvent, QPoint, QSize

from controller.app_controller import AppController
from gui.dialogs_user import show_dialog_type
from gui.manage_widgets import ManagerWidgets
from config.config import res_list

class SettingsWidget(QWidget):
    """
    A widget for managing application settings.
    This widget allows users to view and modify various settings such as region, confirmation messages, value pack, extra profit, language, and elixirs.
    It provides a user-friendly interface to change these settings and save them.
    """
    def __init__(self):
        super().__init__()

        self.controller = AppController.get_instance()
        self.matches_dialog = None  # Initialize matches_dialog attribute

        settings_data = self.controller.get_all_settings_data()
        if settings_data is None:
            show_dialog_type("Failed to load settings data. Please check the settings file.", "error")
            QTimer.singleShot(0, lambda: ManagerWidgets.get_instance().set_page("home")) # Gives time to render actual widget before switching inmediately (if not it will not render main widget)
            return
        
        self.installEventFilter(self) # Install event filter to capture mouse events

        layout_main = QVBoxLayout(self)
        layout_main.setSpacing(60)
        layout_main.setContentsMargins(20, 20, 20, 20)

        settings_title_label = QLabel("Settings")
        settings_title_label.setMinimumWidth(400)
        settings_title_label.setStyleSheet("""
            color: white;
            background-color: rgb(60, 60, 60);
            border: 2px solid rgb(80, 80, 80);
            padding: 10px;
            border-radius: 10px;
        """)
        self.elixir_labels_style = """
            QLabel {
                color: white;
                background-color: rgb(50, 50, 50);
                border: 1px solid rgb(80, 80, 80);
                padding: 5px;
                border-radius: 8px;
            }
        """
        self.elixirs_default_font = QFont("Arial", 12)
        
        settings_title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        settings_title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout_main.addWidget(settings_title_label, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        widget_settings_inputs = QWidget()
        layout_settings_inputs = QVBoxLayout(widget_settings_inputs)
        layout_settings_inputs.setSpacing(10)
        layout_settings_inputs.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        widget_settings_inputs.setStyleSheet("""
            background-color: rgb(30, 30, 30); 
        """)
        
        self.original_settings: dict[str, Any] = { # Get original settings from the controller to show or not show apply settings button
            'Region': settings_data.get('region', 'eu'),
            'Show Confirm Clean Sessions Message': settings_data.get('show_confirm_clean_message', True),
            'Show Confirm Exit Message': settings_data.get('show_confirm_exit_message', True),
            'Value Pack': settings_data.get('value_pack', False),
            'Extra profit (Ring, Old moon...)': settings_data.get('extra_profit', False),
            'Language': settings_data.get('language', 'en-US'),
            'Elixirs': settings_data.get('elixirs', {})
        }

        self.settings_actual_data: dict[str, tuple[str, Any]] = {
            'Region': ('region', self.original_settings['Region']),
            'Show Confirm Clean Sessions Message': ('show_confirm_clean_message', self.original_settings['Show Confirm Clean Sessions Message']),
            'Show Confirm Exit Message': ('show_confirm_exit_message', self.original_settings['Show Confirm Exit Message']),
            'Value Pack': ('value_pack', self.original_settings['Value Pack']),
            'Extra profit (Ring, Old moon...)': ('extra_profit', self.original_settings['Extra profit (Ring, Old moon...)']),
            'Language': ('language', self.original_settings['Language']),
            'Elixirs': ('elixirs', self.original_settings['Elixirs'].copy()) # Copy to avoid modifying the original settings
        }

        for setting_name, setting_val in self.original_settings.items():
            setting_label = QLabel(setting_name)
            setting_widget = QWidget()
            setting_widget.setMinimumWidth(900)
            setting_layout = QHBoxLayout(setting_widget)
            setting_label.setFont(QFont("Arial", 14))
            setting_layout.addWidget(setting_label, 0, Qt.AlignmentFlag.AlignLeft)

            if setting_name in {'Show Confirm Clean Sessions Message', 'Show Confirm Exit Message', 'Value Pack', 'Extra profit (Ring, Old moon...)'}:
                    check_box = QCheckBox()
                    check_box.setFont(QFont("Arial", 14))
                    check_box.setStyleSheet("""
                        QCheckBox {
                            color: white;
                        }
                        QCheckBox::indicator {
                            width: 20px;
                            height: 20px;
                        }
                        QCheckBox::indicator:unchecked {
                            border: 1px solid rgb(80, 80, 80);
                            background-color: rgb(30, 30, 30);
                        }
                        QCheckBox::indicator:checked {
                            border: 1px solid rgb(80, 80, 80);
                            background-color: rgb(150, 150, 150);
                        }
                    """)
                    check_box.setChecked(setting_val)
                    check_box.stateChanged.connect(lambda state, text=setting_name: self.on_settings_changed(text, state == Qt.CheckState.Checked.value)) # type: ignore

                    setting_layout.addWidget(check_box, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    layout_settings_inputs.addWidget(setting_widget) # Add the setting to the settings container widget

            elif setting_name in {'Region', 'Language'}:
                combo_box = QComboBox()
                combo_box.setFont(QFont("Arial", 14))
                combo_box.setMinimumWidth(100)
                combo_box.setStyleSheet("""
                    QComboBox {
                        background-color: rgb(50, 50, 50);
                        color: white;
                        border: 1px solid rgb(80, 80, 80);
                        padding: 5px;
                        border-radius: 8px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: rgb(50, 50, 50);
                        color: white;
                        selection-background-color: rgb(80, 80, 80);
                    }
                """)

                if setting_name == 'Region':
                    combo_box.addItems(['eu', 'na'])
                elif setting_name == 'Language':
                    combo_box.addItems(['en-US'])

                if combo_box.findText(setting_val) == -1:
                    show_dialog_type(f"Invalid setting value for {setting_name}: {setting_val}.", "error")
                    manager_widgets = ManagerWidgets.get_instance()
                    QTimer.singleShot(0, lambda: manager_widgets.set_page("home")) # Gives time to render actual widget before switching inmediately (if not it will not render main widget)
                    return

                combo_box.setCurrentText(setting_val)
                combo_box.currentTextChanged.connect(lambda val, text=setting_name: self.on_settings_changed(text, val)) # type: ignore
                setting_layout.addWidget(combo_box, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                layout_settings_inputs.addWidget(setting_widget) # Add the setting to the settings container widget

            else:
                self.scroll_area_elixirs = QScrollArea()
                self.scroll_area_elixirs.setStyleSheet("""
                    QScrollArea { 
                        background-color: rgb(30, 30, 30);
                        border: 2px solid rgb(80, 80, 80);
                        padding: 10px;
                        border-radius: 8px;
                    }
                    QScrollBar:vertical {
                        width: 16px;
                        background-color: rgb(30, 30, 30);
                    }
                    QScrollBar:horizontal {
                        height: 16px;
                        background-color: rgb(30, 30, 30);
                    }
                """)
                self.scroll_area_elixirs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area_elixirs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area_elixirs.setWidgetResizable(True)
                self.scroll_area_elixirs.setFixedHeight(200)
                self.scroll_area_elixirs.setFixedWidth(400)

                elixirs_widget = QWidget()
                self.elixirs_layout = QVBoxLayout(elixirs_widget)
                self.elixirs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                self.elixirs_layout.setSpacing(5)
                
                self.scroll_area_elixirs.setWidget(elixirs_widget)

                for id, name in setting_val.items():
                    self.add_elixir_entry(name, id)

                setting_layout.addWidget(self.scroll_area_elixirs, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                layout_settings_inputs.addWidget(setting_widget) # Add the setting to the settings container widget

                # Search elixirs input
                search_widget = QWidget()
                search_layout = QHBoxLayout(search_widget)

                self.search_line_edit = QLineEdit()
                self.search_line_edit.setFixedWidth(400)
                self.search_line_edit.setPlaceholderText("Elixir Name or ID")
                self.search_line_edit.setFont(QFont("Arial", 14))
                self.search_line_edit.setClearButtonEnabled(True)
                self.search_line_edit.setStyleSheet("""
                    QLineEdit {
                        background-color: rgb(50, 50, 50);
                        color: white;
                        border: 1px solid rgb(80, 80, 80);
                        padding: 5px;
                        border-radius: 8px;
                    }
                """)

                self.search_line_edit.textChanged.connect(lambda text: self.search_elixir(text)) # type: ignore
                self.esc_shortcut = QShortcut(QKeySequence("Escape"), self.search_line_edit)
                self.esc_shortcut.activated.connect(lambda: self.matches_dialog.close() if self.matches_dialog else None)

                search_layout.addWidget(self.search_line_edit, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                layout_settings_inputs.addWidget(search_widget) # Add search widget to settings container widget

        layout_main.addWidget(widget_settings_inputs, 0, Qt.AlignmentFlag.AlignTop)

        self.apply_settings_button = QPushButton("Apply Settings")
        self.apply_settings_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.apply_settings_button.setEnabled(False)
        self.apply_settings_button.setStyleSheet("""
            QPushButton:disabled {
                background-color: rgba(80, 80, 80, 0.05);
                color: rgba(255, 255, 255, 0.6);
                border: 1px solid rgb(80, 80, 80);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:enabled {
                background-color: rgb(80, 80, 80);
                color: rgba(255, 255, 255, 1);
                border: 1px solid rgb(80, 80, 80);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(120, 120, 120);
            }
            QPushButton:pressed {
                background-color: rgb(150, 150, 150);
            }
        """)
        self.apply_settings_button.clicked.connect(lambda _: self.save_user_settings()) # type: ignore

        layout_main.addWidget(self.apply_settings_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout_main.addStretch()

    def add_elixir_entry(self, elixir_id: str, elixir_name: str):
        """
        Add an entry for an elixir in the settings widget.
            :param elixir_id: The ID of the elixir.
            :param elixir_name: The name of the elixir.
        """
        entry_elixir_widget = QWidget()
        entry_elixir_layout = QHBoxLayout(entry_elixir_widget)
        entry_elixir_layout.setContentsMargins(0, 2, 0, 2)
        entry_elixir_layout.setSpacing(10)

        button_delete_elixir = QPushButton()
        button_delete_elixir.setFont(self.elixirs_default_font)
        button_delete_elixir.setIcon(QIcon(res_list["delete_elixir"]) if os.path.exists(res_list["delete_elixir"]) else QIcon(res_list["not_found_ico"]))
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

        button_delete_elixir.clicked.connect(lambda _, widget=entry_elixir_widget, name=elixir_name: self.delete_elixir_entry(widget, name)) # type: ignore

        label_elixir = QLabel(f"{elixir_name} ({elixir_id})")
        label_elixir.setFont(self.elixirs_default_font)
        label_elixir.setStyleSheet(self.elixir_labels_style)

        entry_elixir_layout.addWidget(button_delete_elixir, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        entry_elixir_layout.addWidget(label_elixir, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.elixirs_layout.addWidget(entry_elixir_widget, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def delete_elixir_entry(self, widget: QWidget, elixir_name: str):
        """
        Delete an elixir entry from the settings widget.
            :param widget: The widget representing the elixir entry to be deleted.
            :param elixir_name: The name of the elixir to be deleted.
        """
        self.elixirs_layout.removeWidget(widget)
        widget.setParent(None)
        widget.deleteLater()

        self.settings_actual_data['Elixirs'][1].pop(elixir_name, None)  # Remove the elixir from the settings data
        self.on_settings_changed('Elixirs', self.settings_actual_data['Elixirs'][1])  # Trigger settings change

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """
        Event filter to handle mouse events on the settings widget.
            :param obj: The object that received the event.
            :param event: The event that occurred.
            :return: True if the event was handled, False otherwise.
        """
        if event.type() == QEvent.Type.MouseButtonPress and self.matches_dialog and self.matches_dialog.isVisible():
            if isinstance(event, QMouseEvent):
                # Find the widget under the mouse click
                clicked_widget = self.childAt(self.mapFromGlobal(event.globalPos()))
                
                # If clicked widget is None or NOT a child/descendant of matches_dialog, close dialog
                if clicked_widget is None or not (clicked_widget == self.matches_dialog or self.matches_dialog.isAncestorOf(clicked_widget)):
                    self.matches_dialog.close()
                        
        return super().eventFilter(obj, event)

    def search_elixir(self, text: str):
        """
        Search for elixirs by name or ID and update the elixir settings.
            :param text: The text to search for in the elixirs.
        """
        matches = self.controller.get_match_elixirs(text)
        if matches is None:
            self.clean_matches_dialog()  # Clean previous dialog if exists
            return # Empty matches, do nothing
        self.show_elixir_matches(matches)

    def clean_matches_dialog(self):
        """
        Clean the matches dialog if it exists.
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
        self.clean_matches_dialog()  # Clean previous dialog if exists

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
            Qt.WindowType.WindowStaysOnTopHint
        )

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 16px;
                background-color: rgb(30, 30, 30);
            }
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

        if self.search_line_edit:
            height_search_line = self.search_line_edit.height()
            pos = self.search_line_edit.mapTo(self, QPoint(0, height_search_line))
            offset_x = (self.matches_dialog.width() - self.search_line_edit.width()) // 2  # Center the dialog horizontally below the search line edit 
            offset_y = 20
            self.matches_dialog.move(pos.x() - offset_x, pos.y() + offset_y)  # Position dialog below the search line edit
        
        self.matches_dialog.show() # Show dialog with matches

    def update_elixirs_list(self, elixir_name: str, elixir_id: str):
        """
        Update the elixirs list with the selected elixir from the matches dialog.
            :param elixir_name: The name of the elixir to add.
            :param elixir_id: The ID of the elixir to add.
        """
        id_entry_json, elixirs_dict = self.settings_actual_data['Elixirs'] # Get the actual elixirs list

        if elixir_id in elixirs_dict.values():
            show_dialog_type(f"Elixir {elixir_name} ({elixir_id}) is already in the list.", "info")
            return # If the elixir ID is already in the dict, do nothing

        elixirs_dict[elixir_name] = elixir_id # Add the new elixir to the list
        self.settings_actual_data['Elixirs'] = (id_entry_json, elixirs_dict)

        self.add_elixir_entry(elixir_id, elixir_name) # Add the new elixir entry to the UI

        self.search_line_edit.setText("") # Clear the search line edit to show the updated elixirs list
        self.matches_dialog.close() if self.matches_dialog else None # Close the dialog with matches

        self.on_settings_changed('Elixirs', elixirs_dict) # Notify that the settings have changed

    def update_original_settings(self):
        """
        Update the original settings with the current actual data.
        This is used to update the original settings after saving.
        """
        for key, value in self.settings_actual_data.items():
            if key == 'Elixirs':
                self.original_settings[key] = value[1].copy() # Copies the elixirs dict to avoid modifying the original settings directly
            else:
                self.original_settings[key] = value[1]

    def save_user_settings(self):
        self.setEnabled(False) # Disable the widget while saving settings
        result = self.controller.save_user_settings(self.settings_actual_data)

        if result == 0: # If the settings were saved successfully
            self.update_original_settings() # Update the original settings to match the current actual data
            self.setEnabled(True) # Re-enable the widget after saving settings
            # Buttons style is changed to indicate that the settings are saved (no changes to apply)
            self.apply_settings_button.setEnabled(False)
        else:
            self.setEnabled(True) # Re-enable the widget after saving settings

    def on_settings_changed(self, setting_name: str, value: Any):
        """
        Handle changes to settings enabling the apply settings button if the value has changed.
            :param setting_name: The name of the setting that was changed.
            :param value: The new value for the setting.
        """
        if setting_name in self.original_settings and self.original_settings[setting_name] != value:
            self.settings_actual_data[setting_name] = (self.settings_actual_data[setting_name][0], value)
            self.apply_settings_button.setEnabled(True) # Enable the apply settings button to apply changes
        elif self.apply_settings_button.isEnabled():
            self.apply_settings_button.setEnabled(False) # Disable the apply settings button if the value is the same as the original setting