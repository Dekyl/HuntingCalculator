from config.config import (
    n_fragment_exchange, 
    n_black_stone_exchange, 
    n_sharp_exchange_concentrate, 
    n_black_gem_concentrate_gem_exchange, 
    n_sharp_exchange_concentrate_gem,
    TupleProfits
)

class CalculateMaxProfit:
    """
    Class to calculate the maximum profit from black gem fragments, black gems and concentrated black gems based on the provided stone data.
    """
    
    def __init__(self, black_stone_cost: int, concentrated_black_stone_cost: int):
        self.black_stone_cost = black_stone_cost
        self.concentrated_black_stone_cost = concentrated_black_stone_cost

    def calculate_profit_fragments(self, data_gems_stones: dict[str, int]) -> TupleProfits:
        """
        Calculate the profit from each stone and gem separately based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :return: The total profit from black gem fragments, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        result = 0
        return self.get_profit_sharps(data_gems_stones, result)  # Calculate profit from sharps and return the result adding it to current result

    def calc_profit_black_gem(self, data_gems_stones: dict[str, int]) -> TupleProfits:
        """
        Calculate the profit from black gems and sharps based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :return: The total profit from black gems, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        result = 0  # Initialize result variable
        if n_fragment_exchange > 0 and n_black_stone_exchange > 0:
            amount_black_gem_exchange = data_gems_stones["amount_fragments"] // n_fragment_exchange  # Number of Black Gem Fragments that can be exchanged
            black_stone_exchange = amount_black_gem_exchange * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            data_gems_stones["amount_fragments"] %= n_fragment_exchange  # Remaining Black Gem Fragments after exchange
            data_gems_stones["amount_black_gem"] += amount_black_gem_exchange  # Number of Black Gems obtained from fragments # Add the amount of Black Gems already present

            result -= black_stone_exchange * self.black_stone_cost  # Subtract the cost of Black Stones used for exchange

        return self.get_profit_sharps(data_gems_stones, result)  # Calculate profit from sharps and return the result adding it to current result

    def calc_profit_conc_black_gem(self, data_gems_stones: dict[str, int]) -> TupleProfits:
        """
        Calculate the profit from concentrated black gems and sharps based on the provided stone data.
            :param data_gems_stones: A dictionary containing the stones and gems data with their prices and amounts.
            :return: The total profit from concentrated black gems, whether concentrated black stone profit is greater than sharps profit and specific amount of profits for each stone.
        """
        result = 0  # Initialize result variable

        if n_fragment_exchange > 0 and n_black_stone_exchange > 0:
            amount_black_gem_exchange = data_gems_stones["amount_fragments"] // n_fragment_exchange  # Number of Black Gem Fragments that can be exchanged
            black_stone_exchange = amount_black_gem_exchange * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            data_gems_stones["amount_fragments"] %= n_fragment_exchange  # Remaining Black Gem Fragments after exchange
            data_gems_stones["amount_black_gem"] += amount_black_gem_exchange  # Number of Black Gems obtained from fragments

            result -= black_stone_exchange * self.black_stone_cost  # Subtract the cost of Black Stones used for exchange

        if n_black_gem_concentrate_gem_exchange > 0 and n_sharp_exchange_concentrate_gem > 0:
            amount_concentrated_black_stone = min(data_gems_stones["amount_black_gem"] // n_black_gem_concentrate_gem_exchange, data_gems_stones["amount_sharps"] // n_sharp_exchange_concentrate_gem)  # Number of Concentrated Magical Black Stone that can be exchanged

            data_gems_stones["amount_black_gem"] -= amount_concentrated_black_stone * n_black_gem_concentrate_gem_exchange  # Remaining Black Gems after exchange
            data_gems_stones["amount_sharps"] -= amount_concentrated_black_stone * n_sharp_exchange_concentrate_gem  # Remaining Special Black Crystal Shards after exchange

            data_gems_stones["amount_concentrated_gem"] += amount_concentrated_black_stone  # Add the number of Concentrated Magical Black Gems obtained from the exchange

        return self.get_profit_sharps(data_gems_stones, result)  # Calculate profit from sharps and return the result adding it to current result

    def get_profit_sharps(self, data_gems_stones: dict[str, int], result: int) -> TupleProfits:
        profit_fragments = data_gems_stones["amount_fragments"] * data_gems_stones["price_fragments"]
        profit_black_gem = data_gems_stones["amount_black_gem"] * data_gems_stones["price_black_gem"]
        profit_concentrated_gem = data_gems_stones["amount_concentrated_gem"] * data_gems_stones["price_concentrated_gem"]

        result += (profit_fragments + profit_black_gem + profit_concentrated_gem)  # Add the profits from fragments, black gems and concentrated gems
        results_profit = {
            "Black Gem Fragments": profit_fragments,
            "Black Gem": profit_black_gem,
            "Concentrated Black Gem": profit_concentrated_gem
        }

        concentrate_black_stone_profit = self.get_results_concentrated_black_stone(data_gems_stones["amount_sharps"], data_gems_stones["price_sharps"])
        profit_sharps = data_gems_stones["amount_sharps"] * data_gems_stones["price_sharps"]

        if concentrate_black_stone_profit > profit_sharps:
            result += concentrate_black_stone_profit
            results_profit["Sharps"] = concentrate_black_stone_profit  # Add concentrated black stone profit if it is greater than sharps profit
            return (result, True, results_profit) # True if concentrated black stone profit is greater than sharps profit
        else:
            result += profit_sharps
            results_profit["Sharps"] = profit_sharps
            return (result, False, results_profit) # False if concentrated black stone profit is not greater than sharps profit
        
    def get_results_concentrated_black_stone(self, amount_sharps: int, price_sharps: int) -> int:
        """
        Get the results of concentrated black stone based on the amount of sharps and their price.
            :return: The total profit from concentrated black stones.
        """
        if n_sharp_exchange_concentrate > 0 and n_black_stone_exchange > 0:
            amount_exchange_concentrated = amount_sharps // n_sharp_exchange_concentrate
            black_stone_exchange = amount_exchange_concentrated * n_black_stone_exchange  # Number of Black Stones needed for the exchange

            amount_sharps %= n_sharp_exchange_concentrate  # Remaining Special Black Crystal Shards after exchange

            return (amount_exchange_concentrated * self.concentrated_black_stone_cost) + (amount_sharps * price_sharps) - (black_stone_exchange * self.black_stone_cost)
        
        return 0