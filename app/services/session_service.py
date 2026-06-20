"""
POS Session service — open/close session lifecycle.
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, SessionNotOpenException
from app.core.websocket_manager import WSEventType, ws_manager
from app.models.pos_session import SessionStatus
from app.models.order import Order, OrderStatus
from app.repositories.session_repository import SessionRepository
from app.schemas.order import CloseSessionRequest, OpenSessionRequest, SessionResponse


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SessionRepository(db)

    async def open_session(self, user_id: int, data: OpenSessionRequest) -> SessionResponse:
        """Open a new POS session. Only one session can be open at a time."""
        existing = await self.repo.get_open_session()
        if existing:
            raise BadRequestException(
                "A POS session is already open. Close it before opening a new one."
            )

        session = await self.repo.create({
            "opened_by": user_id,
            "opening_balance": data.opening_balance,
            "status": SessionStatus.OPEN,
        })

        # Broadcast
        await ws_manager.broadcast_to_channel("session", WSEventType.SESSION_OPENED, {
            "session_id": session.id,
            "opened_by": user_id,
        })

        return self._to_response(session)

    async def close_session(self, data: CloseSessionRequest) -> SessionResponse:
        """Close an active POS session."""
        session = await self.repo.get_by_id(data.session_id)
        if not session:
            raise NotFoundException("Session", data.session_id)
        if session.status == SessionStatus.CLOSED:
            raise BadRequestException("Session is already closed")

        # Check for active orders
        result = await self.db.execute(
            select(Order).where(
                Order.session_id == data.session_id,
                Order.status.in_([OrderStatus.DRAFT, OrderStatus.SENT_TO_KITCHEN, OrderStatus.PREPARING, OrderStatus.READY])
            )
        )
        active_orders = result.scalars().all()
        if active_orders:
            raise BadRequestException("Cannot close session with active orders")

        session.status = SessionStatus.CLOSED
        session.closing_balance = data.closing_balance
        session.closed_at = datetime.now(timezone.utc)
        await self.db.flush()
        await self.db.refresh(session)

        # Broadcast
        await ws_manager.broadcast_to_channel("session", WSEventType.SESSION_CLOSED, {
            "session_id": session.id,
        })

        return self._to_response(session)

    async def get_current_session(self) -> SessionResponse:
        """Get the currently open session."""
        session = await self.repo.get_open_session()
        if not session:
            raise SessionNotOpenException()
        return self._to_response(session)

    async def get_all_sessions(self) -> list[SessionResponse]:
        sessions = await self.repo.get_sessions()
        return [self._to_response(s) for s in sessions]

    def _to_response(self, session) -> SessionResponse:
        return SessionResponse(
            id=session.id,
            opened_by=session.opened_by,
            opened_by_name=session.opened_by_user.name if session.opened_by_user else None,
            opened_at=session.opened_at,
            closed_at=session.closed_at,
            opening_balance=float(session.opening_balance),
            closing_balance=float(session.closing_balance) if session.closing_balance else None,
            status=session.status.value,
        )
