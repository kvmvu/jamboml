import requests
import json

# for working with GSheets API
import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from requests.structures import CaseInsensitiveDict
from keys import *


def get_auth():
    response = requests.post(url, headers=headers, data=json.dumps(body))
    resp_data = json.loads(response.text)
    token = resp_data['access_token']
    return token


def gsheet_api_check(SCOPES):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def pull_sheet_data(SCOPES, SPREADSHEET_ID, DATA_TO_PULL):
    creds = gsheet_api_check(SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=DATA_TO_PULL).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        rows = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                  range=DATA_TO_PULL).execute()
        data = rows.get('values')
        print("COMPLETE: Data copied")
        return data


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
# get_customers()
gsheet_api_check(SCOPES)
