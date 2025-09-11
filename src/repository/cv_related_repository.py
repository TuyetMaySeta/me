from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import re

from .base_repository import BaseRepository
from src.core.models.cv import Language, TechnicalSkill, SoftSkill, Project

logger = logging.getLogger(__name__)


class LanguageRepository(BaseRepository[Language]):
    def __init__(self, db: Session):
        super().__init__(db, Language)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        if not data.get("cv_id") or len(data["cv_id"]) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        if not data.get("language_name") or len(data["language_name"]) > 100:
            errors["language_name"] = ["Language name is required (max 100 chars)"]
        if data.get("proficiency") not in ["Native", "Fluent", "Intermediate", "Basic"]:
            errors["proficiency"] = ["Invalid proficiency value"]
        return errors

    def create_language(self, data: Dict[str, Any]) -> Language:
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)


class TechnicalSkillRepository(BaseRepository[TechnicalSkill]):
    def __init__(self, db: Session):
        super().__init__(db, TechnicalSkill)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        if not data.get("cv_id") or len(data["cv_id"]) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        if not data.get("skill_name") or len(data["skill_name"]) > 255:
            errors["skill_name"] = ["Skill name is required (max 255 chars)"]
        if data.get("category") not in [
            "Programming Language", "Database", "Framework", "Tool", "Hardware"
        ]:
            errors["category"] = ["Invalid category"]
        return errors

    def create_skill(self, data: Dict[str, Any]) -> TechnicalSkill:
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)


class SoftSkillRepository(BaseRepository[SoftSkill]):
    def __init__(self, db: Session):
        super().__init__(db, SoftSkill)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        if not data.get("cv_id") or len(data["cv_id"]) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        if data.get("skill_name") not in [
            "Communication", "Teamwork", "Problem Solving", "Decision Making",
            "Leadership", "Time Management", "Adaptability", "Other"
        ]:
            errors["skill_name"] = ["Invalid soft skill"]
        return errors

    def create_soft_skill(self, data: Dict[str, Any]) -> SoftSkill:
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        errors = {}
        if not data.get("cv_id") or len(data["cv_id"]) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        if not data.get("project_name") or len(data["project_name"]) > 255:
            errors["project_name"] = ["Project name is required (max 255 chars)"]
        return errors

    def create_project(self, data: Dict[str, Any]) -> Project:
        errors = self.validate(data)
        if errors:
            raise ValueError(errors)
        return self.create(data)
