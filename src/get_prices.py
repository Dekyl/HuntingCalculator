import json
import pycurl
from io import BytesIO
from logs import add_log
from typing import Any

def get_sell_price(item_data:str) -> str:
    """
    Fetch selling price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :type item_data: str
        :return: The selling price of the item as a string.
        :rtype: str
    """
    item_data = item_data[0:item_data.find("history")]
    index = 0
    last_sell_val = "0"

    while index < len(item_data):
        # Takes index of first "sellCount", iterates through all "sellCount" in item_data until it finds the best match to gain maximum profit (selling higher price with no sellers)
        index = item_data.find("sellCount")
        if index == -1:
            return last_sell_val
        
        index += len("sellCount") + 2
        left_index_price = item_data.find("onePrice", index) + len("onePrice") + 2
        right_index_price = item_data.find("}", left_index_price)
        last_sell_val = item_data[left_index_price:right_index_price]

        if item_data[index] != "0":
            return last_sell_val
        
        item_data = item_data[index:len(item_data)]
        index = 0

    return last_sell_val

def get_buy_price(elixir_data:str) -> str:
    """
    Fetch buying price of an elixir from the provided data.
        :param elixir_data: The raw data string containing response information from API.
        :type elixir_data: str
        :return: The buying price of the elixir as a string.
        :rtype: str
    """
    elixir_data = elixir_data[0:elixir_data.find("history")]
    index = 0
    buy_price = "0"

    while index < len(elixir_data):
        index = elixir_data.find("buyCount")

        if index == -1:
            break
        
        index += len("buyCount") + 2

        left_index_price = elixir_data.find("onePrice", index) + len("onePrice") + 2
        right_index_price = elixir_data.find("}", left_index_price)
        buy_price = elixir_data[left_index_price:right_index_price]

        if elixir_data[index] != "0":
            return buy_price
        
        elixir_data = elixir_data[index:len(elixir_data)]
        index = 0

    return buy_price

def connect_sever(id_item: str, connection: pycurl.Curl, region: str = "eu") -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir data.
        :param id_item: The ID of the item or elixir to fetch.
        :type id_item: str
        :param connection: The pycurl connection object to use for the request.
        :type connection: pycurl.Curl
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :return: The response body as a string.
    """
    url_base = f"https://api.blackdesertmarket.com/item/{id_item}/0?region={region}"
    buffer = BytesIO()
    response_code = None
    
    connection.setopt(connection.URL, url_base) # type: ignore
    connection.setopt(connection.WRITEDATA, buffer) # type: ignore

    while response_code != 200:
        try:
            connection.perform()
            response_code = connection.getinfo(pycurl.HTTP_CODE) # type: ignore
        except Exception as e:
            print(e)

    return buffer.getvalue().decode('utf-8')

def update_prices(data: dict[str, Any]) -> None:
    """
    Update the prices of items and elixirs in the provided data dictionary by fetching them from the Black Desert Market API.
        :param data: Dictionary containing item IDs, prices, and elixir IDs.
        :type data: dict[str, Any]
        :return: True if prices were successfully updated, False otherwise.
    """
    index = 0
    items_ids = data['items_ids']
    prices = data['prices']
    elixirs_ids = data['elixirs_ids']

    connection = pycurl.Curl()
    headers: list[str] = ['accept: */*']
    connection.setopt(connection.HTTPHEADER, headers) # type: ignore
    connection.setopt(connection.CONNECTTIMEOUT, 1) # type: ignore

    add_log("Connecting to Black Desert Market API to get prices...", "info")

    for id in items_ids:
        body_sell_price = connect_sever(id, connection, data["region"])
        sell_price = get_sell_price(body_sell_price)

        if id == "3564":
            data['price_master_special_stuffed'] = int(sell_price)
            continue

        if id == "3554":
            data['price_master_stuffed'] = int(sell_price)
            break

        while prices[index] == 0:
            index += 1

        prices[index] = int(sell_price)
        index += 1

    items_log = "Items: {\n"
    for id, price in zip(items_ids, prices):
        items_log += f"\tItem ID {id}: Price {price:,}\n"
    items_log += "}"
    add_log(items_log, "info")
    elixirs_cost: list[int] = []

    for id_elixir in elixirs_ids:
        body_buy_price = connect_sever(id_elixir, connection)
        elixir_cost = int(get_buy_price(body_buy_price))

        if (id_elixir == '771'): # Deep sea perfume with a duration of 20 minutes so 3 per hour (thats the multiplier applied)
            elixir_cost *= 3
        else: # Rest of elixirs with a duration of 15 minutes so 4 per hour (thats the multiplier applied)
            elixir_cost *= 4

        elixirs_cost.append(elixir_cost)

    data['elixirs_cost'] = sum(elixirs_cost)

    elixirs_log = "Elixirs: {\n"
    for id, cost in zip(elixirs_ids, elixirs_cost):
        elixirs_log += f"\tElixir ID {id}: Cost {cost:,}\n"
    elixirs_log += "}"
    add_log(elixirs_log, "info")
    add_log("Total elixirs cost: " + str(data['elixirs_cost']), "info")
    
    connection.close()

def search_prices() -> bool:
    """
    Search for the current prices of items and elixirs from the Black Desert Market API and save them in a JSON file.
    """
    try:
        with open('./res/data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        add_log("Data JSON file not found. Please ensure that 'data.json' exists in the 'res' directory.", "error")
        return False

    update_prices(data)

    with open('./res/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return True