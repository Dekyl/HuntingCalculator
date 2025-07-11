from typing import Optional

from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PySide6.QtGui import QIcon, QGuiApplication, QShortcut, QCloseEvent, QKeySequence
from PySide6.QtCore import QSize

from gui.manage_widgets import ManagerWidgets
from gui.side_bar_widget import SideBarWidget
from gui.stack_compo.settings.settings_widget import SettingsWidget
from gui.stack_compo.home_widget import HomeWidget
from gui.stack_compo.new_session_widgets.new_session import NewSession
from gui.stack_compo.view_sessions_widget import ViewSessionsWidget
from controllers.app_controller import AppController
from config.config import res_abs_paths
from logic.data_classes.new_session_data import NewSessionData

class GuiEntryPoint(QMainWindow):
    def __init__(self):
        """
        Initializes the main window of the Hunting Calculator application.
        """
        super().__init__()

        self.setWindowIcon(QIcon(res_abs_paths["matchlock_ico"]))
        self.setWindowTitle("Hunting Calculator")
        self.resize(QSize(1800, 1020))
        self.setMinimumSize(QSize(400, 300))
        
        primary_screen = QGuiApplication.primaryScreen()
        if primary_screen:
            screen_geometry = primary_screen.availableGeometry()  # Use availableGeometry so the taskbar is not included
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

        # Create a main layout and widget for the window
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(main_widget)

        # Create the ManagerWidgets instance to manage different widgets in the application
        self.manager = ManagerWidgets()
        # Create the AppController instance to manage the application logic
        # This controller will handle interactions between the view and the model
        self.controller = AppController(self)
        # Create the left-side menu and add it to the main layout
        self.side_bar_widget = SideBarWidget(self)

        stack = self.manager.get_stack()

        # Add the left-side menu and the main stack to the main layout
        main_layout.addWidget(self.side_bar_widget)
        main_layout.addWidget(stack, stretch=1)

        self.manager.add_page("home", HomeWidget()) # Add the home widget to the manager
        self.manager.set_page("home")  # Set the home page as the current page
        self.create_shortcuts()

    def create_shortcuts(self):
        """
        Create keyboard shortcuts for various actions in the application.
        """
        # Home page shortcut
        self.shortcut_home = QShortcut(QKeySequence("Ctrl+H"), self)
        self.shortcut_home.activated.connect(lambda: self.manager.set_page("home"))

        # New session shortcut
        self.shortcut_new_session = QShortcut(QKeySequence("Ctrl+N"), self)
        new_session_button = self.side_bar_widget.get_left_widget_button("new_session")
        self.shortcut_new_session.activated.connect(lambda: new_session_button.click() if new_session_button else None)

        # View sessions shortcut
        self.shortcut_view_sessions = QShortcut(QKeySequence("Ctrl+A"), self)
        self.shortcut_view_sessions.activated.connect(lambda: self.controller.show_dialog_select_session_controller() if self.controller else None)

        # Clean sessions shortcut
        self.shortcut_clean_sessions = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut_clean_sessions.activated.connect(lambda: self.controller.clean_all_sessions_controller() if self.controller else None)

        # Settings shortcut
        self.shortcut_settings = QShortcut(QKeySequence("Ctrl+G"), self)
        self.shortcut_settings.activated.connect(self.create_settings_widget)

        # Exit application shortcut
        self.shortcut_exit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_exit.activated.connect(lambda: self.controller.handle_close_window() if self.controller else None)

    def create_new_session_widget(self, new_session: NewSessionData):
        """
        Create a new session widget for the specified hunting spot.
            :param new_session: An instance of NewSessionData containing the details of the new session.
        """
        self.actual_session = NewSession(new_session)

    def create_settings_widget(self):
        """
        Create and display the settings widget in the application.
        This method initializes the settings widget and adds it to the manager.
        """
        self.manager.add_page("settings", SettingsWidget())  # Add the settings widget to the manager
        self.manager.set_page("settings")  # Switch to the settings page
       
    def set_ui_enabled(self, enabled: bool):
        """
        Enable or disable the main UI components of the application.
            :param enabled: A boolean indicating whether to enable or disable the UI.
        """
        self.side_bar_widget.set_left_widget_buttons_enabled(enabled)
        self.set_shortcuts_enabled(enabled)

    def set_shortcuts_enabled(self, enabled: bool):
        """
        Enable or disable keyboard shortcuts in the application.
            :param enabled: A boolean indicating whether to enable or disable the shortcuts (exit shortcut is always enabled in case UI blocks for unexpected error).
        """
        self.shortcut_home.setEnabled(enabled)
        self.shortcut_new_session.setEnabled(enabled)
        self.shortcut_view_sessions.setEnabled(enabled)
        self.shortcut_clean_sessions.setEnabled(enabled)
        self.shortcut_settings.setEnabled(enabled)

    def set_session_button_enabled(self, enabled: bool):
        """
        Enable or disable the session button in the left-side menu and its shortcut.
            :param enabled: A boolean indicating whether to enable or disable the new session button.
        """
        self.side_bar_widget.set_left_widget_button_enabled("new_session", enabled)
        self.shortcut_new_session.setEnabled(enabled)

    def get_main_window_instance(self) -> QMainWindow:
        """
        Get the instance of the main window.
            :return: The instance of the QMainWindow.
        """
        return self
    
    def change_page(self, page: str):
        """
        Change the current page in the application.
            :param page: The name of the page to switch to.
        """
        self.manager.set_page(page)

    def get_current_page_name(self) -> Optional[str]:
        """
        Get the name of the current page in the application (required by ViewInterface).
            :return: The name of the current page.
        """
        return self.manager.get_current_page_name()
    
    def process_view_session(self, session_file_selected: str):
        """ Open the view sessions widget to display existing sessions.
        This method prompts the user to select a session file and then opens the ViewSessionsWidget
        to display the selected session.
            :param session_file_selected: The path to the session file selected by the user.
        """
        self.manager.add_page("view_sessions", ViewSessionsWidget(session_file_selected)) # Add the view_sessions widget to the manager
        self.manager.set_page("view_sessions") # Switch to the view sessions page

    def trigger_close_event(self):
        """
        Trigger the close event of the main window.
        This method is called when the user attempts to close the main window.
        """
        self.close()

    def closeEvent(self, closeEvent: QCloseEvent):
        """
        Overrides the window close event (e.g., clicking the X button).
        You can handle cleanup or confirmation here.
        """
        closeEvent.accept() if self.controller.on_exit_button_controller() else closeEvent.ignore()