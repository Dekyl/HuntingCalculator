from typing import Any
import math

from logic.logs import add_log
from logic.exchange_calculator import exchange_results
from logic.data_classes.session_results import SessionResultsData
from config.config import (
    FlatDict, 
    n_damaged_hide_exchange, 
    n_usable_hide_exchange, 
    n_magical_lightstone_exchange,
    n_magical_lightstones_scroll,
    n_remnants_of_mystic_beasts_exchange,
    n_supreme_hide_scroll,
    value_pack_multiplier,
    extra_profit_multiplier
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
        if self.auto_calculate_best_profit:
            self.exchange_wildsparks()  # Exchange wildsparks if auto calculate best profit is enabled
            if self.exchange_data_best_profit() == -1:
                add_log(f"Error exchanging data for best profit calculation for spot: {self.name_spot}.", "error")
                return -1

        self.total_no_elixirs = self.results_total() if self.hours_digit > 0 else 0  # Calculate total results only if hours is greater than 0
        
        self.value_pack_val = value_pack_multiplier if self.value_pack else 0  # Set value pack multiplier if value pack is active, otherwise set to 0
        self.value_pack_val += extra_profit_multiplier if self.extra_profit else 0  # Add extra profit multiplier if extra profit is active, otherwise add 0

        total_h = self.results_h() if self.hours_digit > 0 else 0  # Calculate total results per hour only if hours is greater than 0
        self.taxed = self.results_taxed() if self.hours_digit > 0 else 0 # Apply market tax, value pack and extra profit if applicable if hours is greater than 0
        taxed_h = self.results_taxed_h() if self.hours_digit > 0 else 0  # Calculate taxed results per hour only if hours is greater than 0
        total_elixirs_cost = self.get_total_elixirs_cost()  # Get the total cost of elixirs for the session

        total = self.total_no_elixirs - total_elixirs_cost  # Subtract elixirs cost
        self.taxed -= total_elixirs_cost  # Subtract elixirs cost after tax
        total_h -= self.elixirs_cost_h # Subtract elixirs cost per hour
        taxed_h -= self.elixirs_cost_h # Subtract elixirs cost per hour after tax

        user_inputs = ["Breath of Narcion", "Breath of Narcion Previous", "Usable Hide", "Damaged Hide", "Supreme Hide", f"St. {self.name_spot} Head", "Wildspark", "Black Gem Frag.",]
        for key in user_inputs: # Restore original data input values for specific keys that were changed during calculations
            if key in original_data_input:
                self.data_input[key] = original_data_input[key]

        return {
            'total': total,
            'total_h': total_h,
            'taxed': self.taxed,
            'taxed_h': taxed_h,
            'new_labels_input_text': self.recalculate_labels_input(),
            'elixirs_cost': str(f"{total_elixirs_cost:,}"),
            'new_data_input': self.data_input
        }
    
    def exchange_data_best_profit(self) -> int:
        """
        Exchange data for best profit calculation in the input data.
            :return: 0 if successful, -1 if an error occurs.
        """
        items_of_interest = {
            'Breath of Narcion': self.data_input.get('Breath of Narcion', ("", "0")),
            f'St. {self.name_spot} Head': self.data_input.get(f'St. {self.name_spot} Head', ("", "0")),
            f'M. St. {self.name_spot} Head': (self.data_input.get(f'M. St. {self.name_spot} Head', ("", "0"))[0], "0"),
            f'M. Sp. St. {self.name_spot} Head': (self.data_input.get(f'M. Sp. St. {self.name_spot} Head', ("", "0"))[0], "0"),
            'Damaged Hide': self.data_input.get('Damaged Hide', ("", "0")),
            'Usable Hide': self.data_input.get('Usable Hide', ("", "0")),
            'Supreme Hide': self.data_input.get('Supreme Hide', ("", "0")),
            'BMB: All AP': (self.data_input.get('BMB: All AP', ("", "0"))[0], "0"),
            'BMB: Accuracy': (self.data_input.get('BMB: Accuracy', ("", "0"))[0], "0"),
            'BMB: Damage Reduction': (self.data_input.get('BMB: Damage Reduction', ("", "0"))[0], "0"),
            'BMB: Evasion': (self.data_input.get('BMB: Evasion', ("", "0"))[0], "0"),
            'BMB: Max HP': (self.data_input.get('BMB: Max HP', ("", "0"))[0], "0")
        }

        # Profit Breath of Narcion
        res_of_interest_b_o_n = items_of_interest.copy()
        breath_of_narcion_profit = self.get_profit_breath_of_narcion(res_of_interest_b_o_n) # Get profit from Breath of Narcion
        # Profit BMB
        self.lowest_cost_imperfects = self.get_lowest_cost_imperfects() # Get the lowest cost of imperfect lightstones
        res_of_interest_bmb = items_of_interest.copy()
        bmb_profit = self.get_profit_bmb(res_of_interest_bmb) # Get profit from Blessing of Mystic Beasts (BMB)

        # Profit Normal yellow head with previous bmb
        res_of_interest_bmb_n_y_h = res_of_interest_bmb.copy()
        bmb_normal_yellow_profit = self.get_profit_normal_yellow_head(res_of_interest_bmb_n_y_h, f'St. {self.name_spot} Head', f'M. St. {self.name_spot} Head')
        # Profit Special yellow head with previous bmb
        res_of_interest_bmb_s_y_h = res_of_interest_bmb_n_y_h.copy()
        bmb_special_yellow_profit = self.get_profit_special_yellow_head(res_of_interest_bmb_s_y_h, f'M. St. {self.name_spot} Head', f'M. Sp. St. {self.name_spot} Head')

        # Profit Normal yellow head without previous bmb
        res_of_interest_n_y_h = items_of_interest.copy()
        normal_yellow_head_profit = self.get_profit_normal_yellow_head(res_of_interest_n_y_h, f'St. {self.name_spot} Head', f'M. St. {self.name_spot} Head')
        # Profit Special yellow head without previous bmb
        res_of_interest_s_y_h = res_of_interest_n_y_h.copy()
        special_yellow_head_profit = self.get_profit_special_yellow_head(res_of_interest_s_y_h, f'M. St. {self.name_spot} Head', f'M. Sp. St. {self.name_spot} Head')
        
        best_profits: dict[str, tuple[int, dict[str, tuple[str, str]]]] = {
            "Breath of Narcion": (breath_of_narcion_profit, res_of_interest_b_o_n),
            "Normal Yellow Heads": (normal_yellow_head_profit, res_of_interest_n_y_h),
            "Special Yellow Heads": (special_yellow_head_profit, res_of_interest_s_y_h),
            "Normal Yellow Heads with BMB": (bmb_normal_yellow_profit, res_of_interest_bmb_n_y_h),
            "Special Yellow Heads with BMB": (bmb_special_yellow_profit, res_of_interest_bmb_s_y_h),
            "BMB": (bmb_profit, res_of_interest_bmb)
        }

        max_key = max(best_profits, key=lambda k: best_profits[k][0]) # Get the key with the maximum profit
        max_result = best_profits[max_key][1]  # Get the result with the maximum profit

        return self.update_data_input(max_result) # Update the input data with the maximum profit value

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

            price = price.replace(',', '').replace(' ', '') if price != '' else '0' # Remove commas and spaces
            amount = amount.replace(',', '').replace(' ', '') if amount != '' else '0' # Remove commas and spaces
            total += int(amount) * int(price)

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
        new_labels_input_text: list[str] = []
        for name, (price, amount) in self.data_input.items():
            if name == 'Hours':
                new_labels_input_text.append(name)
            else:
                price = price.replace(',', '').replace(' ', '') if price != '' else '0' # Remove commas and spaces for validation
                amount = amount.replace(',', '').replace(' ', '') if amount != '' else '0' # Remove commas and spaces for validation
                item_total = int(price) * int(amount)
                percent = (item_total / self.total_no_elixirs) * 100 if self.total_no_elixirs > 0 else 0
                if percent > 100:
                    percent = 100.0
                new_labels_input_text.append(f"{name} ({percent:.2f}%)")

        return new_labels_input_text

    def get_amount_val_data(self, data: dict[str, tuple[str, str]], name_key: str) -> int:
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

    def exchange_wildsparks(self):
        """
        Exchange Wildsparks to Black Gem Fragments in the input data.
            :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        """
        wildspark = self.get_amount_val_data(self.data_input, 'Wildspark')  # Get current wildspark value
        black_gem_fragment = self.get_amount_val_data(self.data_input, 'Black Gem Frag.')  # Get current black gem fragment value

        n_exchanges = wildspark // 10 # 10 Wildsparks can be exchanged for 5 Black Gem Fragment
        wildspark %= 10 # Remaining Wildsparks after exchange
        black_gem_fragment += n_exchanges * 5

        self.data_input['Black Gem Frag.'] = (self.data_input["Black Gem Frag."][0], str(black_gem_fragment)) # Update Black Gem Fragment
        self.data_input['Wildspark'] = (self.data_input["Wildspark"][0], str(wildspark)) # Update Wildspark

    def get_profit_items_interest(self, items_of_interest: dict[str, tuple[str, str]]) -> int:
        """
        Calculate the profit from the items of interest based on the input data.
            :param items_of_interest: A dictionary containing the items of interest with their prices and amounts.
            :return: The total profit from the items of interest.
        """
        profit = 0
        for _, (price, amount) in items_of_interest.items():
            profit += int(price.replace(',', '').replace(' ', '')) * int(amount.replace(',', '').replace(' ', '')) if price and amount else 0
        return profit

    def update_data_input(self, max_val: dict[str, tuple[str, str]]) -> int:
        """
        Update the input data with the maximum profit value.
            :param max_val: A dictionary containing the maximum profit value.
            :return: 0 if successful, -1 if an error occurs.
        """
        for name, (price, amount) in max_val.items():
            if name in self.data_input:
                self.data_input[name] = (price, amount)  # Update existing item
            else:
                add_log(f"Error updating data input with maximum profit value: {name} not found in data", "error")
                return -1
            
        return 0

    def get_profit_breath_of_narcion(self, items_of_interest: dict[str, tuple[str, str]]) -> int:
        """
        Calculate the profit from the Breath of Narcion based on the input data.
            :param items_of_interest: A dictionary containing the items of interest with their prices and amounts.
            :return: The profit from the Breath of Narcion.
        """
        return self.get_profit_items_interest(items_of_interest)

    def get_profit_normal_yellow_head(self, items_of_interest: dict[str, tuple[str, str]], green_head_name: str, normal_yellow_head_name: str) -> int:
        """
        Calculate the profit from the Normal Yellow Head based on the input data.
            :param items_of_interest: A dictionary containing the items of interest with their prices and amounts.
            :param green_head_name: The name of the Green Head item.
            :param normal_yellow_head_name: The name of the Normal Yellow Head item.
            :return: The profit from the Normal Yellow Head.
        """
        n_damaged_hide = self.get_amount_val_data(items_of_interest, 'Damaged Hide')  # Get the number of Damaged Hides
        n_usable_hide = self.get_amount_val_data(items_of_interest, 'Usable Hide')  # Get the number of Usable Hides
        n_supreme_hide = self.get_amount_val_data(items_of_interest, 'Supreme Hide')  # Get the number of Supreme Hides

        n_usable_hide += n_supreme_hide * 2

        _, n_damaged_hide, n_usable_hide = exchange_results(n_damaged_hide, n_usable_hide) # Exchange usable hide to damaged hide so number of them is equal to maximize profit

        n_heads_damaged_hide, remaining_damaged_hide = divmod(n_damaged_hide, n_damaged_hide_exchange) # 60 Damaged Hides can be exchanged for 1 Normal Yellow Head
        n_heads_usable_hide, remaining_usable_hide = divmod(n_usable_hide, n_usable_hide_exchange) # 50 Usable Hides can be exchanged for 1 Normal Yellow Head
        green_heads = self.get_amount_val_data(items_of_interest, green_head_name) # Get the number of Green Heads

        n_normal_yellow_head = min(n_heads_damaged_hide, n_heads_usable_hide, green_heads) # The number of Normal Yellow Heads is the minimum of the two exchanges

        items_of_interest[green_head_name] = (items_of_interest[green_head_name][0], str(green_heads - n_normal_yellow_head)) # Update Green Heads amount

        items_of_interest[normal_yellow_head_name] = (items_of_interest[normal_yellow_head_name][0], str(n_normal_yellow_head)) # Update Normal Yellow Head
        items_of_interest['Damaged Hide'] = (items_of_interest['Damaged Hide'][0], str(remaining_damaged_hide)) # Update Damaged Hide
        items_of_interest['Usable Hide'] = (items_of_interest['Usable Hide'][0], str(remaining_usable_hide)) # Update Usable Hide

        return self.get_profit_items_interest(items_of_interest)  # Return the profit from the items of interest

    def get_profit_special_yellow_head(self, items_of_interest: dict[str, tuple[str, str]], normal_yellow_head_name: str, special_yellow_head_name: str) -> int:
        """
        Calculate the profit from the Special Yellow Head based on the input data.
            :param items_of_interest: A dictionary containing the items of interest with their prices and amounts.
            :param normal_yellow_head_name: The name of the Normal Yellow Head item.
            :param special_yellow_head_name: The name of the Special Yellow Head item.
            :return: The profit from the Special Yellow Head.
        """
        n_normal_yellow_head = self.get_amount_val_data(items_of_interest, normal_yellow_head_name)  # Get the number of Normal Yellow Heads
        n_breath_of_narcion = self.get_amount_val_data(items_of_interest, 'Breath of Narcion')  # Get the number of Breath of Narcion

        n_breath_of_narcion, remaining_breath_of_narcion = divmod(n_breath_of_narcion, 2)  # 2 Breath of Narcion can be exchanged for 1 Special Yellow Head
        n_special_yellow_head = min(n_normal_yellow_head, n_breath_of_narcion)  # 2 Breath of Narcion can be exchanged for 1 Special Yellow Head

        items_of_interest[special_yellow_head_name] = (items_of_interest[special_yellow_head_name][0], str(n_special_yellow_head)) # Update Special Yellow Head
        items_of_interest[normal_yellow_head_name] = (items_of_interest[normal_yellow_head_name][0], str(n_normal_yellow_head - n_special_yellow_head)) # Update Normal Yellow Head
        items_of_interest['Breath of Narcion'] = (items_of_interest['Breath of Narcion'][0], str(remaining_breath_of_narcion)) # Update Breath of Narcion

        return self.get_profit_items_interest(items_of_interest)  # Return the profit from the items of interest

    def get_lowest_cost_imperfects(self) -> int:
        """
        Get the name of the lightstone with the lowest cost.
            :return: The lowest lightstone cost.
        """
        return min(v[1] for v in self.lightstone_costs.values())

    def get_profit_bmb(self, items_of_interest: dict[str, tuple[str, str]]) -> int:
        """
        Calculate the profit from the Blessing of Mystic Beasts (BMB) based on the input data.
            :param items_of_interest: A dictionary containing the items of interest with their prices and amounts.
            :return: The profit from the Blessing of Mystic Beasts (BMB).
        """
        scroll_lightstone = {
            'BMB: All AP': 'Lightstone of Fire: Rage',
            'BMB: Accuracy': 'Lightstone of Fire: Marked',
            'BMB: Damage Reduction': 'Lightstone of Earth: Iron Wall',
            'BMB: Evasion': 'Lightstone of Earth: Waves',
            'BMB: Max HP': 'Lightstone of Wind: Heart'
        }

        prices_scrolls = {
            'BMB: All AP': int(items_of_interest['BMB: All AP'][0].replace(',', '').replace(' ', '')) if items_of_interest['BMB: All AP'][0] else 0,
            'BMB: Accuracy': int(items_of_interest['BMB: Accuracy'][0].replace(',', '').replace(' ', '')) if items_of_interest['BMB: Accuracy'][0] else 0,
            'BMB: Damage Reduction': int(items_of_interest['BMB: Damage Reduction'][0].replace(',', '').replace(' ', '')) if items_of_interest['BMB: Damage Reduction'][0] else 0,
            'BMB: Evasion': int(items_of_interest['BMB: Evasion'][0].replace(',', '').replace(' ', '')) if items_of_interest['BMB: Evasion'][0] else 0,
            'BMB: Max HP': int(items_of_interest['BMB: Max HP'][0].replace(',', '').replace(' ', '')) if items_of_interest['BMB: Max HP'][0] else 0
        }

        lightstones_id_names = {name: lightstone_id for lightstone_id, (name, _) in self.lightstone_costs.items()}

        prices_lightstones = {
            'Lightstone of Fire: Rage': self.lightstone_costs[lightstones_id_names['Lightstone of Fire: Rage']][1],
            'Lightstone of Fire: Marked': self.lightstone_costs[lightstones_id_names['Lightstone of Fire: Marked']][1],
            'Lightstone of Earth: Iron Wall': self.lightstone_costs[lightstones_id_names['Lightstone of Earth: Iron Wall']][1],
            'Lightstone of Earth: Waves': self.lightstone_costs[lightstones_id_names['Lightstone of Earth: Waves']][1],
            'Lightstone of Wind: Heart': self.lightstone_costs[lightstones_id_names['Lightstone of Wind: Heart']][1]
        }

        most_profitable_scroll_name, max_profit_scroll = max(
            ((scroll, prices_scrolls.get(scroll, 0))
            for scroll in scroll_lightstone),
            key=lambda x: x[1],
            default=("", 0)
        )

        # Calculate how many scrolls can be crafted
        n_supreme_hide = self.get_amount_val_data(items_of_interest, 'Supreme Hide')  # Get the number of Supreme Hides
        n_imperfect_lightstones_scroll = math.ceil(n_magical_lightstones_scroll / n_magical_lightstone_exchange)
        cost_magical_lightstones_scroll = n_imperfect_lightstones_scroll * self.lowest_cost_imperfects  # Cost of magical lightstones per scroll
        cost_lightstone_scroll = prices_lightstones[scroll_lightstone[most_profitable_scroll_name]] # Cost of lightstone per scroll
        breath_of_narcion_cost = int(items_of_interest.get("Breath of Narcion", ("", "0"))[0].replace(',', '').replace(' ', '')) or 0  # Breath of Narcion cost
        cost_remnants_scroll = math.ceil(breath_of_narcion_cost / n_remnants_of_mystic_beasts_exchange) # Cost of remnants of mystic beasts per scroll

        # Profit per scroll using supreme hides
        profit_scroll = max_profit_scroll - cost_lightstone_scroll - cost_magical_lightstones_scroll - cost_remnants_scroll
        n_scrolls = n_supreme_hide // n_supreme_hide_scroll  # Number of scrolls that can be crafted from supreme hides

        items_of_interest[most_profitable_scroll_name] = (items_of_interest[most_profitable_scroll_name][0], str(n_scrolls))  # Update the number of scrolls crafted
        items_of_interest['Supreme Hide'] = (items_of_interest['Supreme Hide'][0], str(n_supreme_hide - n_scrolls * n_supreme_hide_scroll))  # Update the number of supreme hides left

        return profit_scroll * n_scrolls if n_scrolls > 0 and profit_scroll > 0 else 0  # Total profit from scrolls