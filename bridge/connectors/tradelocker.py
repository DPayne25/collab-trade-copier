from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from config import ACCOUNTS


class TradeLockerConnector:
    def __init__(self) -> None:
        self.config = ACCOUNTS["tradelocker"]
        self.base_url = self.config["base_url"].rstrip("/")
        self.email = self.config["email"]
        self.password = self.config["password"]
        self.server = self.config["server"]
        self.account_id = str(self.config["account_id"])
        self.acc_num = str(self.config["acc_num"])
        self.token: Optional[str] = None

    def _headers(self, include_trade_headers: bool = False) -> Dict[str, str]:
        if not self.token:
            self.login()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        if include_trade_headers:
            headers["accNum"] = self.acc_num

        return headers

    def login(self) -> str:
        url = f"{self.base_url}/auth/jwt/token"
        payload = {
            "email": self.email,
            "password": self.password,
            "server": self.server,
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        token = data.get("accessToken")
        if not token:
            raise RuntimeError(f"TradeLocker login failed: no accessToken in response: {data}")

        self.token = token
        return token

    def health_check(self) -> str:
        try:
            if not self.token:
                self.login()

            url = f"{self.base_url}/auth/jwt/all-accounts"
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, headers=self._headers(False))
                response.raise_for_status()

            return "connected"
        except Exception as exc:
            return f"error: {exc}"

    def _get_instruments(self) -> list[dict[str, Any]]:
        url = f"{self.base_url}/trade/accounts/{self.account_id}/instruments"

        with httpx.Client(timeout=20.0) as client:
            response = client.get(url, headers=self._headers(True))
            response.raise_for_status()
            data = response.json()

        if data.get("s") != "ok":
            raise RuntimeError(f"TradeLocker instruments request failed: {data}")

        d = data.get("d")
        if not isinstance(d, dict):
            raise RuntimeError(f"TradeLocker instruments missing 'd' object: {data}")

        instruments = d.get("instruments")
        if not isinstance(instruments, list):
            raise RuntimeError(f"TradeLocker instruments missing list: {data}")

        return instruments

    def _find_instrument(self, symbol: str):
        instruments = self._get_instruments()

        if not instruments:
            raise RuntimeError(f"No instruments returned from TradeLocker for symbol lookup: {symbol}")

        for inst in instruments:
            name = (
                inst.get("name")
                or inst.get("symbol")
                or inst.get("tradableInstrumentName")
                or inst.get("displayName")
            )
            if str(name).upper() == symbol.upper():
                return inst

        raise RuntimeError(f"TradeLocker instrument not found for symbol: {symbol}")
    
    def _extract_trade_route_id(self, instrument: Dict[str, Any]) -> str:
        routes = instrument.get("routes", [])
        if isinstance(routes, list):
            for route in routes:
                route_type = str(route.get("type", "")).upper()
                if route_type == "TRADE":
                    return str(route.get("id"))

        raise RuntimeError(f"TRADE routeId not found for instrument: {instrument}")

    def _extract_tradable_instrument_id(self, instrument: Dict[str, Any]) -> str:
        for key in ("tradableInstrumentId", "id", "instrumentId"):
            value = instrument.get(key)
            if value is not None:
                return str(value)

        raise RuntimeError(f"tradableInstrumentId not found for instrument: {instrument}")

    def place_market_order(
        self,
        symbol: str,
        side: str,
        volume: float,
        stopPrice: float | None,
        tp: float | None,
    ) -> Dict[str, Any]:
        instrument = self._find_instrument(symbol)
        route_id = self._extract_trade_route_id(instrument)
        tradable_instrument_id = self._extract_tradable_instrument_id(instrument)

        url = f"{self.base_url}/trade/accounts/{self.account_id}/orders"

        payload: Dict[str, Any] = {
            "routeId": route_id,
            "tradableInstrumentId": tradable_instrument_id,
            "qty": volume,
            "side": side.upper(),
            "type": "MARKET",
            "validity": "IOC"
        }

        if stopPrice is not None:
            payload["stopLoss"] = stopPrice
        if tp is not None:
            payload["takeProfit"] = tp

        with httpx.Client(timeout=20.0) as client:
            response = client.post(url, headers=self._headers(True), json=payload)
            response.raise_for_status()
            data = response.json()

        if data.get("s") != "ok":
            return {
                "ok": False,
                "platform": "tradelocker",
                "raw": data,
                "target_order_id": None,
                "target_position_id": None,
                "status": "REJECTED",
                "reason": data.get("errmsg", "Unknown TradeLocker error"),
            }

        d = data.get("d", {}) if isinstance(data.get("d"), dict) else data

        d = data.get("d", {}) if isinstance(data.get("d"), dict) else {}

        target_order_id = d.get("orderId") or d.get("id")

        target_position_id = d.get("positionId")

        return {
            "ok": True,
            "platform": "tradelocker",
            "raw": data,
            "target_order_id": str(target_order_id) if target_order_id is not None else None,
            "target_position_id": str(target_position_id) if target_position_id is not None else None,
            "status": "OPENED",
        }

    def close_position(self, target_position_id: str) -> Dict[str, Any]:
        # Keep Stage 1 simple: do this after we confirm real market opens work.
        raise NotImplementedError("TradeLocker close_position not wired yet.")

    def modify_sl_tp(
        self,
        target_position_id: str,
        stopPrice: float | None,
        tp: float | None,
    ) -> Dict[str, Any]:
        # Keep Stage 1 simple: do this after we confirm real market opens work.
        raise NotImplementedError("TradeLocker modify_sl_tp not wired yet.")