import requests
import json
from requests.structures import CaseInsensitiveDict
from keys import *


def get_auth():
    response = requests.post(url, headers=headers, data=json.dumps(body))
    resp_data = json.loads(response.text)
    token = resp_data['access_token']
    return token


def get_sales():
    token = get_auth()
    header = CaseInsensitiveDict()
    header['Content-Type'] = 'application/json'
    header['Authorization'] = 'Bearer' f' {token}'
    header['Host'] = host
    sales = requests.get(reports,
                         headers=header,
                         data=json.dumps(sales_param)
                         )

    with open('sales_from_start.json', 'w') as f:
        json.dump(sales.json(), f)


def get_inventory():
    token = get_auth()
    header = CaseInsensitiveDict()
    header['Content-Type'] = 'application/json'
    header['Authorization'] = 'Bearer' f' {token}'
    header['Host'] = host
    inventory_data = requests.get(inventory,
                                  headers=header,
                                  data=json.dumps(inventory_param)
                                  )

    with open('inventory.json', 'w') as f:
        json.dump(inventory_data.json(), f)


def get_suppliers():
    token = get_auth()
    header = CaseInsensitiveDict()
    header['Content-Type'] = 'application/json'
    header['Authorization'] = 'Bearer' f' {token}'
    header['Host'] = host
    suppliers_data = requests.get(suppliers,
                                  headers=header,
                                  data=json.dumps(suppliers_param)
                                  )

    with open('suppliers.json', 'w') as f:
        json.dump(suppliers_data.json(), f)


def get_customers():
    token = get_auth()
    header = CaseInsensitiveDict()
    header['Content-Type'] = 'application/json'
    header['Authorization'] = 'Bearer' f' {token}'
    header['Host'] = host
    customers_data = requests.get(customers,
                                  headers=header,
                                  data=json.dumps(customers_param)
                                  )

    with open('customers.json', 'w') as f:
        json.dump(customers_data.json(), f)


# get_sales()
# get_inventory()
# get_suppliers()
get_customers()
