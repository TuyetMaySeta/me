import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from src.core.enums.verification import VerificationTypeEnum
from src.core.models.verification_code import VerificationCode
from src.repository.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class VerificationRepository(BaseRepository[VerificationCode]):
    def __init__(self, db: Session):
        super().__init__(db, VerificationCode)

    def create_verification(self, verification: VerificationCode) -> VerificationCode:
        self.db.add(verification)
        self.db.commit()
        self.db.refresh(verification)
        return verification

    def get_active_otp(
        self, employee_id: int, verification_type: VerificationTypeEnum
    ) -> Optional[VerificationCode]:
        """Check if there's an active OTP of employee_id"""
        now = datetime.now(timezone.utc)
        return (
            self.db.query(VerificationCode)
            .filter(
                VerificationCode.employee_id == employee_id,
                VerificationCode.type == verification_type,
                VerificationCode.expires_at > now,
            )
            .first()
        )

    def get_valid_otp(
        self, employee_id: int, code: str, verification_type: VerificationTypeEnum
    ) -> Optional[VerificationCode]:
        """Get valid OTP"""
        now = datetime.now(timezone.utc)
        return (
            self.db.query(VerificationCode)
            .filter(
                VerificationCode.employee_id == employee_id,
                VerificationCode.code == code,
                VerificationCode.type == verification_type,
                VerificationCode.expires_at > now,
            )
            .first()
        )

    def mark_as_used(self, verification_id: int) -> None:
        """Mark OTP as used by setting expiration to now"""
        verification = (
            self.db.query(VerificationCode)
            .filter(VerificationCode.id == verification_id)
            .first()
        )

        if verification:
            verification.expires_at = datetime.now(timezone.utc)
            self.db.commit()  
