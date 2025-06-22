from typing import Optional, cast

from PySide6.QtWidgets import QStackedWidget, QWidget, QMainWindow

no_singleton_pages = ["view_sessions", "settings", "new_session"]

class ManagerWidgets:
    """
    A helper class to manage multiple widgets via a QStackedWidget.
    """
    instance = None

    def __init__(self):
        """
        Initialize the ManageWidgets instance with a QStackedWidget.
        This class is a singleton and should be accessed via the get_instance method.
        """
        if ManagerWidgets.instance is not None:
            raise Exception("ManagerWidgets is a singleton!")
        ManagerWidgets.instance = self
        
        self.stack = QStackedWidget()
        self.pages: dict[str, QWidget] = {}  #  Dictionary to hold page names and their corresponding widgets

    def add_page(self, name: str, page: QWidget):
        """
        Add a new page to the QStackedWidget.
            :param name: The name of the page to be added.
            :param page: The QWidget instance to be added as a page.
        """
        current_page = self.get_current_page_name()

        if current_page and current_page in no_singleton_pages:
            # If the current page is in no_singleton_pages, we remove it from the stack to release resources
            old_page = self.pages[current_page]
            self.stack.removeWidget(old_page)
            old_page.deleteLater()  # Delete widget to free resources
            del self.pages[current_page]

        page.setProperty("page_name", name)
        self.pages[name] = page
        self.stack.addWidget(page)

    def set_page(self, name: str):
        """
        Set the current page in the QStackedWidget by name.
            :param name: The name of the page to set as current.
        """
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])

    def get_current_page_name(self) -> Optional[str]:
        """
        Get the name of the current page in the QStackedWidget.
            :return: The name of the current page or None if no page is set.
        """
        current_widget = cast(Optional[QWidget], self.stack.currentWidget())
        if current_widget is not None:
            return current_widget.property("page_name")
        return None

    def get_stack(self) -> QStackedWidget:
        """
        Get the QStackedWidget instance.
            :return: The QStackedWidget instance.
        """
        return self.stack
    
    def set_central_widget(self, mainWindow: QMainWindow):
        """
        Set the central widget of the QStackedWidget.
        """
        mainWindow.setCentralWidget(self.stack)

    @staticmethod
    def get_instance() -> "ManagerWidgets":
        """
        Get the singleton instance of ManagerWidgets.
            :return: The singleton instance of ManagerWidgets.
        """
        if ManagerWidgets.instance is None:
            raise Exception("ManagerWidgets instance not created. Call ManagerWidgets first.")
        return ManagerWidgets.instance