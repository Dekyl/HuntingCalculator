import json
from logic.logs import add_log

market_tax:int = 0
value_pack:int = 0
prices:list[int] = []
price_master_special_stuffed:int = 0
price_master_stuffed:int = 0
elixirs_cost:int = 0
hours:int = 1
results_tot:int = 0
results_tax:int = 0
gains_per_item:list[int] = []
results_tot_percentage:int = 0
breath_of_narcion_price:int = 0
n_breath_bought:int = 0

def load_data() -> bool:
    """
    Load the data from the JSON file and initialize global variables.
    """
    global market_tax, value_pack, prices, price_master_special_stuffed, elixirs_cost, price_master_stuffed, breath_of_narcion_price
    try:
        with open('./res/data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

            market_tax = data['market_tax']
            value_pack = data['value_pack']
            prices = data['prices']
            price_master_special_stuffed = data['price_master_special_stuffed']
            price_master_stuffed = data['price_master_stuffed']
            elixirs_cost = data['elixirs_cost']

        breath_of_narcion_price = prices[9]
    except FileNotFoundError:
        add_log("Data JSON file not found. Please ensure that 'data.json' exists in the 'res' directory.", "error")
        return False
    
    return True

def check_data_received(data_input: list[str]) -> bool:
    for i in range(len(data_input)):
        val = data_input[i]
        for j in range(len(val)):
            if ord(val[j]) < 48 or ord(val[j]) > 57:
                return False
    return True

def results_total(data_input: list[str]) -> int:
    global hours, results_tot, gains_per_item, results_tot_percentage, n_breath_bought
    
    results_tot = 0
    results_tot_percentage = 0
    n_breath_bought = 0
    n_breath_previous = 0

    gains_per_item = []
    gains_per_item = [0] * (len(data_input)-1)

    valid = check_data_received(data_input)

    if valid == False:
        return -elixirs_cost
    
    if data_input[len(data_input)-1] != '' and data_input[len(data_input)-1] != '0':
        hours = int(data_input[len(data_input)-1])
    else:
        data_input[len(data_input)-1] = '1'
        hours = 1

    for i in range(len(data_input)-1):
        actual_price = 0
        if data_input[i] == '':
            data_input[i] = str(actual_price)
        elif i == 9 or i == 20 or i == 21:
            actual_price = 0
        elif i == 16:
            if data_input[20] != '':
                n_breath_bought = int(data_input[20])
            
            if data_input[21] != '':
                n_breath_previous = int(data_input[21])

            green_hide = int(data_input[10])
            blue_hide = int(data_input[11])
            n_lion_head = int(data_input[16])
            breath_of_narcion = int(data_input[9]) + n_breath_bought + n_breath_previous

            n_blue_heads = int(green_hide/60)
            n_yellow_heads = int(blue_hide/50)
            n_yellow_heads = min(n_blue_heads, n_lion_head, n_yellow_heads) # If lion heads are the limit or green hides are

            # Simple yellow lion head
            if n_yellow_heads > 0:
                n_yellow_special_heads = int(breath_of_narcion/2)
                n_yellow_special_heads = min(n_yellow_heads, n_yellow_special_heads) # If simple yellow lion heads are the limit or breath of narcion are

                n_yellow_heads -= n_yellow_special_heads

                actual_price = n_yellow_special_heads * price_master_special_stuffed + n_yellow_heads * price_master_stuffed

                n_lion_head -= n_yellow_heads
                n_lion_head -= n_yellow_special_heads

            actual_price += n_lion_head * prices[i]
        elif i == 19:
            actual_price = int(int(data_input[i])/10)*5 * prices[4]
        else:
            actual_price = prices[i]*int(data_input[i])

        gains_per_item[i] = actual_price
        results_tot_percentage += actual_price

        results_tot += actual_price

    # Adds the extra profit from processing materials instead of selling them at once
    #if results_tot != 0:
        #results_tot += diff_profit_processed*hours

    return results_tot - elixirs_cost*hours - breath_of_narcion_price*n_breath_bought

def results_h() -> int:
    return int((results_tot - elixirs_cost*hours - breath_of_narcion_price*n_breath_bought)/hours)

def results_taxed() -> int:
    global results_tax
    results_tax = 0
    results_tax = results_tot*(1-market_tax)
    results_tax += results_tax*value_pack
    return int(results_tax - elixirs_cost*hours - breath_of_narcion_price*n_breath_bought)

def results_taxed_h() -> int:
    return int((results_tax - elixirs_cost*hours - breath_of_narcion_price*n_breath_bought)/hours)

def get_gains_per_item() -> list[int]:
    return gains_per_item

def get_results_tot_percentage() -> int:
    return results_tot_percentage

def get_percentage_item(actual_label: str, gains_item: int, total_gains: int) -> str:
    """
    Returns the percentage of gains for a specific item formatted as a string.
        :param actual_label: The label of the item, which may include a name and a percentage.
        :param gains_item: The gains for the specific item.
        :param total_gains: The total gains from all items.
        :return: A string containing the item name and its percentage of total gains.
    """
    new_text = actual_label[0:actual_label.rfind(" ")]

    if total_gains == 0:
        new_text += " (" + f"{0:.2f}" + "%)"
        return new_text
    
    actual_percent = gains_item / total_gains * 100

    if actual_percent < 0:
        actual_percent = 0

    actual_percent = f"{actual_percent:.2f}"

    new_text += " (" + actual_percent + "%)"

    return new_text