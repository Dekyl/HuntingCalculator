import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
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
        self.setWindowTitle("Sessions Viewer")
        
        layout = QVBoxLayout()
        self.table_view = QTableView()

        df: pd.DataFrame = pd.read_excel(file_path) # type: ignore

        layout.addWidget(self.table_view)

        self.setLayout(layout)
        self.show_dataframe(df)

    def show_dataframe(self, df: pd.DataFrame):
        """
        Convert a DataFrame to a QStandardItemModel and set it to the table view.
            :param df: The DataFrame to display.
        """
        model = QStandardItemModel()
        model.setColumnCount(len(df.columns))
        model.setHorizontalHeaderLabels([str(column) for column in df.columns])

        for row in df.itertuples(index=False):
            items: list[QStandardItem] = []
            for cell in row:
                if pd.isna(cell):
                    item = QStandardItem("") # No text if cell is NaN
                else:
                    item = QStandardItem(str(cell))
                items.append(item)
            model.appendRow(items)

        self.table_view.setModel(model)

        