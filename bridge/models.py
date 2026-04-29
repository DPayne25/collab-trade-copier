from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


ActionType = Literal["OPEN", "CLOSE", "MODIFY_SLTP"]
SideType = Literal["BUY", "SELL"]


class MT5TradeEvent(BaseModel):
    event_id: str = Field(..., min_length=1)
    source_platform: Literal["mt5"] = "mt5"
    source_account: str
    source_ticket: str
    action: ActionType
    symbol: str
    side: Optional[SideType] = None
    volume: float = 0.0
    price: Optional[float] = None
    stopPrice: Optional[float] = None
    tp: Optional[float] = None
    magic: Optional[int] = None
    comment: Optional[str] = None
    timestamp: datetime


class HealthStatus(BaseModel):
    status: str
    tradelocker: str
    dxtrade: str