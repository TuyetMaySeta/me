import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.core.enums import SessionProviderEnum
from src.core.models.employee_session import EmployeeSession

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class SessionRepository(BaseRepository[EmployeeSession]):
    """Repository for Employee Session management"""

    def __init__(self, db: Session):
        super().__init__(db, EmployeeSession)

    def create_session(
        self,
        employee_id: int,
        session_token: str,
        expires_at: datetime,
        provider: SessionProviderEnum = SessionProviderEnum.LOCAL,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> EmployeeSession:
        """Create a new employee session"""
        try:
            session_data = {
                "employee_id": employee_id,
                "session_token": session_token,
                "provider": provider,
                "device_info": device_info,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "expires_at": expires_at,
                "is_active": True,
            }

            session = EmployeeSession(**session_data)
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            logger.info(f"Created session for employee {employee_id}")
            return session

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create session: {str(e)}")
            raise

    def get_active_session(self, session_token: str) -> Optional[EmployeeSession]:
        """Get active session by token"""
        try:
            now = datetime.now(timezone.utc)
            session = (
                self.db.query(EmployeeSession)
                .filter(
                    and_(
                        EmployeeSession.session_token == session_token,
                        EmployeeSession.is_active == True,
                        EmployeeSession.expires_at > now,
                        EmployeeSession.revoked_at.is_(None),
                    )
                )
                .first()
            )

            return session

        except SQLAlchemyError as e:
            logger.error(f"Error getting session: {str(e)}")
            raise

    def revoke_session(self, session_token: str) -> bool:
        """Revoke a session"""
        try:
            session = (
                self.db.query(EmployeeSession)
                .filter(EmployeeSession.session_token == session_token)
                .first()
            )

            if session:
                session.is_active = False
                session.revoked_at = datetime.now(timezone.utc)
                self.db.commit()
                logger.info(f"Revoked session: {session_token}")
                return True

            return False

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error revoking session: {str(e)}")
            raise

    def revoke_all_employee_sessions(self, employee_id: int) -> int:
        """Revoke all sessions for an employee"""
        try:
            now = datetime.now(timezone.utc)
            updated = (
                self.db.query(EmployeeSession)
                .filter(
                    and_(
                        EmployeeSession.employee_id == employee_id,
                        EmployeeSession.is_active == True,
                    )
                )
                .update({"is_active": False, "revoked_at": now})
            )

            self.db.commit()
            logger.info(f"Revoked {updated} sessions for employee {employee_id}")
            return updated

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error revoking employee sessions: {str(e)}")
            raise

    def cleanup_expired_sessions(self) -> int:
        """Cleanup expired sessions"""
        try:
            now = datetime.now(timezone.utc)

            # Soft delete expired sessions
            updated = (
                self.db.query(EmployeeSession)
                .filter(
                    and_(
                        EmployeeSession.expires_at < now,
                        EmployeeSession.is_active == True,
                    )
                )
                .update({"is_active": False, "revoked_at": now})
            )

            self.db.commit()
            logger.info(f"Cleaned up {updated} expired sessions")
            return updated

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error cleaning up sessions: {str(e)}")
            raise

    def get_employee_active_sessions(self, employee_id: int) -> List[EmployeeSession]:
        """Get all active sessions for an employee"""
        try:
            now = datetime.now(timezone.utc)
            sessions = (
                self.db.query(EmployeeSession)
                .filter(
                    and_(
                        EmployeeSession.employee_id == employee_id,
                        EmployeeSession.is_active == True,
                        EmployeeSession.expires_at > now,
                        EmployeeSession.revoked_at.is_(None),
                    )
                )
                .order_by(EmployeeSession.created_at.desc())
                .all()
            )

            return sessions

        except SQLAlchemyError as e:
            logger.error(f"Error getting employee sessions: {str(e)}")
            raise
