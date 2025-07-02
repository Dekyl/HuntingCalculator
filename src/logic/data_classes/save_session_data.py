from dataclasses import dataclass

@dataclass
class SaveSessionData:
    """
    Data class to hold information for saving a hunting session.
    This class is used to store the necessary information required to save a session's results.
    """
    name_spot: str
    res_name: list[str]
    res_data: list[str]
    labels_res: list[str]
    total_res: int
    total_res_h: int
    taxed_res: int
    taxed_res_h: int
    user_action: str