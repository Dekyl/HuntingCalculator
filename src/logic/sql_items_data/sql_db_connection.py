import sqlite3, time

from config.config import sql_file, time_cached, FlatDict, NestedDict
from logic.logs import add_log

def check_cached_data(data_items: dict[str, str], region: str) -> tuple[dict[str, str], FlatDict]:
    """
    Check the cached data in the SQLite database to determine which items are outdated and which are up-to-date.
        :param data_items: Dictionary of item IDs and their names to check against the cache.
        :param region: The region for which the data is being checked (not used in this function but can be useful for future extensions).
        :return: A tuple containing two dictionaries:
            - outdated_items: Items that need to be fetched (not in cache or outdated).
            - cached_items: Items that are up-to-date with their prices.
    """
    outdated_items: dict[str, str] = {}
    cached_items: FlatDict = {}

    conn = sqlite3.connect(sql_file)
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS items (
        id TEXT,
        region TEXT,
        price REAL,
        last_updated REAL,
        PRIMARY KEY (id, region)
    )
    """)

    conn.commit()

    for item_id, item_name in data_items.items():
        cursor.execute(f"SELECT price, last_updated FROM items WHERE id = ? AND region = ?", (item_id, region))
        row = cursor.fetchone()

        time_now = time.time()
        if row: # Item found in cache
            price, last_updated_str = row
            last_updated = last_updated_str

            if time_now - last_updated >= time_cached:
                add_log(f"Item {item_name} (ID: {item_id}) is outdated, needs to be fetched", "debug")
                outdated_items[item_id] = item_name  # Item is outdated, needs to be fetched
            else:
                add_log(f"Item {item_name} (ID: {item_id}) is up to date, no need to be fetched", "debug")
                cached_items[item_id] = (item_name, int(price)) # Item is up-to-date, use cached price
        else:
            add_log(f"Item {item_name} (ID: {item_id}) not found in cache, needs to be fetched", "debug")
            outdated_items[item_id] = item_name  # Item not found in cache (must be fetched)

    conn.close()

    return outdated_items, cached_items

def update_cached_data(data_items: NestedDict, region: str):
    """
    Update the cached data in the SQLite database with the fetched prices.
        :param region: The region for which the data is being updated (not used in this function but can be useful for future extensions).
        :param data_items: Nested dictionary containing items, elixirs, lightstones, and imperfect lightstones with their prices.
    """
    items = data_items["items"]
    elixirs = data_items["elixirs"]
    lightstones = data_items["lightstones"]
    imperfect_lightstones = data_items["imperfect_lightstones"]

    update_items: dict[str, int] = {}
    for item_id, (_, price) in items.items():
        update_items[item_id] = price
    
    for elixir_id, (_, price) in elixirs.items():
        update_items[elixir_id] = price

    for lightstone_id, (_, price) in lightstones.items():
        update_items[lightstone_id] = price

    for imperfect_lightstone_id, (_, price) in imperfect_lightstones.items():
        update_items[imperfect_lightstone_id] = price

    conn = sqlite3.connect(sql_file)
    cursor = conn.cursor()

    for item_id, price in update_items.items():
        cursor.execute(f"""
        INSERT OR REPLACE INTO items (id, region, price, last_updated)
        VALUES (?, ?, ?, ?)
        """, (item_id, region, price, time.time()))
        add_log(f"Updated cached price for item ID {item_id} to {price}", "debug")

    conn.commit()
    conn.close()