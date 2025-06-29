from PySide6.QtWidgets import QPushButton, QLineEdit

from dataclasses import dataclass
from typing import Callable

@dataclass
class SessionInputCallbacks:
    get_no_name_percent: Callable[[str], str]
    get_save_button: Callable[[], QPushButton]
    get_input_results: Callable[[], list[QLineEdit]]
    get_elixirs_cost_line_edit: Callable[[], QLineEdit]
    get_user_action_line_edit: Callable[[], QLineEdit]
