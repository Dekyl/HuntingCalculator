from PySide6.QtWidgets import QLabel, QLineEdit
from PySide6.QtGui import QIcon

from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class SaveSessionCallbacks:
    get_labels_result: Callable[[], list[QLabel]]
    get_inputs_result: Callable[[], list[QLineEdit]]
    get_labels_icons_input: Callable[[], list[tuple[Optional[QIcon], QLabel, Optional[QLabel]]]]
    get_line_edit_inputs: Callable[[], dict[str, QLineEdit]]
    get_no_name_percent: Callable[[str], str]
    get_user_action: Callable[[], str]
