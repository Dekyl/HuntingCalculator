import os

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt

from config.config import res_abs_paths

class TitleNewSession(QWidget):
    """
    A widget that displays the title and icon for a new session in the hunting calculator application.
    This widget is used to indicate the hunting spot for which the session is being created.
    """
    def __init__(self, name_spot: str, spot_id_icon: str):
        """
        Create the title widget for the new session.
            :param name_spot: The name of the hunting spot.
            :param spot_id_icon: The ID of the icon associated with the hunting spot.
            :return: A QWidget containing the title and icon for the new session.
        """
        super().__init__()

        # Session title widget and layout
        title_layout = QHBoxLayout(self)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMaximumHeight(80)
        self.setObjectName("titleWidget")
        self.setStyleSheet("""
            #titleWidget {
                padding: 10px;
            }
        """)

        # Hunting zone title and icon
        hunting_zone_icon = QIcon(res_abs_paths[spot_id_icon]) if os.path.exists(res_abs_paths[spot_id_icon]) else QIcon(res_abs_paths["not_found_ico"])
        hunting_zone_name = QLabel(name_spot)
        hunting_zone_name.setFont(QFont("Arial", 24))
        hunting_zone_name.setContentsMargins(0, 0, 50, 0) # Add right margin to title label so it stays in center of screen after adding icon and spacing it
        hunting_zone_icon_label = QLabel()
        hunting_zone_icon_label.setContentsMargins(0, 0, 10, 0)  # Add some space between the icon and the label (right margin)
        hunting_zone_icon_label.setPixmap(hunting_zone_icon.pixmap(50, 50))
        title_layout.addWidget(hunting_zone_icon_label)
        title_layout.addWidget(hunting_zone_name)