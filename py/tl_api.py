import requests, configparser, json
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / '.config')

accNum = "1"

base_url = config['tradelocker-demo-1']['TL_URL']
email = config['tradelocker-demo-1']['TL_EMAIL']
password = config['tradelocker-demo-1']['TL_PASSWORD']
server = config['tradelocker-demo-1']['TL_SERVER']
accountID = int(config['tradelocker-demo-1']['TL_ACCOUNT_ID'])


# Fetch JWT Token
ext_auth_token = "/backend-api/auth/jwt/token"

payload = {
    "email": email,
    "password": password,
    "server": server
}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

access_token = requests.post(f"{base_url}{ext_auth_token}", json=payload, headers=headers)

print(access_token.text)
print(access_token.json()["accessToken"])
bearer_authorization = "Bearer {}".format(access_token.json()["accessToken"])

# Refresh JWT Token #TODO @AbdulAziz
ext_refresh_token = "/backend-api/auth/jwt/refresh"

payload_refresh_token = {"refreshToken": access_token.json()["refreshToken"]}

headers_refresh_token = {
    "accept": "application/json",
    "content-type": "application/json"
}

refresh_token_response = requests.post(f"{base_url}{ext_refresh_token}", json=payload_refresh_token, headers=headers_refresh_token)

# Get List All Accounts
ext_all_accounts = "/backend-api/auth/jwt/all-accounts"

headers_all_accounts = {
    "accept": "application/json",
    "authorization": bearer_authorization
}

all_accounts = requests.get(f"{base_url}{ext_all_accounts}", headers=headers_all_accounts)


# Get Data Configurations (headers of for the data)
ext_data_headers_config = "/backend-api/trade/config"

headers_response_configurations = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

response_config = requests.get(f"{base_url}{ext_data_headers_config}", headers=headers_response_configurations)

with open('data/headers_config.json', 'w') as f:
    json.dump(response_config.json(), f, indent=2)

# Get Account Details
ext_account_details = "/backend-api/trade/accounts"

headers_account_details = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

account_details = requests.get(f"{base_url}{ext_account_details}", headers=headers_account_details)

with open(f'data/{accountID}_account_details.json', 'w') as f:
    json.dump(account_details.json(), f, indent=2)

# List of Instruments #TODO @AbdulAziz


# Get Non-final Orders #TODO @AbdulAziz


# Get Order history
ext_order_history = f"/backend-api/trade/accounts/{accountID}/ordersHistory"

headers_order_history = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

orderHistory = requests.get(f"{base_url}{ext_order_history}", headers=headers_order_history)


with open(f'data/{accountID}_order_history.json', 'w') as f:
    json.dump(orderHistory.json(), f, indent=2)

# Get Open Positions
ext_open_positions = f"/backend-api/trade/accounts/{accountID}/positions"

headers_open_positions = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

open_positions = requests.get(f"{base_url}{ext_open_positions}", headers=headers_open_positions)

with open(f'data/{accountID}_open_positions.json', 'w') as f:
    json.dump(open_positions.json(), f, indent=2)

# Get Account's Current Details
ext_account_current_details = f"/backend-api/trade/accounts/{accountID}/state"

headers_account_current_details = {
    "accNum": accNum,
    "accept": "application/json",   
    "authorization": bearer_authorization
}

account_current_details = requests.get(f"{base_url}{ext_account_current_details}", headers=headers_account_current_details)

with open(f'data/{accountID}_account_current_details.json', 'w') as f:
    json.dump(account_current_details.json(), f, indent=2)  
