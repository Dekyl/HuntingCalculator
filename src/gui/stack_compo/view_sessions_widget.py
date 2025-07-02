import pandas as pd

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QTableView, 
    QPushButton, 
    QSizePolicy, 
    QLabel
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt

from controllers.app_controller import AppController
from config.config import scroll_bar_style, res_abs_paths

class ViewSessionsWidget(QWidget):
    """
    Widget to view sessions in a table format.
    This widget reads session data from an Excel file and displays it in a table.
    """
    def __init__(self,  file_path: str):
        """
        Initialize the ViewSessionsWidget.
            :param file_path: Path to the Excel file containing session data.
        """
        super().__init__()

        controller = AppController.get_instance()
        
        session_layout = QVBoxLayout()
        self.setLayout(session_layout)
        session_layout.setSpacing(5)
        session_layout.setContentsMargins(20, 20, 20, 20)

        label_title = QLabel(file_path.split('/')[-1])
        label_title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        label_title.setStyleSheet("""
            color: white;
            background-color: rgb(50, 50, 50);
            padding: 10px;
            border-radius: 10px;
            border: 2px solid rgb(80, 80, 80);
        """)
        label_title.setMinimumWidth(800)
        label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        session_layout.addWidget(label_title, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        table_view = QTableView()
        table_view.setFont(QFont("Arial", 12))
        table_view.setStyleSheet(f"""
            QTableView {{
                background-color: rgb(30, 30, 30);
                border: 2px solid rgb(200, 200, 200);
                border-radius: 5px;
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
        table_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table_view.setMaximumHeight(800)

        delete_session_button = QPushButton("Delete Session")
        delete_session_button.setStyleSheet("""
            QPushButton {
                background-color: rgb(180, 30, 30);
                color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgb(200, 60, 60);
            }
            QPushButton:pressed {
                background-color: rgb(220, 90, 90);
            }
        """)
        
        delete_session_button.setFont(QFont("Arial", 16))
        delete_session_button.clicked.connect(lambda: controller.delete_session_controller(file_path))
        delete_session_button.setMaximumWidth(300)
        delete_session_button.setMinimumHeight(50)

        button_container = QWidget()
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 30, 0, 0)
        button_layout.addWidget(delete_session_button, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        button_container.setLayout(button_layout)

        session_layout.addWidget(table_view, 0)
        session_layout.addWidget(button_container, 0, Qt.AlignmentFlag.AlignBottom)

        df: pd.DataFrame = pd.read_excel(file_path)  # type: ignore
        self.show_dataframe(df, table_view)

        table_view.resizeColumnsToContents() # Automatically resize columns to fit content

    def show_dataframe(self, df: pd.DataFrame, table_view: QTableView):
        """
        Convert a DataFrame to a QStandardItemModel and set it to the table view.
            :param df: The DataFrame to display.
            :param table_view: The QTableView to set the model on.
        """
        model = QStandardItemModel()
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels([str(column) for column in df.columns])

        font_header = QFont("Arial", 12, QFont.Weight.Bold)
        for col in range(model.columnCount()):
            header_item = model.horizontalHeaderItem(col)
            if header_item:
                header_item.setFont(font_header)

        for row in df.itertuples(index=False):
            items: list[QStandardItem] = []
            for cell in row:
                if pd.isna(cell):
                    item = QStandardItem("") # No text if cell is NaN
                elif isinstance(cell, float) and cell.is_integer():
                    item = QStandardItem(str(int(cell))) # Show as integer if no decimals
                elif isinstance(cell, float):
                    item = QStandardItem(f"{cell:,.2f}") # Set number format with thousands separator
                else:
                    item = QStandardItem(str(cell))
                    
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                items.append(item)
            model.appendRow(items)

        table_view.setModel(model)
