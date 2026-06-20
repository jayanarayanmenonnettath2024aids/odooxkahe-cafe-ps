"""
WebSocket router — real-time event streaming.
"""

import json
import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect

from app.core.websocket_manager import ws_manager

logger = logging.getLogger("cafepos.websocket")

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    channels: str = Query("pos", description="Comma-separated channels: kds,pos,tables,session,customer:{order_id}"),
):
    """
    WebSocket endpoint for real-time events.

    Connect with channels query parameter:
    - ws://host/ws?channels=kds
    - ws://host/ws?channels=pos,tables
    - ws://host/ws?channels=customer:42
    """
    channel_list = [c.strip() for c in channels.split(",") if c.strip()]
    await ws_manager.connect(websocket, channel_list)

    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages (e.g., subscribe/unsubscribe)
            try:
                message = json.loads(data)
                action = message.get("action")
                if action == "subscribe":
                    channel = message.get("channel")
                    if channel:
                        ws_manager.subscribe(websocket, channel)
                elif action == "unsubscribe":
                    channel = message.get("channel")
                    if channel:
                        ws_manager.unsubscribe(websocket, channel)
                elif action == "ping":
                    await websocket.send_text(json.dumps({"event": "pong"}))
            except json.JSONDecodeError:
                pass  # Ignore non-JSON messages
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
