from PyQt6.QtWidgets import QApplication

from interface import MainWindow
from get_prices import search_prices
from get_results import update_data
from access_resources import prepare_resources

import sys, os

def main():
    print("Preparing resources...\n")
    prepare_resources()
    print("Searching prices...\n")
    search_prices()
    print("Updating data...\n")
    update_data()
    
    if os.path.exists('./Hunting Sessions') == False:
        os.mkdir('Hunting Sessions')
    
    print("Loading app...\n")
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == "__main__":
    main()