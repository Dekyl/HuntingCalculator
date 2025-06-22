import sqlite3, time

from config.config import sql_file, time_cached, FlatDict, NestedDict
from logic.logs import add_log

def check_cached_data(data_items: dict[str, str]) -> tuple[dict[str, str], FlatDict]:
    """
    Check the cached data in the SQLite database to determine which items are outdated and which are up-to-date.
        :param data_items: Dictionary of item IDs and their names to check against the cache.
        :return: A tuple containing two dictionaries:
            - outdated_items: Items that need to be fetched (not in cache or outdated).
            - cached_items: Items that are up-to-date with their prices.
    """
    outdated_items: dict[str, str] = {}
    cached_items: FlatDict = {}

    conn = sqlite3.connect(sql_file)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        price REAL,
        last_updated TEXT
    )
    """)

    conn.commit()

    for item_id, item_name in data_items.items():
        cursor.execute("SELECT price, last_updated FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        time_now = time.time()
        if row: # Item found in cache
            price, last_updated_str = row
            last_updated = float(last_updated_str)

            if time_now - last_updated >= time_cached:
                add_log(f"Item {item_name} (ID: {item_id}) is outdated, needs to be fetched", "info")
                outdated_items[item_id] = item_name  # Item is outdated, needs to be fetched
            else:
                add_log(f"Using cached price for {item_name} (ID: {item_id})", "info")
                cached_items[item_id] = (item_name, int(price)) # Item is up-to-date, use cached price
        else:
            add_log(f"Item {item_name} (ID: {item_id}) not found in cache, needs to be fetched", "info")
            outdated_items[item_id] = item_name  # Item not found in cache (must be fetched)

    conn.close()

    return outdated_items, cached_items

def update_cached_data(data_items: NestedDict):
    """
    Update the cached data in the SQLite database with the fetched prices.
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
        cursor.execute("""
        INSERT OR REPLACE INTO items (id, price, last_updated)
        VALUES (?, ?, ?)
        """, (item_id, price, str(time.time())))
        add_log(f"Updated cached price for item ID {item_id} to {price}", "debug")

    conn.commit()
    conn.close()