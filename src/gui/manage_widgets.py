from PySide6.QtWidgets import QStackedWidget, QWidget, QMainWindow

class ManagerWidgets:
    """
    A helper class to manage multiple widgets via a QStackedWidget.
    """
    _instance = None

    def __init__(self):
        """
        Initialize the ManageWidgets instance with a QStackedWidget.
        This class is a singleton and should be accessed via the get_instance method.
        """
        if ManagerWidgets._instance is not None:
            raise Exception("This class is a singleton!")
        ManagerWidgets._instance = self
        self.stack = QStackedWidget()
        self.pages:dict[str, QWidget] = {}  #  Dictionary to hold page names and their corresponding widgets

    def add_page(self, name: str, page: QWidget):
        """
        Add a new page to the QStackedWidget.
            :param name: The name of the page to be added.
            :param page: The QWidget instance to be added as a page.
        """
        self.pages[name] = page
        self.stack.addWidget(page)

    def set_page(self, name: str):
        """
        Set the current page in the QStackedWidget by name.
            :param name: The name of the page to set as current.
        """
        if name in self.pages:
            self.stack.setCurrentWidget(self.pages[name])

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
        if ManagerWidgets._instance is None:
            raise Exception("ManagerWidgets instance not created. Call ManagerWidgets first.")
        return ManagerWidgets._instance