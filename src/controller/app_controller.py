from PyQt6.QtCore import QThread

from logic.manage_excels import clean_sessions, save_session
from logic.logs import add_log
from logic.exchange_calculator import exchange_results
from logic.access_resources import update_confirm_dialog, get_show_confirm_clean, get_show_confirm_exit, get_spots_list, get_spot_loot, get_user_setting, get_spot_icon, get_no_market_items
from logic.get_results import results_total, results_h, results_taxed, results_taxed_h, get_percentage_item, get_results_tot_percentage, get_gains_per_item, calculate_elixirs_cost_hour
from logic.data_fetcher import DataFetcher
from interface.view_interface import ViewInterface

class AppController:
    """
    A controller class to manage the application logic and user interactions.
    This class is a singleton and should be accessed via the get_instance method.
    """
    _instance = None

    def __init__(self, view: ViewInterface):
        """
        Initialize the AppController with the main window.
            :param view: The main window of the application, implementing ViewInterface.
        """
        if AppController._instance is not None:
            raise Exception("This class is a singleton!")
        AppController._instance = self
        add_log("AppController initialized.", "info")
        self.view = view

    def on_clean_sessions_clicked(self):
        """
        Handle the clean sessions action.
            This method is called when the clean sessions button is clicked.
            It cleans the sessions and shows a message box with the result of the action.
        """
        result = clean_sessions()
        if result == 1:
            add_log(f"Clean sessions dialog selection -> {result} (Success)", "info")
            self.view.show_dialog_results("Sessions have been successfully cleaned.", "clean_sessions", result)
        elif result == 0:
            add_log(f"Clean sessions dialog selection -> {result}  (No elements found to delete)", "info")
            self.view.show_dialog_results("No saved sessions found. Nothing to clean.", "clean_sessions", result)
        elif result == -1:
            add_log(f"Clean sessions dialog selection -> {result}  (Error)", "error")
            self.view.show_dialog_results("An error occurred while cleaning sessions.", "clean_sessions", result)

    def on_clean_sessions_button(self):
        """
        Handle the clean sessions button click event.
            This method is called when the clean sessions button is clicked.
        """
        add_log("Clean sessions button clicked.", "info")
        show_confirm_clean = get_show_confirm_clean()

        if show_confirm_clean:
            add_log("Showing confirmation dialog for cleaning sessions.", "info")
            enable_confirm_message = self.view.show_dialog_confirmation("Are you sure you want to clean the sessions?", self.on_clean_sessions_clicked, "clean_sessios")
            update_confirm_dialog(enable_confirm_message, "clean_sessions")
        else:
            self.on_clean_sessions_clicked()
        
    def on_exit_button(self):
        """
        Handle the exit button click event.
        """
        add_log("Exit button clicked.", "info")
        show_confirm_exit = get_show_confirm_exit()

        if show_confirm_exit:
            add_log("Showing confirmation dialog for exiting app.", "info")
            enable_confirm_message = self.view.show_dialog_confirmation("Are you sure you want to exit?", lambda: self.view.close_window(), "exit")
            update_confirm_dialog(enable_confirm_message, "exit")
        else:
            self.view.close_window()

    def get_spots_list(self) -> list[str]:
        """
        Get the list of spots from the data file.
            :return: A list of spots.
        """
        return get_spots_list()
        
    def select_new_session(self, spot_name: str):
        """
        Handle the selection of a new hunting session.
            :param spot_name: The name of the hunting spot selected by the user.
        """
        add_log(f"Session selected: {spot_name}, retrieving data", "info")
        loot_ids = get_spot_loot(spot_name)
        self.view.set_ui_enabled(False)

        self.thread = QThread()
        self.worker = DataFetcher(
            spot_name,
            loot_ids,
            get_user_setting("elixir_ids"),
            get_user_setting("region"),
            get_user_setting("language")
        )

        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run) # type: ignore
        self.worker.finished.connect(self.on_data_retrieved) # type: ignore
        self.worker.finished.connect(self.thread.quit) # type: ignore
        self.worker.finished.connect(self.worker.deleteLater) # type: ignore
        self.thread.finished.connect(self.thread.deleteLater) # type: ignore

        self.thread.start()

    def on_data_retrieved(self, spot_name: str, data_retrieved: dict[str, list[tuple[str, int]]] | None):
        """
        Handle the data retrieval from the API.
            :param spot_name: The name of the hunting spot.
            :param data_retrieved: The data retrieved from the API, or None if an error occurred.
        """
        if data_retrieved is None:
            add_log(f"Error retrieving data for spot '{spot_name}'", "error")
            self.view.set_ui_enabled(True) # Re-enable the UI
            self.view.set_session_button_enabled(False) # Disable the new session button
            self.view.show_dialog_error("Error fetching data from API, too many requests, disabling new session button for 1 minute.")
            return
        
        id_icon = get_spot_icon(spot_name)
        if not id_icon:
            add_log(f"No icon found for spot '{spot_name}'", "error")
            self.view.set_ui_enabled(True) # Re-enable the UI
            self.view.show_dialog_error(f"Error fetching spot {spot_name} icon from JSON file.")
            return
        
        no_market_items = get_no_market_items(spot_name)
        if not no_market_items:
            add_log(f"No market items found for spot '{spot_name}'", "error")
            self.view.set_ui_enabled(True) # Re-enable the UI
            self.view.show_dialog_error(f"Error fetching no market items from JSON file.")
            return
        
        self.view.create_new_session_widget(
            spot_name,
            id_icon,
            no_market_items,
            data_retrieved['prices'],
            calculate_elixirs_cost_hour(data_retrieved['elixir_costs'])
        )
        self.view.set_ui_enabled(True)

    def on_exchange_hides(self, green_hides: str, blue_hides: str):
        """
        Handle the exchange of hides when the button is clicked.
            :param green_hides: The number of green hides to exchange.
            :param blue_hides: The number of blue hides to exchange.
        """
        if len(green_hides) == 0 or len(blue_hides) == 0:
            return
        try:
            res_exchange = exchange_results(int(green_hides), int(blue_hides))
            self.view.update_exchange_hides_results(res_exchange)
        except:
            return
        
    def save_session(self, labels_input_text: list[str], data_input: list[str], labels_res: list[str], results_tot: int, results_tot_h: int, results_tax: int, results_tax_h: int) -> int:
        """
        Save the results of a hunting session to an Excel file.
            :param labels_input_text: List of labels for the input data.
            :param data_input: List of input data values.
            :param labels_res: List of labels for the results.
            :param results_tot: Total results.
            :param results_tot_h: Total results per hour.
            :param results_tax: Results after tax.
            :param results_tax_h: Results after tax per hour.
            :return: 0 if successful, -1 if an error occurs.
        """
        return save_session(labels_input_text, data_input, labels_res, results_tot, results_tot_h, results_tax, results_tax_h)
    
    def get_results(self, data_input: list[str]) -> dict[str, int]:
        """
        Calculate the total results from the input data.
            :param data_input: List of input data values.
            :return: A dictionary containing the total results, results per hour, results after tax, and results after tax per hour.
        """
        return {"results_tot": results_total(data_input), "results_h": results_h(), "results_taxed": results_taxed(), "results_taxed_h": results_taxed_h()}
    
    def get_results_tot_percentage(self) -> int:
        """
        Get the total results percentage from the results.
            :return: The total results percentage.
        """
        return get_results_tot_percentage()
    
    def get_gains_per_item(self) -> list[int]:
        """
        Get the gains per item from the results.
            :return: A list of gains per item.
        """
        return get_gains_per_item()
    
    def get_percentage_item(self, item: str, gains_item: int, results_tot_percentage: int) -> str:
        """
        Get the gains per item from the results.
            :param item: The name of the item.
            :param gains_item: The gains for the specific item.
            :param results_tot_percentage: The total results percentage.
            :return: A string containing the item name and its percentage of total gains.
        """
        return get_percentage_item(item, gains_item, results_tot_percentage)

    @staticmethod
    def get_instance() -> "AppController":
        """
        Get the singleton instance of AppController.
            :return: The singleton instance of AppController.
        """
        if AppController._instance is None:
            raise Exception("AppController instance not created. Call AppController first.")
        return AppController._instance