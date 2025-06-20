from PySide6.QtWidgets import QApplication

from gui.gui_entry_point import GuiEntryPoint
from logic.startup import setup_all

import sys

def main():
    """
    Main function to start the application.
    """
    if not setup_all():
        sys.exit(1)  # Exit if setup fails
    app = QApplication(sys.argv)
    window = GuiEntryPoint()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()