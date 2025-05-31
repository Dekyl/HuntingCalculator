from PyQt6.QtWidgets import QGridLayout, QMessageBox, QWidget, QLineEdit, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon

from get_results import *
from save_results import *
from exchange_calculator import exchange_results
from get_percentage import get_percentage_item

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon("./res/matchlock.ico"))

        self.setWindowTitle("Hunting Calculator")
        self.resize(QSize(1800, 900))
        self.setMinimumSize(QSize(400, 300))
        self.move(60, 60)
        self.setStyleSheet("""
            QWidget {
                color: black;
                background-color: #5A9200;
            }
        """)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #5A9200")

        self.setCentralWidget(main_widget)

        # Title widget and layout
        title_widget = QWidget()
        title_layout = QHBoxLayout()

        title_widget.setLayout(title_layout)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_widget.setMaximumHeight(80)
        title_widget.setContentsMargins(0, 30, 0, 0)

        hunting_zone = QLabel("Shadow Lion")
        hunting_zone.setFont(QFont("Arial", 24))
        title_layout.addWidget(hunting_zone)

        # Inputs, exchange and results fields
        inputs_widget = QWidget()
        inputs_layout = QGridLayout()
        inputs_widget.setLayout(inputs_layout)

        exchange_widget = QWidget()
        exchange_widget.setMaximumHeight(70)
        exchange_layout = QGridLayout()
        exchange_widget.setLayout(exchange_layout)

        exchange_results_widget = QWidget()
        exchange_results_widget.setMaximumHeight(70)
        exchange_results_layout = QGridLayout()
        exchange_results_widget.setLayout(exchange_results_layout)

        results_widget = QWidget()
        results_widget.setMaximumHeight(150)
        results_layout = QGridLayout()
        results_widget.setLayout(results_layout)

        font = QFont('Arial', 14)

        # Button to save data in an excel file
        self.save_button = QPushButton("SAVE")
        self.save_button.setFont(font)
        self.save_button.setStyleSheet("""
            QPushButton{
                background-color: rgba(255,255,255,0.2); 
                border: 1px solid black; 
                border-radius: 6px
            }
            QPushButton:hover{
                background-color: rgba(255,255,255,0.5);
            }""")
        self.save_button.setDisabled(True)
        self.save_button.setFixedSize(250, 50)
        self.save_button.clicked.connect(self.save_excel)
        save_but_widget = QWidget()
        save_but_widget.setFixedHeight(100)
        save_but_lay = QHBoxLayout()

        save_but_widget.setLayout(save_but_lay)
        save_but_widget.setContentsMargins(0, 0, 0, 100)
        save_but_lay.addWidget(self.save_button, alignment= Qt.AlignmentFlag.AlignCenter)

        # Adds the previous widgets to the main layout
        main_layout.addWidget(title_widget)
        main_layout.addWidget(inputs_widget)
        main_layout.addWidget(exchange_widget)
        main_layout.addWidget(exchange_results_widget)
        main_layout.addWidget(results_widget)
        main_layout.addWidget(save_but_widget)

        self.labels_input = [
            QLabel("Lion Meat (0.00%)"), 
            QLabel("Lion Hide (0.00%)"), 
            QLabel("Lion Blood (0.00%)"), 
            QLabel("Fire Horn (0.00%)"), 
            QLabel("Black Gem Fragment (0.00%)"), 
            QLabel("Black Gem (0.00%)"), 
            QLabel("Con. Magical Black Gem (0.00%)"), 
            QLabel("S. Black Crystal Shard (0.00%)"), 
            QLabel("Caphras Stone (0.00%)"), 
            QLabel("Breath of Narcion (0.00%)"), 
            QLabel("Damaged Hide (0.00%)"), 
            QLabel("Usable Hide (0.00%)"), 
            QLabel("Supreme Hide (0.00%)"), 
            QLabel("Cracked Tooth (0.00%)"), 
            QLabel("Intact Tooth (0.00%)"), 
            QLabel("Sharp Tooth (0.00%)"), 
            QLabel("St. Shadow Lion Head (0.00%)"), 
            QLabel("Imp. Light. of Flora (0.00%)"), 
            QLabel("Artifacts (0.00%)"),
            QLabel("Wildspark (0.00%)"),
            QLabel("Breath of Narcion Bought (0.00%)"),
            QLabel("Breath of Narcion Previous (0.00%)"),
            QLabel("Hours")
        ]

        # Data input fields
        self.inputs_input = []
        
        # Column where to place next element
        col = 0
        # Stylesheet used in all textfields
        style = "background-color: rgba(255,255,255,0.2); border: 1px solid black; border-radius: 4px"

        with open('./res/data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            prices = data['prices']

        for i in range(len(self.labels_input)):
            self.inputs_input.append(QLineEdit())
            self.labels_input[i].setFont(font)
            self.inputs_input[i].setFont(font)
            self.inputs_input[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_input[i].setMinimumHeight(30)
            self.inputs_input[i].setStyleSheet(style)
            # Connects each input with result outputs fields
            self.inputs_input[i].textChanged.connect(self.check_data)

            if i < 7:
                inputs_layout.addWidget(self.labels_input[i], 0, col, Qt.AlignmentFlag.AlignBottom)
                price_value = QLabel(str(f"{prices[i]:,}"))
                price_value.setFont(font)
                price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
                price_value.setMaximumHeight(20)
                inputs_layout.addWidget(price_value, 1, col)
                inputs_layout.addWidget(self.inputs_input[i], 2, col, Qt.AlignmentFlag.AlignTop)
            elif i < 14:
                inputs_layout.addWidget(self.labels_input[i], 3, col, Qt.AlignmentFlag.AlignBottom)
                price_value = QLabel(str(f"{prices[i]:,}"))
                price_value.setFont(font)
                price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
                price_value.setMaximumHeight(20)
                inputs_layout.addWidget(price_value, 4, col)
                inputs_layout.addWidget(self.inputs_input[i], 5, col, Qt.AlignmentFlag.AlignTop)
            elif i < 21:
                inputs_layout.addWidget(self.labels_input[i], 6, col, Qt.AlignmentFlag.AlignBottom)
                if i < 19:
                    price_value = QLabel(str(f"{prices[i]:,}"))
                    price_value.setFont(font)
                    price_value.setAlignment(Qt.AlignmentFlag.AlignLeft)
                    price_value.setMaximumHeight(20)
                    inputs_layout.addWidget(price_value, 7, col)
                inputs_layout.addWidget(self.inputs_input[i], 8, col, Qt.AlignmentFlag.AlignTop)
            else:
                inputs_layout.addWidget(self.labels_input[i], 9, col, Qt.AlignmentFlag.AlignBottom)
                inputs_layout.addWidget(self.inputs_input[i], 11, col, Qt.AlignmentFlag.AlignTop)
            
            col +=1
            if col == 7:
                col = 0

        # Exchange hides section
        green_exchange = QLabel("Green Hides Exchange")
        exchange_layout.addWidget(green_exchange, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        green_exchange.setFont(font)
        green_exchange.setContentsMargins(0, 0, 25, 0)

        blue_exchange = QLabel("Blue Hides Exchange")
        exchange_layout.addWidget(blue_exchange, 0, 1, Qt.AlignmentFlag.AlignBottom)
        blue_exchange.setFont(font)
        blue_exchange.setContentsMargins(25, 0, 0, 0)

        self.green_exchange_input = QLineEdit()
        self.green_exchange_input.setFont(font)
        self.green_exchange_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.green_exchange_input.setMinimumHeight(30)
        self.green_exchange_input.setStyleSheet(style)
        self.green_exchange_input.setMinimumWidth(220)
        self.green_exchange_input.setContentsMargins(0, 0, 25, 0)
        
        self.blue_exchange_input = QLineEdit()
        self.blue_exchange_input.setFont(font)
        self.blue_exchange_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.blue_exchange_input.setMinimumHeight(30)
        self.blue_exchange_input.setStyleSheet(style)
        self.blue_exchange_input.setMinimumWidth(220)
        self.blue_exchange_input.setContentsMargins(25, 0, 0, 0)

        # Connects each input field with the function that resolves the request
        self.green_exchange_input.textChanged.connect(self.exchange_hides)
        self.blue_exchange_input.textChanged.connect(self.exchange_hides)

        exchange_layout.addWidget(self.green_exchange_input, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        exchange_layout.addWidget(self.blue_exchange_input, 1, 1, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        results_exchange = QLabel("Results Exchange")
        results_exchange.setFont(font)
        exchange_results_layout.addWidget(results_exchange, 0, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)

        self.exchange_results_input = QLineEdit()
        self.exchange_results_input.setReadOnly(True)
        self.exchange_results_input.setFont(font)
        self.exchange_results_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.exchange_results_input.setMinimumHeight(30)
        self.exchange_results_input.setStyleSheet(style)
        self.exchange_results_input.setMaximumWidth(220)
        exchange_results_layout.addWidget(self.exchange_results_input, 1, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)

        self.labels_result = [
            QLabel("Total Money"), 
            QLabel("Total Money/h"), 
            QLabel("Total Taxed"), 
            QLabel("Total Profit/h")
        ]
        
        self.inputs_result = []

        for i in range(len(self.labels_result)):
            self.inputs_result.append(QLineEdit())
            self.labels_result[i].setFont(font)
            self.inputs_result[i].setFont(font)
            self.inputs_result[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inputs_result[i].setMinimumHeight(30)
            self.inputs_result[i].setStyleSheet(style)
            self.inputs_result[i].setReadOnly(True)

            results_layout.addWidget(self.labels_result[i], 2, i, Qt.AlignmentFlag.AlignBottom)
            results_layout.addWidget(self.inputs_result[i], 3, i, Qt.AlignmentFlag.AlignTop)

    def exchange_hides(self):
        greens = self.green_exchange_input.text()
        blues = self.blue_exchange_input.text()

        if len(greens) == 0 or len(blues) == 0:
            return
        try:
            res_exchange = exchange_results(int(greens), int(blues))
            self.exchange_results_input.setText(f"{res_exchange[0]} ({res_exchange[1]}, {res_exchange[2]})")
        except:
            return
    
    def check_data(self):
        self.labels_input_text = []
        self.data_input = []

        for i in range(len(self.inputs_input)):
            self.labels_input_text.append(self.labels_input[i].text())
            self.data_input.append(self.inputs_input[i].text())

        self.results_tot = results_total(self.data_input)
        self.results_tot_h = results_h()
        self.results_tax = results_taxed()
        self.results_tax_h = results_taxed_h()

        gains_per_item = get_gains_per_item()
        results_tot_percentage = get_results_tot_percentage()

        for i in range(len(self.labels_input)-1):
            new_label_text = get_percentage_item(self.labels_input[i].text(), gains_per_item[i], results_tot_percentage)

            self.labels_input_text[i] = new_label_text
            self.labels_input[i].setText(new_label_text)

        self.save_button.setDisabled(False)
        self.show_results()

    def show_results(self):
        self.inputs_result[0].setText(str(f"{self.results_tot:,}"))
        self.inputs_result[1].setText(str(f"{self.results_tot_h:,}"))
        self.inputs_result[2].setText(str(f"{self.results_tax:,}"))
        self.inputs_result[3].setText(str(f"{self.results_tax_h:,}"))

    def save_excel(self):
        labels_res = []

        for i in range(len(self.labels_result)):
            labels_res.append(self.labels_result[i].text())

        if save_excel(self.labels_input_text, self.data_input, labels_res, self.results_tot, self.results_tot_h, self.results_tax, self.results_tax_h) == -1:
            dialog = QMessageBox()
            dialog.setWindowTitle("Error")
            dialog.setWindowIcon(QIcon("./res/matchlock.ico"))
            dialog.setIcon(QMessageBox.Icon.Critical)
            dialog.setText("Error saving data, wrong data")

            ok_button = dialog.addButton(QMessageBox.StandardButton.Ok)
            ok_button.clicked.connect(dialog.close)

            dialog.exec()