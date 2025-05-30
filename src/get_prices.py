import json
import pycurl
from io import BytesIO

def get_sell_price(item_data):
    item_data = item_data[0:item_data.find("history")]
    index = 0
    last_sell_val = 0

    while index < len(item_data):
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

def get_buy_price(elixir_data):
    elixir_data = elixir_data[0:elixir_data.find("history")]
    index = 0
    buy_price = 0

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

def connect_sever(id_item, connection):
    url_base = "https://api.blackdesertmarket.com/item/" + id_item + "/0?region=eu"
    buffer = BytesIO()
    response_code = None
    
    connection.setopt(connection.URL, url_base)
    connection.setopt(connection.WRITEDATA, buffer)

    while response_code != 200:
        try:
            connection.perform()
            response_code = connection.getinfo(pycurl.HTTP_CODE)
        except Exception as e:
            print(e)

    return buffer.getvalue().decode('utf-8')

def update_prices(items_ids, elixirs_ids, prices, data):
    index = 0

    connection = pycurl.Curl()
    connection.setopt(connection.HTTPHEADER, ['accept: */*'])
    connection.setopt(connection.CONNECTTIMEOUT, 1)

    print("Items")

    for id in items_ids:
        body_sell_price = connect_sever(id, connection)
        sell_price = get_sell_price(body_sell_price)
        print(sell_price)

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

    print("Elixirs")
    elixirs_cost = 0

    for id_elixir in elixirs_ids:
        body_buy_price = connect_sever(id_elixir, connection)
        elixir_cost = int(get_buy_price(body_buy_price))
        print(elixir_cost)

        if (id_elixir == '771'):
            elixir_cost *= 3
        else:
            elixir_cost *= 4

        elixirs_cost += elixir_cost

    data['elixirs_cost'] = elixirs_cost
    
    connection.close()

def search_prices():
    with open('./assets/data.json', 'r') as file:
        data = json.load(file)

    items_ids = data['items_ids']
    prices = data['prices']
    elixirs_ids = data['elixirs_ids']

    update_prices(items_ids, elixirs_ids, prices, data)
    
    file.close()

    with open('./assets/data.json', 'w') as file:
        json.dump(data, file)
