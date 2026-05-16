import requests, configparser, json, Utc
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / '.config')

accNum = "1"

base_url = config['tradelocker-demo-1']['TL_URL']
email = config['tradelocker-demo-1']['TL_EMAIL']
password = config['tradelocker-demo-1']['TL_PASSWORD']
server = config['tradelocker-demo-1']['TL_SERVER']
accountID = int(config['tradelocker-demo-1']['TL_ACCOUNT_ID'])


# POST Fetch JWT Token
ext_auth_token = "backend-api/auth/jwt/token"

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

bearer_authorization = "Bearer {}".format(access_token.json()["accessToken"])


# Refresh JWT Token
ext_refresh_token = "backend-api/auth/jwt/refresh"

payload_refresh_token = {"refreshToken": access_token.json()["refreshToken"]}

headers_refresh_token = {
    "accept": "application/json",
    "content-type": "application/json"
}

refresh_token_response = requests.post(f"{base_url}{ext_refresh_token}", json=payload_refresh_token, headers=headers_refresh_token)


# Get List All Accounts
ext_all_accounts = "backend-api/auth/jwt/all-accounts"

headers_all_accounts = {
    "accept": "application/json",
    "authorization": bearer_authorization
}

all_accounts = requests.get(f"{base_url}{ext_all_accounts}", headers=headers_all_accounts)


# Get Data Configurations (headers of for the data)
ext_data_headers_config = "backend-api/trade/config"

headers_response_configurations = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

response_config = requests.get(f"{base_url}{ext_data_headers_config}", headers=headers_response_configurations)

with open('data/headers_config.json', 'w') as f:
    json.dump(response_config.json(), f, indent=2)

# Get Account Details
ext_account_details = "backend-api/trade/accounts"

headers_account_details = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

account_details = requests.get(f"{base_url}{ext_account_details}", headers=headers_account_details)
#print(account_details.text)
with open(f'data/{accountID}_account_details.json', 'w') as f:
    json.dump(account_details.json(), f, indent=2)


# List of Instruments
# type TRADE for trading operations on an instrument
# type INFO for information on instruments

ext_list_instruments = f"backend-api/trade/accounts/{accountID}/instruments" #...?locale=en" Enum: {ar, en, es, fr, js, ko, pl, pt, ru, tr, ua, zh_sm, zh_tr}

headers_list_instruments = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}


list_instruments = requests.get(f"{base_url}{ext_list_instruments}", headers=headers_list_instruments)


with open(f'data/{accountID}_list_instruments.json', 'w') as f:
    json.dump(list_instruments.json(), f, indent=2)

    
# Get Non-final Orders
ext_non_final_orders = f"backend-api/trade/accounts/{accountID}/orders" #...?from={Unix-millisecond-UTC}&to={Unix-millisecond-UTC}&tradableInstrumentId"

headers_non_final_orders = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

non_final_orders = requests.get(f"{base_url}{ext_non_final_orders}", headers=headers_non_final_orders)

with open(f'data/{accountID}_non_final_orders.json', 'w') as f:
    json.dump(non_final_orders.json(), f, indent=2)

# Get Order history
ext_order_history = f"backend-api/trade/accounts/{accountID}/ordersHistory" #...?from={Unix-millisecond-UTC}&to={Unix-millisecond-UTC}&tradableInstrumentId"

headers_order_history = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

orderHistory = requests.get(f"{base_url}{ext_order_history}", headers=headers_order_history)



with open(f'data/{accountID}_order_history.json', 'w') as f:
    json.dump(orderHistory.json(), f, indent=2)

# Get Open Positions
ext_open_positions = f"backend-api/trade/accounts/{accountID}/positions"

headers_open_positions = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

open_positions = requests.get(f"{base_url}{ext_open_positions}", headers=headers_open_positions)

with open(f'data/{accountID}_open_positions.json', 'w') as f:
    json.dump(open_positions.json(), f, indent=2)

# GET Account's Current Details
ext_account_current_details = f"backend-api/trade/accounts/{accountID}/state"

headers_account_current_details = {
    "accNum": accNum,
    "accept": "application/json",   
    "authorization": bearer_authorization
}

account_current_details = requests.get(f"{base_url}{ext_account_current_details}", headers=headers_account_current_details)

with open(f'data/{accountID}_account_current_details.json', 'w') as f:
    json.dump(account_current_details.json(), f, indent=2)  

# GET Instruments Details

tradableInstrumentId = "4665"
info_route_id = list_instruments.json()['d']['instruments'][0]['routes'][1]['id']
trade_route_id = list_instruments.json()['d']['instruments'][0]['routes'][0]['id']

#info_route_id_local = f"data/{accountID}_list_instruments.json{['d']['instruments'][0]['routes'][0]['id']}" # TODO read the json file make a variable
#print(info_route_id)
#info_route_id_api= list_instruments.json(){"d":{"instruments"}:[{"routes"}:[{"id"}]}]

ext_instrument_details = f"backend-api/trade/instruments/{tradableInstrumentId}?routeId={info_route_id}" #...&locale=en" Enum: {ar, en, es, fr, js, ko, pl, pt, ru, tr, ua, zh_sm, zh_tr}

headers_instrument_details = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

instruments_details = requests.get(f"{base_url}{ext_instrument_details}", headers=headers_instrument_details)

with open(f'data/{accountID}_instrument_details.json', 'w') as f:
    json.dump(instruments_details.json(), f, indent=2)


# Get Trade Session Information
sessionId = 1

ext_trade_session = f"backend-api/trade/sessions/{sessionId}"

headers_trade_session = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

trade_session = requests.get(f"{base_url}{ext_trade_session}", headers=headers_trade_session)

with open(f'data/{accountID}_{sessionId}_trade_session.json', 'w') as f:
    json.dump(trade_session.json(),f, indent=2)

# GET Allowed Orders Operation
sessionStatusId = 1

ext_allowed_orders_operation = f"backend-api/trade/sessionStatuses/{sessionStatusId}"

headers_allowed_orders_operation = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization   
}

allowed_orders_operation = requests.get(f"{base_url}{ext_allowed_orders_operation}", headers=headers_allowed_orders_operation)

with open(f'data/{accountID}_{sessionStatusId}_allowed_orders_operation.json', 'w') as f:
    json.dump(allowed_orders_operation.json(), f, indent=2)


# GET Current Daily Bar
barType = "ASK" # Enum: ASK, BID, TRADE

ext_current_daily_bar = f"backend-api/trade/dailyBar?routeId={info_route_id}&barType={barType}&tradableInstrumentId={tradableInstrumentId}"

headers_current_daily_bar = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

current_daily_bar = requests.get(f"{base_url}{ext_current_daily_bar}", headers=headers_current_daily_bar)

with open(f'data/{accountID}_{Utc().now().date()}_daily_bar.json', 'w') as f:
    json.dump(current_daily_bar.json(), f, indent=2)

# GET Historical Bars
resolution = "1D" # Enum: 1M, 1W, 1D, 4H, 1H, 30m, 15m, 5m, 1m
from_date = 1777608000000 # Unix millisecond UTC
to_date = Utc.now().timestamp() * 1000


ext_historical_bars = f"backend-api/trade/history?routeId={trade_route_id}&from={from_date}&resolution={resolution}&to={to_date}&tradableInstrumentId={tradableInstrumentId}"

headers_historical_bars = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

historical_bars = requests.get(f"{base_url}{ext_historical_bars}", headers=headers_historical_bars)

with open(f'data/{accountID}_historical_bars.json', 'w') as f:
    json.dump(historical_bars.json(), f, indent=2)



# GET Current Prices
ext_current_prices = f"backend-api/trade/quotes"

headers_current_prices = {
    "accNum": accNum,
    "accept": "application/json",
    "authorization": bearer_authorization
}

current_prices = requests.get(f"{base_url}{ext_current_prices}", headers=headers_current_prices)

with open(f'data/current_prices.json', 'w') as f:
    json.dump(current_prices.json(), f, indent=2)

# POST Place a New Order
ext_new_order = f"backend-api/trade/accounts/{accountID}/orders"


payload_new_order = {
    "side": "buy", # Enum: buy, sell
    "type": "market", # Allows 'limit', 'market', 'stop'
    "validity": "IOC", # 'GTC' for pending "type": 
    "price": 1,
    "qty": 1,
    "routeId": 1,
    "strategyId": "1",
    "stopLoss": 1,
    "stopLossType": "absolute", # Enum: absolute, offset, trailingOffset
    "takeProfit": 2,
    "stopPrice": 2,
    "takeProfitType": "absolute", # Enum limit, market, stop
   # "trStopOffset": 3, 
    "tradableInstrumentId": tradableInstrumentId
}
headers_new_order = {
    "accNum": "accNum",
   # "developer-api-key": "string", #TODO
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": bearer_authorization
}

new_order = requests.post(f"{base_url}{ext_new_order}", json=payload_new_order, headers=headers_new_order)



# DELETE Cancel All Orders
ext_cancel_all_orders = f"backend-api/trade/accounts/{accountID}/orders" #...?tradableInstrumentId=####"

headers_cancel_all_orders = {
    "accNum": accNum,
   # "developer-api-key": "string",
    "accept": "application/json",
    "authorization": bearer_authorization
}

cancel_all_orders = requests.delete(f"{base_url}{ext_cancel_all_orders}", headers=headers_cancel_all_orders)


# DELETE Close All Positions
ext_close_all_positions = f"backend-api/trade/accounts/{accountID}/positions" #...?tradableInstrumentId=####&strategyId=####

headers_close_all_positions = {
    "accNum": accNum,
   # "developer-api-key": "string",
    "accept": "application/json",
    "authorization": bearer_authorization
}

close_all_positions = requests.delete(f"{base_url}{ext_close_all_positions}", headers=headers_close_all_positions)


# DELETE Cancel an Existing Order
orderId = 1

ext_cancel_existing_order = f"backend-api/trade/orders/{orderId}"

headers_cancel_existing_order = {
    "accNum": accNum,
   # "developer-api-key": "string",
    "accept": "application/json",
    "authorization": bearer_authorization
}

cancel_existing_order = requests.delete(f"{base_url}{ext_cancel_existing_order}", headers=headers_cancel_existing_order)

# PATCH Modify an Existing Order
ext_modify_existing_order = f"backend-api/trade/orders/{orderId}"

payload = {
    "price": 1,
    "qty": 1,
    "stopLoss": 1,
    "stopLossType": "absolute", # Enum: absolute, offset, trailingOffset
    "stopPrice": 1,
    "takeProfit": 1,
    "takeProfitType": "absolute", # Enum: absolute, offset
    "trStopOffset": 1,
    "validity": "GTC" # Accepts IOC
}
headers_modify_existing_order = {
    "accNum": "accNum",
   # "developer-api-key": "",
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": bearer_authorization
}

modify_existing_order = requests.patch(f"{base_url}{ext_modify_existing_order}", json=payload, headers=headers_modify_existing_order)

# DELETE Close a Position
positionId = 1

ext_close_position = f"backend-api/trade/positions/{positionId}" #...?strategyId=AbC"

payload_close_position = { "qty": 1}

headers_close_position = {
    "accNum": accNum,
   # "developer-api-key": "",
    "content-type": "application/json",
    "authorization": bearer_authorization
}

close_position = requests.delete(f"{base_url}{ext_close_position}", json=payload_close_position, headers=headers_close_position)

# PATCH Modify Position
ext_modify_position = f"backend-api/trade/positions/{positionId}" #...?strategyId=AbC"

payload_modify_position = {
    "stopLoss": 1,
    "takeProfit": 1,
    "trailingOffset": 1
}

headers_modify_position = {
    "accNum": accNum,
   # "developer-api-key": "",
   "content-type": "application/json",
   "authorization": bearer_authorization
}

modify_position = requests.patch(f"{base_url}{ext_modify_position}", json=payload_modify_position, headers=headers_modify_position)