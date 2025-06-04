from PyQt6.QtWidgets import QApplication

from interface import MainWindow
from startup import setup_all
from logs import add_log

import sys

def main():
    """
    Main function to start the application.
    """
    if not setup_all():
        add_log("Failed to set up the application. Exiting...", "error")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()