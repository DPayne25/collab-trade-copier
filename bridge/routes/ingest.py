from __future__ import annotations

from fastapi import APIRouter, HTTPException

from connectors.dxtrade import DXTradeConnector
from connectors.tradelocker import TradeLockerConnector
from db import get_trade_link, insert_trade_event, upsert_trade_link
from models import MT5TradeEvent
from services.dedupe import is_duplicate
from services.mapper import map_symbol
from services.risk import check_risk
from services.sizing import calculate_target_volume

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/mt5")
def ingest_mt5_trade(event: MT5TradeEvent) -> dict:
    event_dict = event.model_dump()

    if is_duplicate(event.event_id):
        return {"ok": True, "duplicate": True, "event_id": event.event_id}

    allowed, reason = check_risk(event_dict)
    if not allowed:
        raise HTTPException(status_code=403, detail=f"Trade blocked by risk engine: {reason}")

    insert_trade_event(event_dict)

    results = []

    for platform, connector in [
        ("tradelocker", TradeLockerConnector()),
        ("dxtrade", DXTradeConnector()),
    ]:
        mapped_symbol = map_symbol(event.symbol, platform)
        target_volume = calculate_target_volume(event.volume)

        if event.action == "OPEN":
            result = connector.place_market_order(
                symbol=mapped_symbol,
                side=event.side or "BUY",
                volume=target_volume,
                stopPrice=event.stopPrice,
                tp=event.tp,
            )
            if result.get("ok"):
                upsert_trade_link(
                    source_ticket=event.source_ticket,
                    target_platform=platform,
                    target_order_id=result.get("target_order_id"),
                    target_position_id=result.get("target_position_id"),
                    status=result["status"],
                )
            results.append(result)

        elif event.action == "CLOSE":
            link = get_trade_link(event.source_ticket, platform)
            if not link or not link.get("target_position_id"):
                results.append(
                    {
                        "ok": False,
                        "platform": platform,
                        "status": "SKIPPED",
                        "reason": "No target position mapping found",
                    }
                )
                continue

            result = connector.close_position(link["target_position_id"])
            upsert_trade_link(
                source_ticket=event.source_ticket,
                target_platform=platform,
                target_order_id=result.get("target_order_id"),
                target_position_id=result.get("target_position_id"),
                status=result["status"],
            )
            results.append(result)

        elif event.action == "MODIFY_stopPriceTP":
            link = get_trade_link(event.source_ticket, platform)
            if not link or not link.get("target_position_id"):
                results.append(
                    {
                        "ok": False,
                        "platform": platform,
                        "status": "SKIPPED",
                        "reason": "No target position mapping found",
                    }
                )
                continue

            result = connector.modify_stopPrice_tp(
                target_position_id=link["target_position_id"],
                stopPrice=event.stopPrice,
                tp=event.tp,
            )
            upsert_trade_link(
                source_ticket=event.source_ticket,
                target_platform=platform,
                target_order_id=result.get("target_order_id"),
                target_position_id=result.get("target_position_id"),
                status=result["status"],
            )
            results.append(result)

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported action: {event.action}")

    return {
        "ok": True,
        "event_id": event.event_id,
        "source_ticket": event.source_ticket,
        "results": results,
    }