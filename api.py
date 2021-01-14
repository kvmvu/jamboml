import requests
import json
from requests.structures import CaseInsensitiveDict
from keys import *


def get_auth():
    response = requests.post(url, headers=headers, data=json.dumps(body))
    resp_data = json.loads(response.text)
    token = resp_data['access_token']
    return token


def generate_data():
    token = get_auth()
    header = CaseInsensitiveDict()
    header['Content-Type'] = 'application/json'
    header['Authorization'] = 'Bearer' f' {token}'
    header['Host'] = host
    sales = requests.get(reports,
                         headers=header,
                         data=json.dumps(param)
                         )

    with open('sales_from_start.json', 'w') as f:
        json.dump(sales.json(), f)


generate_data()
