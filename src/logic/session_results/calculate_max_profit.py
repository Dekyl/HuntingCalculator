from typing import Any
import math

from config.config import (
    n_fragment_exchange, 
    n_black_stone_exchange, 
    n_sharp_exchange_concentrate, 
    n_black_gem_concentrate_gem_exchange, 
    n_sharp_exchange_concentrate_gem,
    n_damaged_hide_exchange,
    n_usable_hide_exchange,
    n_supreme_exchange,
    n_breath_of_narcion_exchange,
    n_supreme_hide_scroll,
    n_magical_lightstone_exchange,
    n_magical_lightstones_scroll,
    n_remnants_of_mystic_beasts_exchange,
    n_scrolls_lighstone,
    FlatDictInt,
    FlatDict,
    FlatDictStr,
    TupleContributions
)
from logic.exchange_calculator import exchange_results

class CalculateMaxProfit:
    """
    Class to calculate the maximum profit from black gem fragments, black gems and concentrated black gems based on the provided stone data.
    """
    
    def __init__(self, data_input: FlatDictStr, 
                       lightstone_costs: FlatDict, 
                       imperfect_lightstone_costs: FlatDict, 
                       black_stone_cost: int, 
                       hours_digit: int, 
                       value_pack_val: float, 
                       market_tax: float,
                       elixir_cost_session: int,
                       elixirs_cost_h: int):
        self.data_input = data_input  # Input data for the session
        self.lightstone_costs = lightstone_costs  # Lightstone costs for the session
        self.imperfect_lightstone_costs = imperfect_lightstone_costs  # Imperfect lightstone costs for the session
        self.black_stone_price = black_stone_cost  # Black stone buy price for the session
        self.hours_digit = hours_digit  # Hours digit for the session
        self.value_pack_val = value_pack_val  # Value pack multiplier for the session
        self.market_tax = market_tax  # Market tax for the session
        self.elixir_cost_session = elixir_cost_session  # Elixir cost for the session
        self.elixirs_cost_h = elixirs_cost_h  # Elixir cost per hour for the session

    def calculate_max_profit(self) -> dict[str, Any]:
        """
        Calculate the maximum profit from items based on the provided input data.
            :return: A dictionary containing the total profit, total profit per hour, taxed profit, taxed profit per hour, new labels for input text and elixir cost.
        """
        result = 0
        gems: FlatDictInt = {}
        heads: FlatDictInt = {}
        contribution_to_total: dict[str, int] = {}
        for name, (price, amount) in self.data_input.items():
            if name == 'Hours':
                continue  # Skip the 'Hours' item as it is not relevant for profit calculation
            elif name in ['Black Gem Frag.', 'Black Gem', 'Conc. Mag. Black Gem', 'S. Black Crystal Shard', 'Wildspark', 'Conc. Mag. Black Stone']:
                gems[name] = (int(price.replace(',', '').replace(' ', '')) if price else 0, int(amount.replace(',', '').replace(' ', '')) if amount else 0)
            elif name in ['Damaged Hide', 'Usable Hide', 'Supreme Hide', 'Breath of Narcion'] or name.startswith('St.'):
                heads[name] = (int(price.replace(',', '').replace(' ', '')) if price else 0, int(amount.replace(',', '').replace(' ', '')) if amount else 0)
            elif 'St.' in name or 'BMB' in name:
                heads[name] = (int(price.replace(',', '').replace(' ', '')) if price else 0, 0)  # Set amount to 0 so previous calculations do not affect the profit calculation
            else:
                result_parcial = (int(price.replace(',', '').replace(' ', '')) if price else 0) * (int(amount.replace(',', '').replace(' ', '')) if amount else 0)  # Calculate the profit for each item
                contribution_to_total[name] = result_parcial  # Store the contribution of each item to the total profit
                result += result_parcial

        result_no_deducted, action_user, black_stone_cost = self.calculate_stones_best_profit(gems, contribution_to_total)  # Calculate the best profit from stones
        result += result_no_deducted  # Add the best profit from stones to the total result

        self.data_input["Conc. Mag. Black Stone"] = ( # Update the input data with the maximum profit value for concentrated black stones
            str(gems["Conc. Mag. Black Stone"][0]), 
            str(int(contribution_to_total["Conc. Mag. Black Stone"] / gems["Conc. Mag. Black Stone"][0])) if contribution_to_total["Conc. Mag. Black Stone"] else "0"
        )

        result_heads, cost_scrolls = self.calculate_heads_best_profit(heads, contribution_to_total)  # Calculate the best profit from stones
        result += result_heads

        new_labels = self.update_labels(result, contribution_to_total)

        total_no_elixirs = result if self.hours_digit > 0 else 0 # Subtract the cost of black stones used for the maximum profit
        total_h = int(total_no_elixirs / self.hours_digit) if self.hours_digit > 0 else 0  # Calculate the total profit per hour
        total_taxed = self.results_taxed(total_no_elixirs) if self.hours_digit > 0 else 0  # Apply market tax to the total profit
        total_taxed_h = int(total_taxed / self.hours_digit) if self.hours_digit > 0 else 0  # Calculate the taxed profit per hour

        black_stone_cost_h = int(black_stone_cost / self.hours_digit) if self.hours_digit > 0 else 0  # Calculate the black stone cost per hour
        scrolls_cost_h = int(cost_scrolls / self.hours_digit) if self.hours_digit > 0 else 0  # Calculate the scrolls cost per hour
        
        total = (total_no_elixirs - self.elixir_cost_session - black_stone_cost - cost_scrolls) if self.hours_digit > 0 else 0  # Subtract the elixir cost from the total profit after calculating profit taxed so it does not affect the taxed profit
        total_taxed = (total_taxed - self.elixir_cost_session - black_stone_cost - cost_scrolls) if self.hours_digit > 0 else 0 # Subtract the elixir cost from the taxed profit
        total_h = (total_h - self.elixirs_cost_h - black_stone_cost_h - scrolls_cost_h) if self.hours_digit > 0 else 0 # Subtract the elixir cost per hour from the total profit per hour
        total_taxed_h = (total_taxed_h - self.elixirs_cost_h - black_stone_cost_h - scrolls_cost_h) if self.hours_digit > 0 else 0 # Subtract the elixir cost per hour from the taxed profit per hour

        return {
            'total': total,
            'total_h': total_h,
            'taxed': total_taxed,
            'taxed_h': total_taxed_h,
            'new_labels_input_text': new_labels,
            'elixirs_cost': str(f"{self.elixir_cost_session:,}"),
            'action_user': action_user
        }

    def calculate_stones_best_profit(self, stones_best_profit: FlatDictInt, contribution_to_total: dict[str, int]) -> tuple[int, str, int]:
        """
        Calculate the best profit from stones based on the provided stone data.
            :param stones_best_profit: A dictionary containing the stone data with their prices and amounts.
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit.
            :return: The total best profit from the stones, action for the user to get that maximum profit and cost of black stones used for the maximum profit.
        """
        if not stones_best_profit:
            return (0, "", 0)  # Return 0 profit and empty action if no stones are provided
        
        self.exchange_wildsparks(stones_best_profit)  # Exchange wildsparks to black gem fragments if auto calculate best profit is enabled
        contribution_to_total['Wildspark'] = stones_best_profit['Wildspark'][0] * stones_best_profit['Wildspark'][1]  # Add the contribution of Wildsparks to the total profit

        profit_fragments, action_fragments, cost_black_stones_fragments, contribution_to_total_fragments = self.calculate_profit_fragments(stones_best_profit.copy())  # Calculate profit for each stone separately
        profit_black_gem, action_black_gem, cost_black_stones_black_gem, contribution_to_total_black_gem = self.calc_profit_black_gem(stones_best_profit.copy())  # Calculate profit for black gems and concentrated black stones (if that is the max profit, otherwise sharps)
        profit_conc_black_gem, action_concentrated, cost_black_stones_concentrated, contribution_to_total_concentrated = self.calc_profit_conc_black_gem(stones_best_profit.copy()) # Calculate profit for concentrated gems and concentrated black stones (if that is the max profit, otherwise sharps)
        
        profit_fragments_cost_applied = profit_fragments - cost_black_stones_fragments  # Add the profit from fragments to the total result and deduct the cost of black stones used for fragments
        profit_black_gem_cost_applied = profit_black_gem - cost_black_stones_black_gem  # Add the
        profit_conc_black_gem_cost_applied = profit_conc_black_gem - cost_black_stones_concentrated  # Add the profit from concentrated black gems to the total result and deduct the cost of black stones used for concentrated gems

        max_profit = max(profit_fragments_cost_applied, profit_black_gem_cost_applied, profit_conc_black_gem_cost_applied)  # Get the maximum profit from all calculations
        if max_profit == profit_fragments_cost_applied:
            max_profit_action_user = "Black Gem Fragments + "
            max_profit_action_user += "Concentrated Black Stone" if action_fragments else "Sharps"  # Add the action based on whether concentrated black stone profit is greater than sharps profit

            contribution_to_total.update(contribution_to_total_fragments)  # Update the contribution to total profit with fragments contribution
            return (profit_fragments, max_profit_action_user, cost_black_stones_fragments)  # Return the maximum profit from fragments calculation
        
        elif max_profit == profit_black_gem_cost_applied:
            max_profit_action_user = "Black Gem + "
            max_profit_action_user += "Concentrated Black Stone" if action_black_gem else "Sharps"

            contribution_to_total.update(contribution_to_total_black_gem)  # Update the contribution to total profit with black gem contribution
            return (profit_black_gem, max_profit_action_user, cost_black_stones_black_gem)  # Return the maximum profit from black gem calculation
        
        else:
            max_profit_action_user = "Concentrated Black Gem + "
            max_profit_action_user += "Concentrated Black Stone" if action_concentrated else "Sharps"

            contribution_to_total.update(contribution_to_total_concentrated)  # Update the contribution to total profit with concentrated black gem contribution
            return (profit_conc_black_gem, max_profit_action_user, cost_black_stones_concentrated)  # Return the maximum profit from sharp calculation

    def calculate_profit_fragments(self, data_gems_stones: FlatDictInt) -> TupleContributions:
        """
        Calculate the profit from each stone and gem separately based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :return: The total profit from black gem fragments, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        return self.get_profit_sharps(data_gems_stones, 0)  # Calculate profit from sharps and return the result adding it to current result

    def calc_profit_black_gem(self, data_gems_stones: FlatDictInt) -> TupleContributions:
        """
        Calculate the profit from black gems and sharps based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :return: The total profit from black gems, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        black_stone_cost = 0
        if n_fragment_exchange > 0 and n_black_stone_exchange > 0:
            amount_black_gem_exchange = data_gems_stones["Black Gem Frag."][1] // n_fragment_exchange  # Number of Black Gem Fragments that can be exchanged
            black_stone_exchange = amount_black_gem_exchange * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            data_gems_stones["Black Gem Frag."] = (
                data_gems_stones["Black Gem Frag."][0], 
                data_gems_stones["Black Gem Frag."][1] % n_fragment_exchange
            )  # Remaining Black Gem Fragments after exchange
            data_gems_stones["Black Gem"] = (
                data_gems_stones["Black Gem"][0], 
                data_gems_stones["Black Gem"][1] + amount_black_gem_exchange
            )  # Update the tuple with the new amount of Black Gems

            black_stone_cost = black_stone_exchange * self.black_stone_price  # Black stone cost to deduct from the profit

        return self.get_profit_sharps(data_gems_stones, black_stone_cost)  # Calculate profit from sharps and return the result adding it to current result

    def calc_profit_conc_black_gem(self, data_gems_stones: FlatDictInt) -> TupleContributions:
        """
        Calculate the profit from concentrated black gems and sharps based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :return: The total profit from concentrated black gems, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        black_stone_cost = 0
        if n_fragment_exchange > 0 and n_black_stone_exchange > 0:
            amount_black_gem_exchange = data_gems_stones["Black Gem Frag."][1] // n_fragment_exchange  # Number of Black Gem Fragments that can be exchanged
            black_stone_exchange = amount_black_gem_exchange * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            data_gems_stones["Black Gem Frag."] = (
                data_gems_stones["Black Gem Frag."][0], 
                data_gems_stones["Black Gem Frag."][1] % n_fragment_exchange
            )  # Remaining Black Gem Fragments after exchange
            data_gems_stones["Black Gem"] = (
                data_gems_stones["Black Gem"][0], 
                data_gems_stones["Black Gem"][1] + amount_black_gem_exchange
            )  # Number of Black Gems obtained from fragments

            black_stone_cost = black_stone_exchange * self.black_stone_price  # Subtract the cost of Black Stones used for exchange

        if n_black_gem_concentrate_gem_exchange > 0 and n_sharp_exchange_concentrate_gem > 0:
            amount_concentrated_black_stone = min(data_gems_stones["Black Gem"][1] // n_black_gem_concentrate_gem_exchange, data_gems_stones["S. Black Crystal Shard"][1] // n_sharp_exchange_concentrate_gem)  # Number of Concentrated Magical Black Stone that can be exchanged

            data_gems_stones["Black Gem"] = (
                data_gems_stones["Black Gem"][0], 
                data_gems_stones["Black Gem"][1] - amount_concentrated_black_stone * n_black_gem_concentrate_gem_exchange
            )  # Remaining Black Gems after exchange
            data_gems_stones["S. Black Crystal Shard"] = (
                data_gems_stones["S. Black Crystal Shard"][0], 
                data_gems_stones["S. Black Crystal Shard"][1] - amount_concentrated_black_stone * n_sharp_exchange_concentrate_gem
            )  # Remaining Special Black Crystal Shards after exchange

            data_gems_stones["Conc. Mag. Black Gem"] = (
                data_gems_stones["Conc. Mag. Black Gem"][0], 
                data_gems_stones["Conc. Mag. Black Gem"][1] + amount_concentrated_black_stone
            ) # Add the number of Concentrated Magical Black Gems obtained from the exchange

        return self.get_profit_sharps(data_gems_stones, black_stone_cost)  # Calculate profit from sharps and return the result adding it to current result

    def get_profit_sharps(self, gem_stones: FlatDictInt, black_stone_cost: int) -> TupleContributions:
        """
        Calculate the profit from Sharps and Concentrated Magical Black Stones based on the provided gem stones data.
            :param gem_stones: A dictionary containing the gem stones data with their prices and amounts.
            :param black_stone_cost: The cost of Black Stones used for the exchange.
            :return: The total profit from Sharps and Concentrated Magical Black Stones, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        gem_stones_concentrated = gem_stones.copy()  # Create a copy of the gem stones data for concentrated black stone calculations

        profit_fragments = gem_stones["Black Gem Frag."][0] * gem_stones["Black Gem Frag."][1]  # Calculate profit from Black Gem Fragments
        profit_black_gem = gem_stones["Black Gem"][0] * gem_stones["Black Gem"][1]  # Calculate profit from Black Gems
        profit_concentrated_gem = gem_stones["Conc. Mag. Black Gem"][0] * gem_stones["Conc. Mag. Black Gem"][1]  # Calculate profit from Concentrated Magical Black Gems
        profit_concentrated_stone, black_stone_cost_concentrated, profit_sharps = self.get_results_concentrated_black_stone(gem_stones_concentrated)  # Calculate profit from Sharps

        contribution_to_total = {
            "Black Gem Frag.": profit_fragments,
            "Black Gem": profit_black_gem,
            "Conc. Mag. Black Gem": profit_concentrated_gem,
            "S. Black Crystal Shard": profit_sharps,
            "Conc. Mag. Black Stone": profit_concentrated_stone
        }

        result = (profit_fragments + profit_black_gem + profit_concentrated_gem)  # Add the profits from fragments, black gems and concentrated gems
        profit_sharps = gem_stones["S. Black Crystal Shard"][0] * gem_stones["S. Black Crystal Shard"][1]  # Calculate profit from Sharps

        if (profit_concentrated_stone - black_stone_cost_concentrated) > profit_sharps:
            black_stone_cost += black_stone_cost_concentrated  # Add the cost of Black Stones used for concentrated black stone exchange
            result += profit_concentrated_stone
            return (result, True, black_stone_cost, contribution_to_total) # True if concentrated black stone profit is greater than sharps profit
        else:
            contribution_to_total["S. Black Crystal Shard"] = profit_sharps  # Update the contribution of Sharps to the total profit
            contribution_to_total["Conc. Mag. Black Stone"] = 0 # Set the contribution of Concentrated Magical Black Stone to 0 if it is not greater than Sharps profit
            result += profit_sharps
            return (result, False, black_stone_cost, contribution_to_total) # False if concentrated black stone profit is not greater than sharps profit
        
    def get_results_concentrated_black_stone(self, data_gems_stones: FlatDictInt) -> tuple[int, int, int]:
        """
        Get the results of concentrated black stone based on the amount of sharps and their price.
            :return: The total profit from concentrated black stones.
        """
        if n_sharp_exchange_concentrate > 0 and n_black_stone_exchange > 0:
            amount_exchange_concentrated = data_gems_stones["S. Black Crystal Shard"][1] // n_sharp_exchange_concentrate
            black_stone_exchange = amount_exchange_concentrated * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            amount_sharps = amount_exchange_concentrated % n_sharp_exchange_concentrate  # Remaining Special Black Crystal Shards after exchange
            
            data_gems_stones["Conc. Mag. Black Stone"] = (data_gems_stones["Conc. Mag. Black Stone"][0], data_gems_stones["Conc. Mag. Black Stone"][1] + amount_exchange_concentrated)  # Update the tuple with the new amount of Concentrated Magical Black Stones
            data_gems_stones["S. Black Crystal Shard"] = (data_gems_stones["S. Black Crystal Shard"][0], amount_sharps)  # Update the tuple with the new amount of Special Black Crystal Shards

            return ((amount_exchange_concentrated * data_gems_stones["Conc. Mag. Black Stone"][0]) + (amount_sharps * data_gems_stones["S. Black Crystal Shard"][0]), (black_stone_exchange * self.black_stone_price), (amount_sharps * data_gems_stones["S. Black Crystal Shard"][0]))
        
        return (0, 0, 0) # Return 0 if no concentrated black stone can be obtained
 
    def exchange_wildsparks(self, stones_best_profit: FlatDictInt):
        """
        Exchange Wildsparks to Black Gem Fragments in the input data.
            :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        """
        wildspark = stones_best_profit['Wildspark'][1] # Get current wildspark value
        black_gem_fragment = stones_best_profit['Black Gem Frag.'][1]  # Get current black gem fragment value

        n_exchanges = wildspark // 10 # 10 Wildsparks can be exchanged for 5 Black Gem Fragment
        wildspark %= 10 # Remaining Wildsparks after exchange
        black_gem_fragment += n_exchanges * 5

        stones_best_profit['Black Gem Frag.'] = (stones_best_profit["Black Gem Frag."][0], black_gem_fragment) # Update Black Gem Fragment amount
        stones_best_profit['Wildspark'] = (stones_best_profit["Wildspark"][0], wildspark) # Update Wildspark amount

    def update_labels(self, result: int, contribution_to_total: dict[str, int]) -> list[str]:
        """
        Update the labels with the calculated results and contributions to total profit.
            :param result: The total profit from the session.
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit.
        """
        new_labels: list[str] = []
        for name, _ in self.data_input.items():
            if name == "Hours":
                new_labels.append("Hours")  # Append "Hours" label as it is not a profit item
                continue

            value = contribution_to_total.get(name, 0)  # Get the contribution of the item to the total profit
            percent = (value / result) * 100 if result > 0 else 0  # Calculate the percentage contribution of each item to the total profit
            if percent > 100:
                percent = 100.0
            new_labels.append(f"{name} ({percent:.2f}%)")  # Format the label with the item name, value and percentage contribution

        return new_labels

    def results_taxed(self, total_no_elixirs: int) -> int:
        """
        Calculate the results after applying market tax and value pack.
            :param total_no_elixirs: The total profit without elixirs cost.
            :return: The total profit after applying market tax and value pack.
        """
        taxed = total_no_elixirs * (1 - self.market_tax)
        taxed += taxed * self.value_pack_val  # Apply value pack multiplier
        return int(taxed)
    
    def calculate_heads_best_profit(self, heads: FlatDictInt, contribution_to_total: dict[str, int]) -> tuple[int, int]:
        """
        Calculate the best profit from heads based on the provided heads data.
            :param heads: A dictionary containing the heads data with their prices and amounts.
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit.
            :return: The total profit from heads.
        """
        name_yellow = ""
        name_special_yellow = ""
        name_green = ""

        for item in heads:
            if item.startswith('St.'):
                name_green = item
            elif item.startswith('M. St.'):
                name_yellow = item
            elif item.startswith('M. Sp. St.'):
                name_special_yellow = item

        green_copy = heads.copy()  # Create a copy of the heads data for green head calculations
        contribution_to_total_green = contribution_to_total.copy()  # Create a copy of the contribution to total profit for green heads
        profit_green = self.get_profit_greens(green_copy, name_green, contribution_to_total_green)  # Calculate the profit from green heads

        yellows_copy = heads.copy()  # Create a copy of the heads data for further calculations
        contribution_to_total_yellow = contribution_to_total.copy()  # Create a copy of the contribution to total profit for yellow heads
        profit_yellow = self.get_profit_normal_yellow_head(yellows_copy, name_yellow, name_green, contribution_to_total_yellow)

        yellow_special_copy = yellows_copy.copy()  # Create a copy of the heads data for special yellow head calculations
        contribution_to_total_special_yellow = contribution_to_total.copy()  # Create a copy of the contribution to total profit for special yellow heads
        profit_special_yellow = self.get_profit_special_yellow_head(yellow_special_copy,name_green, name_yellow, name_special_yellow, contribution_to_total_special_yellow)

        scrolls_copy = heads.copy()  # Create a copy of the heads data for scrolls calculations
        contribution_to_total_scrolls = contribution_to_total.copy()  # Create a copy of the contribution to total profit for scrolls
        profit_scrolls, cost_scrolls = self.get_profit_scrolls(scrolls_copy, contribution_to_total_scrolls, name_green, name_yellow, name_special_yellow)  # Calculate the profit from scrolls

        max_profit = max(profit_green, profit_yellow, profit_special_yellow, profit_scrolls)  # Get the maximum profit from green, yellow and special yellow heads
        cost = 0

        heads_result: FlatDictStr = {}
        if max_profit == profit_green:
            heads_result = {name: (str(price), str(amount)) for name, (price, amount) in green_copy.items()}
            contribution_to_total.update(contribution_to_total_green)  # Update the contribution to total profit with green heads contribution
        elif max_profit == profit_yellow:
            heads_result = {name: (str(price), str(amount)) for name, (price, amount) in yellows_copy.items()}
            contribution_to_total.update(contribution_to_total_yellow)  # Update the contribution to total profit with yellow heads contribution
        elif max_profit == profit_special_yellow:
            heads_result = {name: (str(price), str(amount)) for name, (price, amount) in yellow_special_copy.items()}
            contribution_to_total.update(contribution_to_total_special_yellow)  # Update the contribution to total profit with special yellow heads contribution
        else:
            cost = cost_scrolls
            heads_result = {name: (str(price), str(amount)) for name, (price, amount) in scrolls_copy.items()}
            contribution_to_total.update(contribution_to_total_scrolls)

        self.data_input.update(heads_result)  # Update the contribution to total profit with green heads contribution
        return (max_profit, cost)
    
    def get_profit_greens(self, heads: FlatDictInt, name_green: str, contribution_to_total: dict[str, int]) -> int:
        """
        Calculate the profit from green heads based on the provided heads data.
            :param heads: A dictionary containing the heads data with their prices and amounts.
            :param name_green: The name of the green head to calculate profit for.
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit
            :return: The total profit from green heads.
        """
        n_green = heads[name_green][1]  # Get the number of green heads available for exchange
        price_green = heads[name_green][0]  # Get the price of green heads
        profit_green = n_green * price_green  # Calculate the profit from green heads
        profit_breath = heads['Breath of Narcion'][0] * heads['Breath of Narcion'][1]  # Calculate the profit from Breath of Narcion
        
        contribution_to_total[name_green] = profit_green # Update the contribution to total profit with green heads contribution
        contribution_to_total['Breath of Narcion'] = profit_breath  # Update the contribution to total profit with Breath of Narcion contribution
        
        return profit_green + profit_breath
    
    def get_profit_normal_yellow_head(self, heads: FlatDictInt, name_yellow: str, name_green: str, contribution_to_total: dict[str, int]) -> int:
        """
        Calculate the profit from normal yellow heads based on the provided heads data.
            :param heads: A dictionary containing the heads data with their prices and amounts.
            :param name_yellow: The name of the yellow head to calculate profit for.
            :param name_green: The name of the green head to calculate profit for.
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit
            :return: The total profit from normal yellow heads.
        """
        n_supreme = heads['Supreme Hide'][1] # Number of Supreme Hides that can be exchanged
        n_usable = heads['Usable Hide'][1] + int(n_supreme * n_supreme_exchange)  # Number of Usable Hides that can be exchanged
        n_damaged = heads['Damaged Hide'][1]  # Number of Damaged Hides that can be exchanged
        n_normal_yellow = heads[name_green][1]  # Number of Normal Yellow Heads available for exchange

        (_, n_damaged, n_usable) = exchange_results(n_damaged, n_usable)

        n_exchanges_yellow = min(n_damaged // n_damaged_hide_exchange, n_usable // n_usable_hide_exchange, n_normal_yellow)  # Number of Normal Yellow Heads that can be exchanged from Damaged Hides

        heads[name_green] = (heads[name_green][0], heads[name_green][1] - n_exchanges_yellow)  # Update the number of green heads in the heads dictionary
        heads[name_yellow] = (heads[name_yellow][0], n_exchanges_yellow)  # Update the number of yellow heads in the heads dictionary

        profit_greens = self.get_profit_greens(heads, name_green, contribution_to_total)  # Calculate the profit from remaining green heads
        profit_yellow = heads[name_yellow][0] * heads[name_yellow][1]  # Calculate the profit from exchanged yellow heads

        contribution_to_total[name_yellow] = profit_yellow  # Update the contribution to total profit with yellow heads contribution

        return profit_greens + profit_yellow # Return the total profit from green and yellow heads combined

    def get_profit_special_yellow_head(self, heads: FlatDictInt, name_green: str, name_yellow: str, name_special_yellow: str, contribution_to_total: dict[str, int]) -> int:
        """
        Calculate the profit from special yellow heads based on the provided heads data.
            :param heads: A dictionary containing the heads data with their prices and amounts.
            :param name_green: The name of the green head to calculate profit for.
            :param name_yellow: The name of the yellow head to calculate profit for.
            :param name_special_yellow: The name of the special yellow head to calculate profit for
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit
            :return: The total profit from special yellow heads.
        """
        n_breath = heads['Breath of Narcion'][1]  # Get the number of Breath of Narcion available for exchange
        n_special_yellow = min(heads[name_yellow][1], n_breath // n_breath_of_narcion_exchange)  # Number of Special Yellow Heads that can be exchanged from Breath of Narcion

        heads["Breath of Narcion"] = (heads["Breath of Narcion"][0], (heads["Breath of Narcion"][1] - n_special_yellow * n_breath_of_narcion_exchange))  # Update the number of Breath of Narcion in the heads dictionary
        heads[name_yellow] = (heads[name_yellow][0], heads[name_yellow][1] - n_special_yellow)  # Update the number of yellow heads in the heads dictionary
        heads[name_special_yellow] = (heads[name_special_yellow][0], n_special_yellow)  # Update the number of special yellow heads in the heads dictionary

        profit_greens = self.get_profit_greens(heads, name_green, contribution_to_total)  # Calculate the profit from remaining green heads
        profit_yellow = heads[name_yellow][0] * heads[name_yellow][1]  # Calculate the profit from remaining yellow heads
        profit_special_yellow = heads[name_special_yellow][0] * heads[name_special_yellow][1]  # Calculate the profit from exchanged special yellow heads

        contribution_to_total[name_yellow] = profit_yellow
        contribution_to_total[name_special_yellow] = profit_special_yellow  # Update the contribution to total profit with special yellow heads contribution

        return profit_yellow + profit_special_yellow + profit_greens # Return the total profit from yellow and special yellow heads combined
    
    def get_profit_scrolls(self, heads: FlatDictInt, contribution_to_total: dict[str, int], name_green: str, name_yellow: str, name_special_yellow: str) -> tuple[int, int]:
        """
        Calculate the profit from scrolls based on the provided heads data.
            :param heads: A dictionary containing the heads data with their prices and amounts.
            :param contribution_to_total: A dictionary containing the contribution of each item to the total profit.
            :param name_green: The name of the green head to calculate profit for.
            :param name_yellow: The name of the yellow head to calculate profit for.
            :param name_special_yellow: The name of the special yellow head to calculate profit for
            :return: The total profit from scrolls and the cost of scrolls crafted.
        """
        n_breath_of_narcion = heads["Breath of Narcion"][1]  # Number of Breath of Narcion available for exchange
        if n_breath_of_narcion == 0:
            return 0, 0

        most_profitable_scroll = self.get_most_profitable_scroll(heads)
        n_scrolls = heads['Supreme Hide'][1] // n_supreme_hide_scroll
        max_profit_scroll = most_profitable_scroll[1][0] # Maximum profit from the most profitable scroll

        # Calculate how many scrolls can be crafted
        n_imperfect_lightstones_scroll = math.ceil(n_magical_lightstones_scroll / n_magical_lightstone_exchange)
        lowest_cost_imperfects = min(v[1] for v in self.imperfect_lightstone_costs.values())

        cost_magical_lightstones_scroll = n_imperfect_lightstones_scroll * lowest_cost_imperfects  # Cost of magical lightstones per scroll
        cost_lightstone_scroll = most_profitable_scroll[1][1] // n_scrolls_lighstone # Cost of lightstone per scroll
        breath_of_narcion_cost = int(heads['Breath of Narcion'][0])  # Breath of Narcion cost

        n_max_scrolls = n_breath_of_narcion * n_remnants_of_mystic_beasts_exchange
        if n_max_scrolls < n_scrolls:
            n_scrolls = n_max_scrolls

        cost_remnants_scroll = math.ceil(breath_of_narcion_cost / n_remnants_of_mystic_beasts_exchange) # Cost of remnants of mystic beasts per scroll
        cost_scrolls = (cost_lightstone_scroll + cost_magical_lightstones_scroll + cost_remnants_scroll) * n_scrolls  # Total cost of scrolls crafted

        # Total profit from scrolls crafted
        profit_scrolls = max_profit_scroll * n_scrolls

        heads[most_profitable_scroll[0]] = (most_profitable_scroll[1][0], n_scrolls)  # Update the number of scrolls crafted
        heads['Supreme Hide'] = (heads['Supreme Hide'][0], heads['Supreme Hide'][1] - (n_scrolls * n_supreme_hide_scroll))  # Update the number of supreme hides left
        n_breath_of_narcion_reduced = math.ceil(n_scrolls / n_remnants_of_mystic_beasts_exchange) if heads["Breath of Narcion"][0] else 0

        heads['Breath of Narcion'] = (heads['Breath of Narcion'][0], heads['Breath of Narcion'][1] - n_breath_of_narcion_reduced)

        # Use remnants of mystic beasts if available in heads
        green_copy_scrolls = heads.copy()  # Create a copy of the heads data for green head calculations
        contribution_to_total_green_scrolls = contribution_to_total.copy()  # Create a copy of the contribution to total profit for green heads
        profit_green = self.get_profit_greens(green_copy_scrolls, name_green, contribution_to_total_green_scrolls)  # Calculate the profit from green heads

        yellow_scrolls_copy = heads.copy()
        contribution_to_total_yellow_scrolls = contribution_to_total.copy()  # Create a copy of the contribution to total profit for yellow scrolls
        profit_yellow = self.get_profit_normal_yellow_head(yellow_scrolls_copy, name_yellow, name_green, contribution_to_total_yellow_scrolls)  # Calculate the profit from yellow heads

        yellow_special_scrolls_copy = yellow_scrolls_copy.copy()  # Create a copy of the heads data for special yellow head calculations
        contribution_to_total_special_yellow_scrolls = contribution_to_total.copy()  # Create a copy of the contribution to total profit for special yellow heads
        profit_special_yellow = self.get_profit_special_yellow_head(yellow_special_scrolls_copy, name_green, name_yellow, name_special_yellow, contribution_to_total_special_yellow_scrolls)
    
        max_profit = max(profit_green, profit_yellow, profit_special_yellow)  # Get the maximum profit from green, yellow special yellow heads
        heads_result: FlatDictInt = {}
        if max_profit == profit_green:
            heads_result = {name: (price, amount) for name, (price, amount) in green_copy_scrolls.items()}
            contribution_to_total.update(contribution_to_total_green_scrolls)  # Update the contribution to total profit with green heads contribution
        elif max_profit == profit_yellow:
            heads_result = {name: (price, amount) for name, (price, amount) in yellow_scrolls_copy.items()}
            contribution_to_total.update(contribution_to_total_yellow_scrolls)  # Update the contribution to total profit with yellow heads contribution
        else:
            heads_result = {name: (price, amount) for name, (price, amount) in yellow_special_scrolls_copy.items()}
            contribution_to_total.update(contribution_to_total_special_yellow_scrolls)  # Update the contribution to total profit with special yellow heads contribution

        contribution_to_total[most_profitable_scroll[0]] = profit_scrolls  # Update the contribution to total profit with scrolls contribution

        heads.update(heads_result) # Update the heads with the results of the calculations
        return ((max_profit + profit_scrolls), cost_scrolls)  # Return the total profit from scrolls and heads combined
    
    def get_most_profitable_scroll(self, heads: FlatDictInt):
        """
        Get the most profitable scroll based on the heads data.
            :param heads: A dictionary containing the heads data with their prices and amounts.
            :return: The most profitable scroll and its cost.
        """
        scrolls = {
            'BMB: All AP': (heads['BMB: All AP'][0], self.lightstone_costs["758001"][1]), # Lighstone of fire: Rage
            'BMB: Accuracy': (heads['BMB: Accuracy'][0], self.lightstone_costs["758002"][1]), # Lighstone of earth: Marked
            'BMB: Evasion': (heads['BMB: Evasion'][0], self.lightstone_costs["760002"][1]), # Lighstone of earth: Waves
            'BMB: Damage Reduction': (heads['BMB: Damage Reduction'][0], self.lightstone_costs["760001"][1]), # Lighstone of earth: Iron Wall
            'BMB: Max HP': (heads['BMB: Max HP'][0], self.lightstone_costs["762001"][1]) # Lighstone of Wind: Heart
        }
        
        max_scroll = max(scrolls.items(), key=lambda x: x[1][0] - x[1][1])
        return max_scroll