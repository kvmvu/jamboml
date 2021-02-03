import pandas as pd
import json
import flat_table

from sqlalchemy import create_engine, exc
from keys import conn_str

engine = create_engine(conn_str, echo=True)


def get_sales():
    # read from json file and place in new dataframe
    with open('sales_from_start.json') as sales_data:
        read_content = json.load(sales_data)
        df = pd.json_normalize(read_content)

    new_df = flat_table.normalize(df)
    return new_df


def raw_data_to_sql():
    # read json from POS API
    raw = get_sales()
    raw.sort_values(by=['Created'], inplace=True, ascending=True)

    # create SQL table and insert raw data
    try:
        raw.to_sql('raw_sales', con=engine, if_exists='append', index=False)
    except exc.IntegrityError:
        pass
    e = engine.execute("SELECT * FROM raw_sales").fetchall()
    print(e)


def update_inventory():
    # read inventory data from API
    with open('inventory.json') as inventory_data:
        read_content = json.load(inventory_data)
        df = pd.json_normalize(read_content)

    inventory_df = flat_table.normalize(df)

    try:
        inventory_df.to_sql('inventory_raw', con=engine, if_exists='append', index=False)
    except exc.IntegrityError:
        pass
    e = engine.execute("SELECT * FROM inventory_raw").fetchall()
    print(e)


def update_customers():
    # read customer data from API
    with open('customers.json') as customers_data:
        read_content = json.load(customers_data)
        df = pd.json_normalize(read_content)

    customers_df = flat_table.normalize(df)

    try:
        customers_df.to_sql('customers_raw', con=engine, if_exists='append', index=False)
    except exc.IntegrityError:
        pass
    e = engine.execute("SELECT * FROM customers_raw").fetchall()
    print(e)


# raw_data_to_sql()
# update_inventory()
update_customers()
