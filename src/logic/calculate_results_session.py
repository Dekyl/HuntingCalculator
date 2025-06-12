from typing import Any

from logic.logs import add_log

value_pack_multiplier = 0.315 # Value pack multiplier for the results calculation
extra_profit_multiplier = 0.05 # Extra profit multiplier for the results calculation

def calculate_elixirs_cost_hour(elixirs: dict[str, tuple[str, int]]) -> str:
    """
    Calculate the cost of elixirs per hour based on the provided elixirs data.
        :param elixirs: A dictionary containing elixir id: (name and cost).
        :return: The total cost of elixirs per hour.
    """
    cost_elixirs = 0
    for _, (name, cost) in elixirs.items():
        if name.startswith("Perfume"):
            cost *= 3 # Perfumes cost 3 times more (3 perfumes per hour)
        else:
            cost *= 4 # Other elixirs cost 4 times more (4 elixirs per hour)
        cost_elixirs += cost

    return str(f"{cost_elixirs:,}")

def calculate_results_session(value_pack: bool, market_tax: float, extra_profit: bool, data_input: dict[str, tuple[str, str]], elixirs_cost: str) -> dict[str, Any]:
    """
    Calculate the results of a hunting session based on the provided input data.
        :param value_pack: A boolean indicating whether the value pack is active.
        :param market_tax: The market tax percentage to apply.
        :param extra_profit: The extra profit to apply or not to results
        :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        :param elixirs_cost: The cost of elixirs for the session.
        :return: A dictionary containing the calculated results of the session, including total results, total per hour, taxed results, taxed per hour, 
            and updated labels for input text. or an empty dictionary if there is an error in the input data.
    """
    hours = data_input.get('Hours', ("", "0"))[1] or "0" # If 'Hours' is not in data_input or if it is empty, default to "0"
    elixirs_cost = elixirs_cost.replace(',', '').replace(' ', '')  # Remove commas and spaces for validation

    if not elixirs_cost.isdigit():
        add_log(f"Invalid elixirs cost: {elixirs_cost}. Expected a number.", "error")
        return {}
    
    if not hours.isdigit():
        add_log(f"Invalid hours: {hours}. Expected a number.", "error")
        return {}
    
    hours = int(hours)
    elixirs_cost_h = int(elixirs_cost) if hours > 0 else 0  # Elixirs cost per hour, if hours is 0, set to 0

    extra_breath_of_narcion = get_extra_breath_of_narcions(data_input) # Get the total number of extra Breath of Narcions
    total = results_total(data_input, extra_breath_of_narcion) if hours > 0 else 0  # Calculate total results only if hours is greater than 0
    if total is None:
        add_log("Invalid input data for results_total calculation.", "error")
        return {}
    
    value_pack_val = value_pack_multiplier if value_pack else 0  # Set value pack multiplier if value pack is active, otherwise set to 0
    value_pack_val += extra_profit_multiplier if extra_profit else 0  # Add extra profit multiplier if extra profit is active, otherwise add 0

    total_h = results_h(total, hours) if hours > 0 else 0  # Calculate total results per hour only if hours is greater than 0
    taxed = results_taxed(total, market_tax, value_pack_val) if hours > 0 else 0 # Apply market tax, value pack and extra profit if applicable if hours is greater than 0
    taxed_h = results_taxed_h(taxed, hours) if hours > 0 else 0  # Calculate taxed results per hour only if hours is greater than 0
    total_elixirs_cost = get_total_elixirs_cost(elixirs_cost_h, hours)  # Get the total cost of elixirs for the session

    total -= total_elixirs_cost  # Subtract elixirs cost
    taxed -= total_elixirs_cost  # Subtract elixirs cost after tax
    total_h -= elixirs_cost_h # Subtract elixirs cost per 1 hour
    taxed_h -= elixirs_cost_h # Subtract elixirs cost per 1 hour after tax

    return {
        'total': total,
        'total_h': total_h,
        'taxed': taxed,
        'taxed_h': taxed_h,
        'new_labels_input_text': recalculate_labels_input(total, data_input),
        'elixirs_cost': str(f"{total_elixirs_cost:,}")
    }

def get_total_elixirs_cost(elixirs_cost: int, hours: int) -> int:
    """
    Calculate the total cost of elixirs for the session based on the cost per hour and the number of hours.
        :param elixirs_cost: The cost of elixirs per hour.
        :param hours: The number of hours the session lasted.
        :return: The total cost of elixirs for the session.
    """
    return elixirs_cost * hours

def results_total(data_input: dict[str, tuple[str, str]], extra_breath_of_narcion: int) -> int | None:
    """
    Calculate the total results from the session based on the input data.
        :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        :param extra_breath_of_narcion: The total number of extra Breath of Narcions.
        :return: The total results from the session or None if an error occurs.
    """
    total = 0
    for name, (price, amount) in data_input.items():
        if name == 'Hours':
            continue  # Skip hours as it is not an item

        price = price.replace(',', '').replace(' ', '') if price != '' else '0' # Remove commas and spaces for validation
        if not price.isdigit():
            add_log(f"Invalid price for {name}: {price}. Expected a number.", "error")
            return None

        amount = amount.replace(',', '').replace(' ', '') if amount != '' else '0' # Remove commas and spaces for validation
        if not amount.isdigit():
            add_log(f"Invalid input for {name}: {amount}. Expected a number.", "error")
            return None
        
        if 'Breath of Narcion (' in name:
            total += (int(amount) +  extra_breath_of_narcion) * int(price)
        else:
            total += int(amount) * int(price)

    return total

def results_h(total: int, hours: int) -> int:
    """
    Calculate the total results per hour.
        :param total: The total results from the session.
        :param hours: The number of hours the session lasted.
        :return: The total results per hour.
    """
    return int(total / hours)

def results_taxed(total: int, market_tax: float, value_pack: float) -> int:
    """
    Calculate the results after applying market tax and value pack.
        :param total: The total results from the session.
        :param market_tax: The market tax percentage to apply.
        :param value_pack: The value pack percentage to apply.
        :return: The total results after tax and value pack.
    """
    taxed = total * (1 - market_tax)
    taxed += taxed * value_pack
    return int(taxed)

def results_taxed_h(taxed: int, hours: int) -> int:
    """
    Calculate the results after tax per hour.
        :param taxed: The total results after tax and value pack.
        :param hours: The number of hours the session lasted.
        :return: The total results after tax per hour.
    """
    return int(taxed / hours)

def recalculate_labels_input(total: int, data_input: dict[str, tuple[str, str]]) -> list[str]:
    """
    Recalculate the labels for input data based on the total results.
        :param total: The total results from the session.
        :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        :return: A list of recalculated labels for input data.
    """
    new_labels_input_text: list[str] = []
    for name, (price, amount) in data_input.items():
        if name == 'Hours':
            new_labels_input_text.append(name)
        else:
            price = price.replace(',', '').replace(' ', '') if price != '' else '0' # Remove commas and spaces for validation
            amount = amount.replace(',', '').replace(' ', '') if amount != '' else '0' # Remove commas and spaces for validation
            name_without_percent = name[:name.index('(') - 1]
            item_total = int(price) * int(amount)
            percent = (item_total / total) * 100 if total > 0 else 0
            if percent > 100:
                percent = 100.0
            new_labels_input_text.append(f"{name_without_percent} ({percent:.2f}%)")

    return new_labels_input_text
        
def get_extra_breath_of_narcions(data_input: dict[str, tuple[str, str]]) -> int:
    """
    Get the total number of extra Breath of Narcions from the input data.
        :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
        :return: The total number of extra Breath of Narcions.
    """
    extra_breath = 0
    for name, (_, amount) in data_input.items():
        if 'Breath of Narcion Bought' in name:
            extra_breath += int(amount.replace(',', '').replace(' ', '')) if amount else 0
        if 'Breath of Narcion Previous' in name:
            extra_breath += int(amount.replace(',', '').replace(' ', '')) if amount else 0

    return extra_breath