import requests, configparser, json
from datetime import datetime, timezone
from pathlib import Path

class TradeLockerClient:
    def __init__(self, name, base_url, email, password, server, account_id, acc_num, role):
        self.name = name
        self.base_url = base_url
        self.email = email
        self.password = password
        self.server = server
        self.account_id = account_id
        self.acc_num = acc_num
        self.role = role
        self.bearer = None
        self.refresh_token = None
        self.token_expire_date = None

    def login(self):
        if  self.token_expire_date is None:
            # POST Fetch JWT Token
            ext_auth_token = "backend-api/auth/jwt/token"

            payload_login  = {
                "email": self.email,
                "password": self.password,
                "server": self.server
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }

            access_token = requests.post(f'{self.base_url}{ext_auth_token}', json=payload_login, headers=headers)
            
            print(access_token.status_code)
            self.bearer = f'Bearer {access_token.json()["accessToken"]}'
            self.token_expire_date = access_token.json()["expireDate"]
            return
        expire_date = datetime.fromisoformat(self.token_expire_date.replace('Z', '+00:00')).timestamp()
        current_time = datetime.now(timezone.utc).timestamp()
        if current_time >= (expire_date - 300):
            # Refresh JWT Token (Put into a condition)
            ext_refresh_token = "backend-api/auth/jwt/refresh"

            self.refresh_token = {"refreshToken": access_token.json()["refreshToken"]}
            
            headers_refresh_token = {
                "accept": "application/json",
                "content-type": "application/json"
            }

            refresh_token_response = requests.post(f'{self.base_url}{ext_refresh_token}', json=self.refresh_token, headers=headers_refresh_token)
            
            print(refresh_token_response.status_code)
            self.bearer = f'Bearer {refresh_token_response.json()["accessToken"]}'
            self.token_expire_date = refresh_token_response.json()["expireDate"]
        else:
            return

    def _headers(self):
        return {
            "accNum": self.acc_num,
            "accept": "application/json",
            "authorization": self.bearer
        }
    
    