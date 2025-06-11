from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QCheckBox, QComboBox, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from typing import Any

from controller.app_controller import AppController

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout_settings = QVBoxLayout(self)
        layout_settings.setSpacing(60)
        layout_settings.setContentsMargins(20, 20, 20, 20)

        settings_title_label = QLabel("Settings")
        settings_title_label.setStyleSheet("""
            color: white;
            background-color: rgb(30, 30, 30);
            border: 2px solid rgb(80, 80, 80);
            padding: 10px;
            border-radius: 10px;
        """)
        settings_title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        settings_title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout_settings.addWidget(settings_title_label, 0, Qt.AlignmentFlag.AlignTop)
        
        widget_settings_inputs = QWidget()
        layout_settings_inputs = QVBoxLayout(widget_settings_inputs)
        layout_settings_inputs.setSpacing(10)
        layout_settings_inputs.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        widget_settings_inputs.setStyleSheet("""
            background-color: rgb(30, 30, 30); 
        """)

        self.controller = AppController.get_instance()
        settings_data = self.controller.get_all_settings_data()
        
        self.original_settings: dict[str, Any] = {
            'Region': settings_data.get('region', 'eu'),
            'Show Confirm Clean Sessions Message': settings_data.get('show_confirm_clean_message', True),
            'Show Confirm Exit Message': settings_data.get('show_confirm_exit_message', True),
            'Value Pack': settings_data.get('value_pack', False),
            'Language': settings_data.get('language', 'en-US'),
            'Elixirs': settings_data.get('elixir_ids', [])
        }

        self.settings_actual_data: dict[str, tuple[str, Any]] = {
            'Region': ('region', self.original_settings['Region']),
            'Show Confirm Clean Sessions Message': ('show_confirm_clean_message', self.original_settings['Show Confirm Clean Sessions Message']),
            'Show Confirm Exit Message': ('show_confirm_exit_message', self.original_settings['Show Confirm Exit Message']),
            'Value Pack': ('value_pack', self.original_settings['Value Pack']),
            'Language': ('language', self.original_settings['Language']),
            'Elixirs': ('elixir_ids', self.original_settings['Elixirs'])
        }

        for setting_name, setting_val in self.original_settings.items():
            setting_label = QLabel(setting_name)
            setting_widget = QWidget()
            setting_widget.setMinimumWidth(700)
            setting_layout = QHBoxLayout(setting_widget)
            setting_label.setFont(QFont("Arial", 14))
            setting_layout.addWidget(setting_label, 0, Qt.AlignmentFlag.AlignLeft)

            text_setting_label = setting_label.text()
            if text_setting_label in {'Show Confirm Clean Sessions Message', 'Show Confirm Exit Message', 'Value Pack'}:
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
                    check_box.stateChanged.connect(lambda state, text=text_setting_label: self.on_settings_changed(text, state == Qt.CheckState.Checked.value)) # type: ignore

                    setting_layout.addWidget(check_box, 0, Qt.AlignmentFlag.AlignRight)

            elif text_setting_label in {'Region', 'Language'}:
                combo_box = QComboBox()
                combo_box.setFont(QFont("Arial", 14))
                combo_box.setMinimumWidth(100)
                combo_box.setStyleSheet("""
                    QComboBox {
                        background-color: rgb(50, 50, 50);
                        color: white;
                        border: 1px solid rgb(80, 80, 80);
                        padding: 5px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: rgb(50, 50, 50);
                        color: white;
                        selection-background-color: rgb(80, 80, 80);
                    }
                """)

                if text_setting_label == 'Region':
                    combo_box.addItems(['eu', 'na', 'asia']) # type: ignore
                    combo_box.setCurrentText(setting_val)
                elif text_setting_label == 'Language':
                    combo_box.addItems(['en-US', 'fr-FR', 'de-DE', 'es-ES']) # type: ignore
                    combo_box.setCurrentText(setting_val)

                combo_box.currentTextChanged.connect(lambda val, text=text_setting_label: self.on_settings_changed(text, val)) # type: ignore
                setting_layout.addWidget(combo_box, 0, Qt.AlignmentFlag.AlignRight)

            else:
                setting_line_edit = QLineEdit("")
                setting_line_edit.setFont(QFont("Arial", 14))
                setting_line_edit.setStyleSheet("""
                    background-color: rgb(50, 50, 50);
                    color: white;
                    border: 1px solid rgb(80, 80, 80);
                    padding: 5px;
                """)

                setting_layout.addWidget(setting_line_edit, 0, Qt.AlignmentFlag.AlignRight)
            layout_settings_inputs.addWidget(setting_widget)

        layout_settings.addWidget(widget_settings_inputs, 0, Qt.AlignmentFlag.AlignTop)

        self.apply_settings_button = QPushButton("Apply Settings")
        self.apply_settings_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.apply_settings_button.setEnabled(False)
        self.apply_settings_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(80, 80, 80, 0.05);
                color: rgba(255, 255, 255, 0.6);
                border: 1px solid rgb(80, 80, 80);
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(80, 80, 80);
            }
        """)
        self.apply_settings_button.clicked.connect(lambda _: self.save_user_settings()) # type: ignore

        layout_settings.addWidget(self.apply_settings_button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout_settings.addStretch()

    def update_original_settings(self):
        """
        Update the original settings with the current actual data.
        This is used to reset the original settings after saving.
        """
        self.original_settings = {key: value[1] for key, value in self.settings_actual_data.items()} # Takes second element of each tuple in settings_actual_data

    def save_user_settings(self):
        self.setEnabled(False) # Disable the widget while saving settings
        result = self.controller.save_user_settings(self.settings_actual_data)
        if result == 0: # If the settings were saved successfully
            self.update_original_settings() # Update the original settings to match the current actual data
            self.setEnabled(True) # Re-enable the widget after saving settings
            # Buttons style is changed to indicate that the settings are saved (no changes to apply)
            self.apply_settings_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(80, 80, 80, 0.05);
                    color: rgba(255, 255, 255, 0.6);
                    border: 1px solid rgb(80, 80, 80);
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                }
            """)
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
            self.apply_settings_button.setStyleSheet("""
                QPushButton {
                    background-color: rgb(80, 80, 80);
                    color: rgba(255, 255, 255, 1);
                    border: 1px solid rgb(80, 80, 80);
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                }
                QPushButton:pressed {
                    background-color: rgb(120, 120, 120);
                }
            """)
            self.apply_settings_button.setEnabled(True) # Enable the apply settings button to apply changes
        else:
            self.apply_settings_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(80, 80, 80, 0.05);
                    color: rgba(255, 255, 255, 0.6);
                    border: 1px solid rgb(80, 80, 80);
                    border-radius: 8px;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: rgb(80, 80, 80);
                }
                QPushButton:pressed {
                    background-color: rgb(120, 120, 120);
                }
            """)
            self.apply_settings_button.setEnabled(False)