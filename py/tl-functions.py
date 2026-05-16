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

    def login(self):
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

        access_token = requests.post(f"{self.base_url}{ext_auth_token}", json=payload_login, headers=headers)

        self.bearer = "Bearer {}".format(access_token.json()["accessToken"])
    
    def _headers(self):
        return {
            "accNum": self.acc_num,
            "accept": "application/json",
            "authorization": self.bearer
        }