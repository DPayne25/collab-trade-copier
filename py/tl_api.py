import requests, configparser
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / '.config')

url_access_token = "https://demo.tradelocker.com/backend-api/auth/jwt/token" 

# config['tradelocker']['TL_URL']

payload = {
    "email": config['tradelocker']['TL_EMAIL'],
    "password": config['tradelocker']['TL_PASSWORD'],
    "server": config['tradelocker']['TL_SERVER']
}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

# Access token

access_token = requests.post(url_access_token, json=payload, headers=headers)

print(access_token.text)
print(access_token.json()["accessToken"])
print(access_token.status_code)

# ===========================================================================================================================================
# ===========================================================================================================================================


# ===========================================================================================================================================
# All accounts
# ===========================================================================================================================================

headers_all_accounts = {
    "accept": "application/json",
    "authorization": "Bearer {}".format(access_token.json()["accessToken"])
}


all_accounts = requests.get("{}/backend-api/auth/jwt/all-accounts".format(config['tradelocker']['TL_URL']), headers=headers_all_accounts)
print(all_accounts.text)