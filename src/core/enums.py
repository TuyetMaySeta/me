# src/core/enums.py
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class ProficiencyEnum(str, Enum):
    NATIVE = "Native"
    FLUENT = "Fluent"
    INTERMEDIATE = "Intermediate"
    BASIC = "Basic"

class SkillCategoryEnum(str, Enum):
    PROGRAMMING_LANGUAGE = "Programming Language"
    DATABASE = "Database"
    FRAMEWORK = "Framework"
    TOOL = "Tool"
    HARDWARE = "Hardware"

class SoftSkillEnum(str, Enum):
    COMMUNICATION = "Communication"
    TEAMWORK = "Teamwork"
    PROBLEM_SOLVING = "Problem Solving"
    DECISION_MAKING = "Decision Making"
    LEADERSHIP = "Leadership"
    TIME_MANAGEMENT = "Time Management"
    ADAPTABILITY = "Adaptability"
    OTHER = "Other"

class MaritalStatusEnum(str, Enum):
    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"

class EmployeeStatusEnum(str, Enum):
    ACTIVE = "Active"
    ON_LEAVE = "On Leave"
    RESIGNED = "Resigned"

class DraftStatusEnum(str, Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    REJECTED = "Rejected"
