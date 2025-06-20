from typing import Any

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QLabel, 
    QHBoxLayout, 
    QCheckBox,
    QComboBox, 
    QPushButton,
    QScrollArea
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QTimer

from controller.app_controller import AppController
from gui.dialogs.dialogs_user import show_dialog_type
from gui.manage_widgets import ManagerWidgets
from gui.stack_compo.settings.settings_elixirs_widget import SettingsElixirsWidget
from config.config import res_abs_paths, scroll_bar_style

class SettingsWidget(QWidget):
    """
    A widget for managing application settings.
    This widget allows users to view and modify various settings such as region, confirmation messages, value pack, Extra Profit, language, and elixirs.
    It provides a user-friendly interface to change these settings and save them.
    """
    def __init__(self):
        super().__init__()
        self.controller = AppController.get_instance()

        settings_data = self.controller.get_all_settings_data()
        if settings_data is None:
            show_dialog_type("Failed to load settings data. Please check the settings file.", "Settings load", "error", "no_action")
            QTimer.singleShot(0, lambda: ManagerWidgets.get_instance().set_page("home")) # Gives time to render actual widget before switching inmediately (if not it will not render main widget)
            return

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
            'Auto Calculate Best Profit': settings_data.get('auto_calculate_best_profit', False),
            'Extra Profit (Ring, Old moon...)': settings_data.get('extra_profit', False),
            'Language': settings_data.get('language', 'en-US'),
            'Elixirs': settings_data.get('elixirs', {})
        }

        self.settings_actual_data: dict[str, tuple[str, Any]] = {
            'Region': ('region', self.original_settings['Region']),
            'Show Confirm Clean Sessions Message': ('show_confirm_clean_message', self.original_settings['Show Confirm Clean Sessions Message']),
            'Show Confirm Exit Message': ('show_confirm_exit_message', self.original_settings['Show Confirm Exit Message']),
            'Value Pack': ('value_pack', self.original_settings['Value Pack']),
            'Auto Calculate Best Profit': ('auto_calculate_best_profit', self.original_settings['Auto Calculate Best Profit']),
            'Extra Profit (Ring, Old moon...)': ('extra_profit', self.original_settings['Extra Profit (Ring, Old moon...)']),
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

            if setting_name in {'Show Confirm Clean Sessions Message', 'Show Confirm Exit Message', 'Value Pack', 'Extra Profit (Ring, Old moon...)', 'Auto Calculate Best Profit'}:
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
                    show_dialog_type(f"Invalid setting value for {setting_name}: {setting_val}.", "Setting value", "error", "no_action")
                    manager_widgets = ManagerWidgets.get_instance()
                    QTimer.singleShot(0, lambda: manager_widgets.set_page("home")) # Gives time to render actual widget before switching inmediately (if not it will not render main widget)
                    return

                combo_box.setCurrentText(setting_val)
                combo_box.currentTextChanged.connect(lambda val, text=setting_name: self.on_settings_changed(text, val)) # type: ignore
                setting_layout.addWidget(combo_box, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                layout_settings_inputs.addWidget(setting_widget) # Add the setting to the settings container widget

            else:
                self.scroll_area_elixirs = QScrollArea()
                self.scroll_area_elixirs.setStyleSheet(f"""
                    QScrollArea {{ 
                        background-color: rgb(30, 30, 30);
                        border: 2px solid rgb(80, 80, 80);
                        padding: 10px;
                        border-radius: 8px;
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
                self.scroll_area_elixirs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area_elixirs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
                self.scroll_area_elixirs.setWidgetResizable(True)
                self.scroll_area_elixirs.setFixedHeight(200)
                self.scroll_area_elixirs.setFixedWidth(400)

                self.elixirs_widget = SettingsElixirsWidget(setting_val, self.settings_actual_data, self.on_settings_changed) # Create an instance of the elixirs widget
                
                self.scroll_area_elixirs.setWidget(self.elixirs_widget)

                setting_layout.addWidget(self.scroll_area_elixirs, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                layout_settings_inputs.addWidget(setting_widget) # Add the setting to the settings container widget

                # Search elixirs input
                search_widget = QWidget()
                search_layout = QHBoxLayout(search_widget)

                search_elixir_line_edit = self.elixirs_widget.get_search_elixir_input()
                search_elixir_line_edit.textChanged.connect(lambda text: self.elixirs_widget.search_elixir(text)) # type: ignore

                search_layout.addWidget(search_elixir_line_edit, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                layout_settings_inputs.addWidget(search_widget) # Add search widget to settings container widget

        layout_main.addWidget(widget_settings_inputs, 0, Qt.AlignmentFlag.AlignTop)

        self.apply_settings_button = QPushButton("Apply Settings")
        self.apply_settings_button.setFont(QFont("Arial", 16))
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
        self.apply_settings_button.clicked.connect(lambda _: self.apply_user_settings()) # type: ignore

        layout_main.addWidget(self.apply_settings_button, 1, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

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

    def apply_user_settings(self):
        """ Apply the user settings by saving the current actual data to the controller.
            This method disables the widget while saving settings and re-enables it after saving.
            If the settings are saved successfully, it updates the original settings to match the current actual data.
        """
        self.setEnabled(False) # Disable the widget while saving settings
        result = self.controller.apply_user_settings(self.settings_actual_data)

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