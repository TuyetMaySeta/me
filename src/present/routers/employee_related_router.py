# src/present/routers/employee_related_router.py
from fastapi import APIRouter, Depends, status, Path
from typing import List, Dict

from src.present.request.employee import (
    EmployeeContactCreate, EmployeeContactUpdate, EmployeeContactResponse,
    EmployeeDocumentCreate, EmployeeDocumentUpdate, EmployeeDocumentResponse,
    EmployeeEducationCreate, EmployeeEducationUpdate, EmployeeEducationResponse,
    EmployeeCertificationCreate, EmployeeCertificationUpdate, EmployeeCertificationResponse,
    EmployeeProfileCreate, EmployeeProfileUpdate, EmployeeProfileResponse,
    EmployeeLanguageCreate, EmployeeLanguageUpdate, EmployeeLanguageResponse,
    EmployeeTechnicalSkillCreate, EmployeeTechnicalSkillUpdate, EmployeeTechnicalSkillResponse,
    EmployeeProjectCreate, EmployeeProjectUpdate, EmployeeProjectResponse,
    EmployeeChildCreate, EmployeeChildUpdate, EmployeeChildResponse
)
from src.present.controllers.employee_related_controller import EmployeeRelatedController
from src.bootstrap.dependencies import get_employee_related_controller

router = APIRouter(prefix="/employee-components", tags=["Employee Components"])


# ===================== CONTACT ENDPOINTS =====================

@router.post("/contacts/employee/{employee_id}", response_model=EmployeeContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    request: EmployeeContactCreate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new contact for an Employee
    
    - **employee_id**: Employee ID (must exist)
    - **name**: Contact person's name
    - **relation**: Relationship to employee (e.g., Emergency Contact, Spouse, etc.)
    - **phone**: Contact phone number
    """
    return controller.create_contact(employee_id, request)


@router.get("/contacts/{contact_id}", response_model=EmployeeContactResponse)
def get_contact(
    contact_id: int = Path(..., description="Contact ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get contact by ID"""
    return controller.get_contact(contact_id)


@router.get("/contacts/employee/{employee_id}", response_model=List[EmployeeContactResponse])
def get_contacts_by_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all contacts for an Employee"""
    return controller.get_contacts_by_employee(employee_id)


@router.put("/contacts/{contact_id}", response_model=EmployeeContactResponse)
def update_contact(
    contact_id: int = Path(..., description="Contact ID", gt=0),
    request: EmployeeContactUpdate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Update contact by ID"""
    return controller.update_contact(contact_id, request)


@router.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int = Path(..., description="Contact ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete contact by ID"""
    return controller.delete_contact(contact_id)


# ===================== DOCUMENT ENDPOINTS =====================

@router.post("/documents/employee/{employee_id}", response_model=EmployeeDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    request: EmployeeDocumentCreate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new document record for an Employee
    
    - **employee_id**: Employee ID (must exist)
    - **identity_number**: Identity card number
    - **tax_id_number**: Tax identification number
    - **social_insurance_number**: Social insurance number
    - **bank_name**: Bank name for salary
    - **account_bank_number**: Bank account number
    - **motorbike_plate**: Motorbike license plate (if applicable)
    """
    return controller.create_document(employee_id, request)


@router.get("/documents/{document_id}", response_model=EmployeeDocumentResponse)
def get_document(
    document_id: int = Path(..., description="Document ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get document by ID"""
    return controller.get_document(document_id)


@router.get("/documents/employee/{employee_id}", response_model=List[EmployeeDocumentResponse])
def get_documents_by_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all documents for an Employee"""
    return controller.get_documents_by_employee(employee_id)


@router.put("/documents/{document_id}", response_model=EmployeeDocumentResponse)
def update_document(
    document_id: int = Path(..., description="Document ID", gt=0),
    request: EmployeeDocumentUpdate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Update document by ID"""
    return controller.update_document(document_id, request)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int = Path(..., description="Document ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete document by ID"""
    return controller.delete_document(document_id)


# ===================== EDUCATION ENDPOINTS =====================

@router.post("/education/employee/{employee_id}", response_model=EmployeeEducationResponse, status_code=status.HTTP_201_CREATED)
def create_education(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    request: EmployeeEducationCreate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new education record for an Employee
    
    - **employee_id**: Employee ID (must exist)
    - **school_name**: Name of the school/university
    - **graduation_year**: Year of graduation
    - **degree**: Degree obtained (e.g., Bachelor, Master, PhD)
    - **major**: Field of study/major
    """
    return controller.create_education(employee_id, request)


@router.get("/education/{education_id}", response_model=EmployeeEducationResponse)
def get_education(
    education_id: int = Path(..., description="Education ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get education by ID"""
    return controller.get_education(education_id)


@router.get("/education/employee/{employee_id}", response_model=List[EmployeeEducationResponse])
def get_education_by_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all education records for an Employee"""
    return controller.get_education_by_employee(employee_id)


@router.put("/education/{education_id}", response_model=EmployeeEducationResponse)
def update_education(
    education_id: int = Path(..., description="Education ID", gt=0),
    request: EmployeeEducationUpdate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Update education by ID"""
    return controller.update_education(education_id, request)


@router.delete("/education/{education_id}")
def delete_education(
    education_id: int = Path(..., description="Education ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete education by ID"""
    return controller.delete_education(education_id)


# ===================== LANGUAGE ENDPOINTS =====================

@router.post("/languages/employee/{employee_id}", response_model=EmployeeLanguageResponse, status_code=status.HTTP_201_CREATED)
def create_language(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    request: EmployeeLanguageCreate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new language for an Employee
    
    - **employee_id**: Employee ID (must exist)
    - **language_name**: Name of the language
    - **proficiency**: Language proficiency level (Native/Fluent/Intermediate/Basic)
    - **description**: Optional description of language skills
    """
    return controller.create_language(employee_id, request)


@router.get("/languages/{language_id}", response_model=EmployeeLanguageResponse)
def get_language(
    language_id: int = Path(..., description="Language ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get language by ID"""
    return controller.get_language(language_id)


@router.get("/languages/employee/{employee_id}", response_model=List[EmployeeLanguageResponse])
def get_languages_by_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all languages for an Employee"""
    return controller.get_languages_by_employee(employee_id)


@router.put("/languages/{language_id}", response_model=EmployeeLanguageResponse)
def update_language(
    language_id: int = Path(..., description="Language ID", gt=0),
    request: EmployeeLanguageUpdate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Update language by ID"""
    return controller.update_language(language_id, request)


@router.delete("/languages/{language_id}")
def delete_language(
    language_id: int = Path(..., description="Language ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete language by ID"""
    return controller.delete_language(language_id)


# ===================== TECHNICAL SKILL ENDPOINTS =====================

@router.post("/technical-skills/employee/{employee_id}", response_model=EmployeeTechnicalSkillResponse, status_code=status.HTTP_201_CREATED)
def create_technical_skill(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    request: EmployeeTechnicalSkillCreate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new technical skill for an Employee
    
    - **employee_id**: Employee ID (must exist)
    - **category**: Skill category (Programming Language/Database/Framework/Tool/Hardware)
    - **skill_name**: Name of the skill
    - **description**: Optional description of skill level/experience
    """
    return controller.create_technical_skill(employee_id, request)


@router.get("/technical-skills/{skill_id}", response_model=EmployeeTechnicalSkillResponse)
def get_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get technical skill by ID"""
    return controller.get_technical_skill(skill_id)


@router.get("/technical-skills/employee/{employee_id}", response_model=List[EmployeeTechnicalSkillResponse])
def get_technical_skills_by_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all technical skills for an Employee"""
    return controller.get_technical_skills_by_employee(employee_id)


@router.put("/technical-skills/{skill_id}", response_model=EmployeeTechnicalSkillResponse)
def update_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    request: EmployeeTechnicalSkillUpdate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Update technical skill by ID"""
    return controller.update_technical_skill(skill_id, request)


@router.delete("/technical-skills/{skill_id}")
def delete_technical_skill(
    skill_id: int = Path(..., description="Technical Skill ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete technical skill by ID"""
    return controller.delete_technical_skill(skill_id)


# ===================== PROJECT ENDPOINTS =====================

@router.post("/projects/employee/{employee_id}", response_model=EmployeeProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    request: EmployeeProjectCreate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Create a new project for an Employee
    
    - **employee_id**: Employee ID (must exist)
    - **project_name**: Name of the project
    - **project_description**: Description of the project
    - **position**: Employee's position in the project
    - **responsibilities**: Employee's responsibilities
    - **programming_languages**: Programming languages used
    """
    return controller.create_project(employee_id, request)


@router.get("/projects/{project_id}", response_model=EmployeeProjectResponse)
def get_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get project by ID"""
    return controller.get_project(project_id)


@router.get("/projects/employee/{employee_id}", response_model=List[EmployeeProjectResponse])
def get_projects_by_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Get all projects for an Employee"""
    return controller.get_projects_by_employee(employee_id)


@router.put("/projects/{project_id}", response_model=EmployeeProjectResponse)
def update_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    request: EmployeeProjectUpdate = ...,
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Update project by ID"""
    return controller.update_project(project_id, request)


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int = Path(..., description="Project ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """Delete project by ID"""
    return controller.delete_project(project_id)


# ===================== UTILITY ENDPOINTS =====================

@router.get("/employee/{employee_id}/summary")
def get_employee_component_summary(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeRelatedController = Depends(get_employee_related_controller)
):
    """
    Get component summary for an Employee
    
    Returns count of each component type for the employee
    """
    contacts = controller.get_contacts_by_employee(employee_id)
    documents = controller.get_documents_by_employee(employee_id)
    education = controller.get_education_by_employee(employee_id)
    languages = controller.get_languages_by_employee(employee_id)
    technical_skills = controller.get_technical_skills_by_employee(employee_id)
    projects = controller.get_projects_by_employee(employee_id)
    
    return {
        "employee_id": employee_id,
        "component_counts": {
            "contacts": len(contacts),
            "documents": len(documents),
            "education": len(education),
            "languages": len(languages),
            "technical_skills": len(technical_skills),
            "projects": len(projects),
            "total_components": (
                len(contacts) + len(documents) + len(education) + 
                len(languages) + len(technical_skills) + len(projects)
            )
        },
        "has_components": {
            "has_contacts": len(contacts) > 0,
            "has_documents": len(documents) > 0,
            "has_education": len(education) > 0,
            "has_languages": len(languages) > 0,
            "has_technical_skills": len(technical_skills) > 0,
            "has_projects": len(projects) > 0
        }
    }
