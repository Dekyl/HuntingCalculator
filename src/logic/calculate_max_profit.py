from config.config import (
    n_fragment_exchange, 
    n_black_stone_exchange, 
    n_sharp_exchange_concentrate, 
    n_black_gem_concentrate_gem_exchange, 
    n_sharp_exchange_concentrate_gem,
    TupleProfits,
    FlatDictInt
)
from typing import Optional

class CalculateMaxProfit:
    """
    Class to calculate the maximum profit from black gem fragments, black gems and concentrated black gems based on the provided stone data.
    """
    
    def __init__(self, black_stone_price: int, concentrated_black_stone_price: int):
        self.black_stone_price = black_stone_price
        self.concentrated_black_stone_price = concentrated_black_stone_price

    def calculate_stones_best_profit(self, stones_best_profit: FlatDictInt) -> tuple[int, str, Optional[dict[str, int]]]:
        """
        Calculate the best profit from stones based on the provided stone data.
            :param stones_best_profit: A dictionary containing the stone data with their prices and amounts.
            :return: The total best profit from the stones and action for the user to get that maximum profit.
        """
        if not stones_best_profit:
            return (0, "", None)
        
        price_fragments, amount_fragments = stones_best_profit.get('Black Gem Frag.', (0, 0))  # Get the amount of Black Gem Fragments
        price_black_gem, amount_black_gem = stones_best_profit.get('Black Gem', (0, 0))  # Get the amount of Black Gems
        price_concentrated_gem, amount_concentrated_gem = stones_best_profit.get('Conc. Mag. Black Gem', (0, 0))  # Get the amount of Concentrated Magical Black Gems
        price_sharps, amount_sharps = stones_best_profit.get('S. Black Crystal Shard', (0, 0))  # Get the amount of Special Black Crystal Shards

        original_gems_stones = {
            "price_fragments": price_fragments,
            "amount_fragments": amount_fragments,
            "price_black_gem": price_black_gem,
            "amount_black_gem": amount_black_gem,
            "price_concentrated_gem": price_concentrated_gem,
            "amount_concentrated_gem": amount_concentrated_gem,
            "price_sharps": price_sharps,
            "amount_sharps": amount_sharps
        }

        results_profits: dict[str, TupleProfits] = {}
        
        results_profits["Black Gem Fragments"] = (profit_fragments, _, _) = self.calculate_profit_fragments(original_gems_stones.copy(), original_gems_stones)  # Calculate profit for each stone separately
        results_profits["Black Gem"] = (profit_black_gem, _, _) = self.calc_profit_black_gem(original_gems_stones.copy(), original_gems_stones)  # Calculate profit for black gems and concentrated black stones (if that is the max profit, otherwise sharps)
        results_profits["Concentrated Black Gem"] = (profit_conc_black_gem, _, _) = self.calc_profit_conc_black_gem(original_gems_stones.copy(), original_gems_stones) # Calculate profit for concentrated gems and concentrated black stones (if that is the max profit, otherwise sharps)

        name_max_profit = max(results_profits, key=lambda k: results_profits[k][0])  # Get the key with the maximum profit
        max_profit_action_user = f"{name_max_profit} + "
        max_profit_action_user += "Concentrated Black Stone" if results_profits[name_max_profit][1] else "Sharps"  # Add the action based on whether concentrated black stone profit is greater than sharps profit
        profit_details_percent_labels = results_profits[name_max_profit][2]  # Get the profit details for the maximum profit
        
        return (max(profit_fragments, profit_black_gem, profit_conc_black_gem), max_profit_action_user, profit_details_percent_labels)  # Return the maximum profit from all calculations

    def calculate_profit_fragments(self, data_gems_stones: dict[str, int], original_gem_stones: dict[str, int]) -> TupleProfits:
        """
        Calculate the profit from each stone and gem separately based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :param original_gem_stones: A dictionary containing the original stones and gems data with their prices and amounts.
            :return: The total profit from black gem fragments, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        return self.get_profit_sharps(data_gems_stones, 0, original_gem_stones)  # Calculate profit from sharps and return the result adding it to current result

    def calc_profit_black_gem(self, data_gems_stones: dict[str, int], original_gem_stones: dict[str, int]) -> TupleProfits:
        """
        Calculate the profit from black gems and sharps based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :param original_gem_stones: A dictionary containing the original stones and gems data with their prices and amounts.
            :return: The total profit from black gems, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        black_stone_cost = 0
        if n_fragment_exchange > 0 and n_black_stone_exchange > 0:
            amount_black_gem_exchange = data_gems_stones["amount_fragments"] // n_fragment_exchange  # Number of Black Gem Fragments that can be exchanged
            black_stone_exchange = amount_black_gem_exchange * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            data_gems_stones["amount_fragments"] %= n_fragment_exchange  # Remaining Black Gem Fragments after exchange
            data_gems_stones["amount_black_gem"] += amount_black_gem_exchange  # Number of Black Gems obtained from fragments # Add the amount of Black Gems already present

            black_stone_cost = black_stone_exchange * self.black_stone_price  # Black stone cost to deduct from the profit

        return self.get_profit_sharps(data_gems_stones, black_stone_cost, original_gem_stones)  # Calculate profit from sharps and return the result adding it to current result

    def calc_profit_conc_black_gem(self, data_gems_stones: dict[str, int], original_gem_stones: dict[str, int]) -> TupleProfits:
        """
        Calculate the profit from concentrated black gems and sharps based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :param original_gem_stones: A dictionary containing the original stones and gems data with their prices and amounts.
            :return: The total profit from concentrated black gems, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        black_stone_cost = 0
        if n_fragment_exchange > 0 and n_black_stone_exchange > 0:
            amount_black_gem_exchange = data_gems_stones["amount_fragments"] // n_fragment_exchange  # Number of Black Gem Fragments that can be exchanged
            black_stone_exchange = amount_black_gem_exchange * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            data_gems_stones["amount_fragments"] %= n_fragment_exchange  # Remaining Black Gem Fragments after exchange
            data_gems_stones["amount_black_gem"] += amount_black_gem_exchange  # Number of Black Gems obtained from fragments

            black_stone_cost = black_stone_exchange * self.black_stone_price  # Subtract the cost of Black Stones used for exchange

        if n_black_gem_concentrate_gem_exchange > 0 and n_sharp_exchange_concentrate_gem > 0:
            amount_concentrated_black_stone = min(data_gems_stones["amount_black_gem"] // n_black_gem_concentrate_gem_exchange, data_gems_stones["amount_sharps"] // n_sharp_exchange_concentrate_gem)  # Number of Concentrated Magical Black Stone that can be exchanged

            data_gems_stones["amount_black_gem"] -= amount_concentrated_black_stone * n_black_gem_concentrate_gem_exchange  # Remaining Black Gems after exchange
            data_gems_stones["amount_sharps"] -= amount_concentrated_black_stone * n_sharp_exchange_concentrate_gem  # Remaining Special Black Crystal Shards after exchange

            data_gems_stones["amount_concentrated_gem"] += amount_concentrated_black_stone  # Add the number of Concentrated Magical Black Gems obtained from the exchange

        return self.get_profit_sharps(data_gems_stones, black_stone_cost, original_gem_stones)  # Calculate profit from sharps and return the result adding it to current result

    def get_profit_sharps(self, data_gems_stones: dict[str, int], black_stone_cost: int, original_gem_stones: dict[str, int]) -> TupleProfits:
        profit_fragments, profit_black_gem, profit_concentrated_gem, profit_concentrated_black_stone = self.get_profit_details_deduct_black_stone(black_stone_cost,
                                                                                                                                                  data_gems_stones,
                                                                                                                                                  original_gem_stones)  # Deduct the cost of Black Stones from the profits

        result = (profit_fragments + profit_black_gem + profit_concentrated_gem)  # Add the profits from fragments, black gems and concentrated gems and deduct the cost of Black Stones
        profit_details_percent_labels = {
            "Black Gem Fragments": profit_fragments,
            "Black Gem": profit_black_gem,
            "Concentrated Black Gem": profit_concentrated_gem
        }
        
        profit_sharps = data_gems_stones["amount_sharps"] * data_gems_stones["price_sharps"]

        if profit_concentrated_black_stone > profit_sharps:
            result += profit_concentrated_black_stone
            profit_details_percent_labels["Sharps"] = profit_concentrated_black_stone  # Add concentrated black stone profit if it is greater than sharps profit
            return (result, True, profit_details_percent_labels) # True if concentrated black stone profit is greater than sharps profit
        else:
            result += profit_sharps
            profit_details_percent_labels["Sharps"] = profit_sharps # Add sharps profit if concentrated black stone profit is not greater than sharps profit
            return (result, False, profit_details_percent_labels) # False if concentrated black stone profit is not greater than sharps profit
        
    def get_results_concentrated_black_stone(self, amount_sharps: int, price_sharps: int) -> int:
        """
        Get the results of concentrated black stone based on the amount of sharps and their price.
            :return: The total profit from concentrated black stones.
        """
        if n_sharp_exchange_concentrate > 0 and n_black_stone_exchange > 0:
            amount_exchange_concentrated = amount_sharps // n_sharp_exchange_concentrate
            black_stone_exchange = amount_exchange_concentrated * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            amount_sharps %= n_sharp_exchange_concentrate  # Remaining Special Black Crystal Shards after exchange

            return (amount_exchange_concentrated * self.concentrated_black_stone_price) + (amount_sharps * price_sharps) - (black_stone_exchange * self.black_stone_price)
        
        return 0
    
    def get_profit_details_deduct_black_stone(self, black_stone_cost: int, modified_gem_stones: dict[str, int], original_gem_stones: dict[str, int]) -> tuple[int, int, int, int]:
        """
        Deduct the cost of Black Stones from the profits and return the updated profits.
            :return: The updated profits after deducting the cost of Black Stones.
        """
        profit_fragments = modified_gem_stones["amount_fragments"] * modified_gem_stones["price_fragments"]
        profit_black_gem = modified_gem_stones["amount_black_gem"] * modified_gem_stones["price_black_gem"]
        profit_concentrated_gem = modified_gem_stones["amount_concentrated_gem"] * modified_gem_stones["price_concentrated_gem"]
        profit_sharps = self.get_results_concentrated_black_stone(modified_gem_stones["amount_sharps"], modified_gem_stones["price_sharps"])

        profit_no_deducted = 0
        final_profit_fragments = 0 
        final_profit_black_gem = 0 
        final_profit_concentrated_gem = 0 
        final_profit_sharps = 0
        aport_deducted_profit: list[str] = []  # List to store the names of the profits that were deducted

        for name, value in modified_gem_stones.items():
            if name == "amount_fragments":
                if value != original_gem_stones["amount_fragments"]:
                    profit_no_deducted += profit_fragments
                    aport_deducted_profit.append("Fragments")
                else:
                    final_profit_fragments = profit_fragments
            elif name == "amount_black_gem":
                if value != original_gem_stones["amount_black_gem"]:
                    profit_no_deducted += profit_black_gem
                    aport_deducted_profit.append("Black Gem")
                else:
                    final_profit_black_gem = profit_black_gem
            elif name == "amount_concentrated_gem":
                if value != original_gem_stones["amount_concentrated_gem"]:
                    profit_no_deducted += profit_concentrated_gem
                    aport_deducted_profit.append("Concentrated Gem")
                else:
                    final_profit_concentrated_gem = profit_concentrated_gem
            elif name == "amount_sharps":
                if value != original_gem_stones["amount_sharps"]:
                    profit_no_deducted += profit_sharps
                    aport_deducted_profit.append("Sharps")
                else:
                    final_profit_sharps = profit_sharps

        profit_deducted = profit_no_deducted - black_stone_cost  # Profit deducted is the profit of those stones who aported to the payment of black stones cost

        if "Fragments" in aport_deducted_profit:
            percent_fragments = (profit_fragments / profit_no_deducted) if profit_no_deducted > 0 else 0
            final_profit_fragments = int(profit_deducted * (percent_fragments))
        if "Black Gem" in aport_deducted_profit:
            percent_black_gem = (profit_black_gem / profit_no_deducted) if profit_no_deducted > 0 else 0
            final_profit_black_gem = int(profit_deducted * (percent_black_gem))
        if "Concentrated Gem" in aport_deducted_profit:
            percent_concentrated_gem = (profit_concentrated_gem / profit_no_deducted) if profit_no_deducted > 0 else 0
            final_profit_concentrated_gem = int(profit_deducted * (percent_concentrated_gem))
        if "Sharps" in aport_deducted_profit:
            percent_sharps = (profit_sharps / profit_no_deducted) if profit_no_deducted > 0 else 0
            final_profit_sharps = int(profit_deducted * (percent_sharps))
        
        return (final_profit_fragments, final_profit_black_gem, final_profit_concentrated_gem, final_profit_sharps)