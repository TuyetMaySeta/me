# src/core/enums.py
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class ProficiencyEnum(str, Enum):
    NATIVE = "NATIVE"
    FLUENT = "FLUENT"
    INTERMEDIATE = "INTERMEDIATE"
    BASIC = "BASIC"

class SkillCategoryEnum(str, Enum):
    PROGRAMMING_LANGUAGE = "PROGRAMMING_LANGUAGE"
    DATABASE = "DATABASE"
    FRAMEWORK = "FRAMEWORK"
    TOOL = "TOOL"
    HARDWARE = "HARDWARE"

class SoftSkillEnum(str, Enum):
    COMMUNICATION = "COMMUNICATION"
    TEAMWORK = "TEAMWORK"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    DECISION_MAKING = "DECISION_MAKING"
    LEADERSHIP = "LEADERSHIP"
    TIME_MANAGEMENT = "TIME_MANAGEMENT"
    ADAPTABILITY = "ADAPTABILITY"
    OTHER = "OTHER"

class DraftStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"