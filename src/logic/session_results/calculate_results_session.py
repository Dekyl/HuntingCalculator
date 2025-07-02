from typing import Any

from logic.logs import add_log
from logic.session_results.calculate_max_profit import CalculateMaxProfit
from logic.data_classes.session_results import SessionResultsData
from config.config import (
    FlatDict,
    value_pack_multiplier,
    extra_profit_multiplier,
    FlatDictStr
)

def calculate_elixirs_cost_hour(elixirs: FlatDict) -> str:
    """
    Calculate the cost of elixirs per hour based on the provided elixirs data.
        :param elixirs: A dictionary containing elixir id: (name and cost).
        :return: The total cost of elixirs per hour.
    """
    cost_elixirs = 0
    for _, (name, cost) in elixirs.items():
        if "Whale" in name:
            cost *= 6
        elif "Perfume" in name:
            cost *= 3 # Perfumes cost 3 times more (3 perfumes per hour)
        else:
            cost *= 4 # Other elixirs cost 4 times more (4 elixirs per hour)
        cost_elixirs += cost

    return str(f"{cost_elixirs:,}")

class CalculateResultsSession:
    """
    Class to calculate the results of a hunting session based on the provided session results data.
    This class takes the session results data and performs calculations to determine the total profit, taxed profit, and other relevant metrics.
    """
    def __init__(self, session_results: SessionResultsData):
        """
        Initialize the CalculateResultsSession with the provided session results data.
            :param session_results: An instance of SessionResultsData containing the necessary data for the session.
        """
        self.session_results = session_results  # Store the session results data
        self.data_input = session_results.data_input  # Get the data input from the session results
        self.name_spot = session_results.name_spot  # Get the name of the hunting spot
        self.auto_calculate_best_profit = session_results.auto_calculate_best_profit  # Get the auto calculate best profit flag
        self.data_input = session_results.data_input  # Get the data input from the session results
        self.lightstone_costs = session_results.lightstone_costs  # Get the lightstone costs from the session results
        self.imperfect_lightstone_costs = session_results.imperfect_lightstone_costs  # Get the imperfect lightstone costs from the session results
        self.value_pack = session_results.value_pack  # Get the value pack flag from the session results
        self.market_tax = session_results.market_tax  # Get the market tax from the session results
        self.extra_profit = session_results.extra_profit  # Get the extra profit flag from the session results
        self.hours = self.session_results.data_input.get('Hours', ("", "0"))[1] or "0" # If 'Hours' is not in data_input or if it is empty, default to "0"
        self.elixirs_cost = self.session_results.elixirs_cost.replace(',', '').replace(' ', '')  # Remove commas and spaces for validation
        self.black_stone_cost = [v[1] for v in session_results.black_stone_cost.values() if v[0] == 'Black Stone'][0]

    def calculate_results_session(self) -> dict[str, Any] | int:
        """ 
        Calculate the results of a hunting session based on the provided session results data.
            :return: A dictionary containing the results of the session or -1 if an error occurs
        """
        if not self.elixirs_cost.isdigit():
            add_log(f"Invalid elixirs cost: {self.elixirs_cost}. Expected a number.", "error")
            return -1
        
        if not self.hours.isdigit():
            add_log(f"Invalid hours: {self.hours}. Expected a number.", "error")
            return -1
        
        self.hours_digit = int(self.hours)
        self.elixirs_cost_h = int(self.elixirs_cost) if self.hours_digit > 0 else 0  # Elixirs cost per hour, if hours is 0, set to 0

        if not self.check_data_input():
            return -1  # Check if the input data is valid
        
        original_data_input = self.data_input.copy()  # Keep a copy of the original data input for restoring some values later
        self.exchange_breath_of_narcion() # Add breath of narcion previous to actual breath of narcion

        self.value_pack_val = value_pack_multiplier if self.value_pack else 0  # Set value pack multiplier if value pack is active, otherwise set to 0
        self.value_pack_val += extra_profit_multiplier if self.extra_profit else 0  # Add extra profit multiplier if extra profit is active, otherwise add 0

        total_elixirs_cost = self.get_total_elixirs_cost()  # Get the total cost of elixirs for the session

        if not self.auto_calculate_best_profit: # No auto calculate best profit, just calculate total results
            self.total_no_elixirs = self.results_total() if self.hours_digit > 0 else 0 # Calculate total results without elixirs cost

            total_h = self.results_h() if self.hours_digit > 0 else 0  # Calculate total results per hour only if hours is greater than 0
            self.taxed = self.results_taxed() if self.hours_digit > 0 else 0 # Apply market tax, value pack and extra profit if applicable if hours is greater than 0
            taxed_h = self.results_taxed_h() if self.hours_digit > 0 else 0  # Calculate taxed results per hour only if hours is greater than 0

            total = self.total_no_elixirs - total_elixirs_cost  # Subtract elixirs cost
            self.taxed -= total_elixirs_cost  # Subtract elixirs cost after tax
            total_h -= self.elixirs_cost_h # Subtract elixirs cost per hour
            taxed_h -= self.elixirs_cost_h # Subtract elixirs cost per hour after tax

            self.restore_data_input(original_data_input)  # Restore the original data input values

            return {
                'total': total,
                'total_h': total_h,
                'taxed': self.taxed,
                'taxed_h': taxed_h,
                'new_labels_input_text': self.recalculate_labels_input(),
                'elixirs_cost': str(f"{total_elixirs_cost:,}"),
                'action_user': ''
            }

        max_profit = CalculateMaxProfit(self.data_input, 
                                        self.lightstone_costs, 
                                        self.imperfect_lightstone_costs, 
                                        self.black_stone_cost, 
                                        self.hours_digit, 
                                        self.value_pack_val, 
                                        self.market_tax,
                                        total_elixirs_cost,
                                        self.elixirs_cost_h)
        result_max_profit = max_profit.calculate_max_profit()
        self.restore_data_input(original_data_input)  # Restore the original data input values
        return result_max_profit  # Return the result of the maximum profit calculation

    def restore_data_input(self, original_data_input: FlatDictStr):
        """
        Restore the original data input values after calculations for some inputs that must keep their states.
            :param original_data_input: A dictionary containing the original data input values.
        """
        user_inputs = ["Breath of Narcion", "Breath of Narcion Previous", "Usable Hide", "Damaged Hide", "Supreme Hide", f"St. {self.name_spot} Head", "Wildspark", "Black Gem Frag.", f"St. {self.name_spot}"]
        for key in user_inputs: # Restore original data input values for specific keys that were changed during calculations
            if key in original_data_input:
                self.data_input[key] = original_data_input[key]

    def check_data_input(self) -> bool:
        """
        Check if the input data is valid.
            :return: True if the input data is valid, False otherwise.
        """
        for name, (price, amount) in self.data_input.items():
            if name == 'Hours':
                continue  # Skip hours as it is not an item

            price = price.replace(',', '').replace(' ', '') if price != '' else '0' # Remove commas and spaces for validation, default to '0' if empty
            amount = amount.replace(',', '').replace(' ', '') if amount != '' else '0' # Remove commas and spaces for validation, default to '0' if empty
            
            if not price.isdigit() or not amount.isdigit():
                add_log(f"Invalid input data for {name}: price '{price}' or amount '{amount}' is not a valid number.", "error")
                return False
        return True

    def get_total_elixirs_cost(self) -> int:
        """
        Calculate the total cost of elixirs for the session based on the cost per hour and the number of hours.
            :return: The total cost of elixirs for the session.
        """
        return self.elixirs_cost_h * self.hours_digit

    def results_total(self) -> int:
        """
        Calculate the total results from the session based on the input data.
            :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
            :return: The total results from the session.
        """
        total = 0
        for name, (price, amount) in self.data_input.items():
            if name == 'Hours':
                continue  # Skip hours as it is not an item

            price = int(price.replace(',', '').replace(' ', '')) if price != '' else 0 # Remove commas and spaces
            amount = int(amount.replace(',', '').replace(' ', '')) if amount != '' else 0 # Remove commas and spaces
            total += amount * price

        return total

    def results_h(self) -> int:
        """
        Calculate the total results per hour.
            :return: The total results per hour.
        """
        return int(self.total_no_elixirs / self.hours_digit)

    def results_taxed(self) -> int:
        """
        Calculate the results after applying market tax and value pack.
            :param total: The total results from the session.
            :param market_tax: The market tax percentage to apply.
            :param value_pack: The value pack percentage to apply.
            :return: The total results after tax and value pack.
        """
        taxed = self.total_no_elixirs * (1 - self.market_tax)
        taxed += taxed * self.value_pack_val  # Apply value pack multiplier
        return int(taxed)

    def results_taxed_h(self) -> int:
        """
        Calculate the results after tax per hour.
            :param taxed: The total results after tax and value pack.
            :return: The total results after tax per hour.
        """
        return int(self.taxed / self.hours_digit)

    def recalculate_labels_input(self) -> list[str]:
        """
        Recalculate the labels for input data based on the total results.
            :return: A list of recalculated labels for input data.
        """
        total_percent = 0.0
        new_labels_input_text: list[str] = []
        for name, (price, amount) in self.data_input.items():
            if name == 'Hours':
                new_labels_input_text.append(name)
            else:
                price = int(price.replace(',', '').replace(' ', '')) if price != '' else 0 # Remove commas and spaces for validation
                amount = int(amount.replace(',', '').replace(' ', '')) if amount != '' else 0 # Remove commas and spaces for validation

                if name == 'Breath of Narcion':
                    amount_breath_of_narcion_prev = self.get_amount_val_data(self.data_input, 'Breath of Narcion Previous')  # Get the previous breath of narcion amount
                    amount += amount_breath_of_narcion_prev  # Add the previous breath of narcion amount to the current one
                elif name == "Breath of Narcion Previous":
                    new_labels_input_text.append(f"{name} ({0:.2f}%)")
                    continue  # Skip previous breath of narcion as it is used in Breath of Narcion calculation

                item_total = price * amount

                percent = (item_total / self.total_no_elixirs) * 100 if self.total_no_elixirs > 0 else 0
                if percent > 100:
                    percent = 100.0
                total_percent += percent  # Add the percentage to the total percentage
                new_labels_input_text.append(f"{name} ({percent:.2f}%)")

        return new_labels_input_text

    def get_amount_val_data(self, data: FlatDictStr, name_key: str) -> int:
        """
        Get the amount value from the input data based on the provided name key.
            :param data: A dictionary containing the input data for the session. (name: (price, amount))
            :param name_key: The key to look for in the input data.
            :return: The amount value as an integer, or 0 if not found / the value is empty.
        """
        value = data.get(name_key, ("", "0"))[1]
        cleaned = value.replace(',', '').replace(' ', '')
        return int(cleaned) if cleaned and cleaned != '0' else 0

    def exchange_breath_of_narcion(self):
        """
        Exchange the previous Breath of Narcions to the current one in the input data.
            :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        """
        breath_of_narc = self.get_amount_val_data(self.data_input, 'Breath of Narcion')  # Get current breath of narcion
        breath_of_narc_prev = self.get_amount_val_data(self.data_input, 'Breath of Narcion Previous')  # Get current breath of narcion

        self.data_input['Breath of Narcion Previous'] = (self.data_input["Breath of Narcion Previous"][0], "0") # Update previous breath of narcion
        self.data_input['Breath of Narcion'] = (self.data_input["Breath of Narcion"][0], str(breath_of_narc + breath_of_narc_prev)) # Update current breath of narcion