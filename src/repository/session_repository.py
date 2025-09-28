from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.core.models.employee_session import EmployeeSession

from .base_repository import BaseRepository


class SessionRepository(BaseRepository[EmployeeSession]):
    """Repository for Employee Session management"""

    def __init__(self, db: Session):
        super().__init__(db, EmployeeSession)

    def create_session(
        self,
        session: EmployeeSession,
    ) -> EmployeeSession:
        """Create a new employee session"""
        # update old session to inactive
        self.db.query(EmployeeSession).filter(
            EmployeeSession.employee_id == session.employee_id
        ).update({"is_active": False, "revoked_at": datetime.now(timezone.utc)})
        # create new session
        self.db.add(session)
        self.db.commit()
        return session

    def get_active_session_by_id(self, session_id: int) -> Optional[EmployeeSession]:
        """Get active session by ID"""
        now = datetime.now(timezone.utc)
        session = (
            self.db.query(EmployeeSession)
            .filter(
                and_(
                    EmployeeSession.id == session_id,
                    EmployeeSession.is_active,
                    EmployeeSession.expires_at > now,
                    EmployeeSession.revoked_at.is_(None),
                )
            )
            .first()
        )

        return session

    def get_active_session(self, session_token: str) -> Optional[EmployeeSession]:
        """Get active session by token"""

        return (
            self.db.query(EmployeeSession)
            .filter(
                and_(
                    EmployeeSession.session_token == session_token,
                    EmployeeSession.is_active,
                    EmployeeSession.expires_at > datetime.now(timezone.utc),
                    EmployeeSession.revoked_at.is_(None),
                )
            )
            .first()
        )

    def revoke_session(self, session_id: int) -> bool:
        """Revoke a session"""
        # update session to inactive
        self.db.query(EmployeeSession).filter(EmployeeSession.id == session_id).update(
            {"is_active": False, "revoked_at": datetime.now(timezone.utc)}
        )
        return False

    def revoke_all_employee_sessions(self, employee_id: int) -> int:
        """Revoke all sessions for an employee"""

        now = datetime.now(timezone.utc)
        updated = (
            self.db.query(EmployeeSession)
            .filter(
                and_(
                    EmployeeSession.employee_id == employee_id,
                    EmployeeSession.is_active,
                )
            )
            .update({"is_active": False, "revoked_at": now})
        )

        self.db.commit()
        return updated

    def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions"""

        now = datetime.now(timezone.utc)

        # Soft delete expired sessions
        updated = (
            self.db.query(EmployeeSession)
            .filter(
                and_(
                    EmployeeSession.expires_at < now,
                    EmployeeSession.is_active,
                )
            )
            .update({"is_active": False, "revoked_at": now})
        )

        self.db.commit()
        return updated

    def get_employee_active_sessions(self, employee_id: int) -> List[EmployeeSession]:
        """Get all active sessions for an employee"""
        return (
            self.db.query(EmployeeSession)
            .filter(
                and_(
                    EmployeeSession.employee_id == employee_id,
                    EmployeeSession.is_active,
                    EmployeeSession.expires_at > datetime.now(timezone.utc),
                    EmployeeSession.revoked_at.is_(None),
                )
            )
            .order_by(EmployeeSession.created_at.desc())
            .all()
        )
