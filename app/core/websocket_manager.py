"""
WebSocket connection manager for real-time events.
"""

import json
import logging
from enum import Enum
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("cafepos.websocket")


class WSEventType(str, Enum):
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_SENT_TO_KITCHEN = "ORDER_SENT_TO_KITCHEN"
    ORDER_PREPARING = "ORDER_PREPARING"
    ORDER_COMPLETED = "ORDER_COMPLETED"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    CUSTOMER_DISPLAY_UPDATE = "CUSTOMER_DISPLAY_UPDATE"
    KDS_UPDATE = "KDS_UPDATE"
    TABLE_STATUS_UPDATE = "TABLE_STATUS_UPDATE"
    SESSION_OPENED = "SESSION_OPENED"
    SESSION_CLOSED = "SESSION_CLOSED"
    RESERVATION_CREATED = "RESERVATION_CREATED"
    RESERVATION_UPDATED = "RESERVATION_UPDATED"
    SYNC_REQUIRED = "SYNC_REQUIRED"


class ConnectionManager:
    """
    Manages WebSocket connections with channel-based subscriptions.

    Channels:
      - "kds"              : Kitchen Display System updates
      - "pos"              : POS terminal updates
      - "customer:{order_id}" : Customer display for a specific order
      - "tables"           : Table status updates
      - "session"          : Session lifecycle events
    """

    def __init__(self):
        # channel -> set of websockets
        self._channels: dict[str, set[WebSocket]] = {}
        # websocket -> set of channels
        self._subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket, channels: list[str] | None = None):
        """Accept a WebSocket connection and subscribe to channels."""
        await websocket.accept()
        self._subscriptions[websocket] = set()
        if channels:
            for channel in channels:
                self.subscribe(websocket, channel)
        logger.info(f"WebSocket connected. Channels: {channels}")

    def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe a websocket to a channel."""
        if channel not in self._channels:
            self._channels[channel] = set()
        self._channels[channel].add(websocket)
        if websocket not in self._subscriptions:
            self._subscriptions[websocket] = set()
        self._subscriptions[websocket].add(channel)

    def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe a websocket from a channel."""
        if channel in self._channels:
            self._channels[channel].discard(websocket)
            if not self._channels[channel]:
                del self._channels[channel]
        if websocket in self._subscriptions:
            self._subscriptions[websocket].discard(channel)

    def disconnect(self, websocket: WebSocket):
        """Remove a websocket from all channels."""
        channels = self._subscriptions.pop(websocket, set())
        for channel in channels:
            if channel in self._channels:
                self._channels[channel].discard(websocket)
                if not self._channels[channel]:
                    del self._channels[channel]
        logger.info("WebSocket disconnected")

    async def broadcast_to_channel(
        self, channel: str, event_type: WSEventType | str, data: dict[str, Any]
    ):
        """Send an event to all subscribers of a channel."""
        message = json.dumps({
            "event": event_type.value if hasattr(event_type, "value") else str(event_type),
            "data": data,
        })
        if channel not in self._channels:
            return

        disconnected = set()
        for websocket in self._channels[channel]:
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.add(websocket)

        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_all(self, event_type: WSEventType, data: dict[str, Any]):
        """Send an event to ALL connected websockets."""
        message = json.dumps({
            "event": event_type.value,
            "data": data,
        })
        disconnected = set()
        for websocket in list(self._subscriptions.keys()):
            try:
                await websocket.send_text(message)
            except Exception:
                disconnected.add(websocket)
        for ws in disconnected:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, event_type: WSEventType, data: dict[str, Any]):
        """Send an event to a specific websocket."""
        message = json.dumps({
            "event": event_type.value,
            "data": data,
        })
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    @property
    def active_connections(self) -> int:
        return len(self._subscriptions)


# Singleton instance
ws_manager = ConnectionManager()
