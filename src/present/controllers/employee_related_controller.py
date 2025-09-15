# src/present/controllers/employee_related_controller.py
import logging
from typing import List, Dict

from src.core.services.employee_related_service import EmployeeRelatedService
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

logger = logging.getLogger(__name__)


class EmployeeRelatedController:
    """Controller for Employee related entities (individual table operations)"""
    
    def __init__(self, employee_related_service: EmployeeRelatedService):
        self.employee_related_service = employee_related_service

    # ===================== CONTACT OPERATIONS =====================
    
    def create_contact(self, employee_id: int, request: EmployeeContactCreate) -> EmployeeContactResponse:
        """Create a new contact"""
        logger.info(f"Controller: Creating contact {request.name} for Employee {employee_id}")
        
        try:
            contact = self.employee_related_service.create_contact(employee_id, request)
            logger.info(f"Controller: Contact created successfully - {contact.name} (ID: {contact.id})")
            return contact
        except Exception as e:
            logger.error(f"Controller: Contact creation failed: {str(e)}")
            raise

    def get_contact(self, contact_id: int) -> EmployeeContactResponse:
        """Get contact by ID"""
        logger.info(f"Controller: Getting contact {contact_id}")
        
        try:
            contact = self.employee_related_service.get_contact(contact_id)
            logger.info(f"Controller: Retrieved contact {contact_id}")
            return contact
        except Exception as e:
            logger.error(f"Controller: Failed to get contact {contact_id}: {str(e)}")
            raise

    def get_contacts_by_employee(self, employee_id: int) -> List[EmployeeContactResponse]:
        """Get all contacts for an Employee"""
        logger.info(f"Controller: Getting contacts for Employee {employee_id}")
        
        try:
            contacts = self.employee_related_service.get_contacts_by_employee(employee_id)
            logger.info(f"Controller: Retrieved {len(contacts)} contacts for Employee {employee_id}")
            return contacts
        except Exception as e:
            logger.error(f"Controller: Failed to get contacts for Employee {employee_id}: {str(e)}")
            raise

    def update_contact(self, contact_id: int, request: EmployeeContactUpdate) -> EmployeeContactResponse:
        """Update contact"""
        logger.info(f"Controller: Updating contact {contact_id}")
        
        try:
            contact = self.employee_related_service.update_contact(contact_id, request)
            logger.info(f"Controller: Contact updated successfully {contact_id}")
            return contact
        except Exception as e:
            logger.error(f"Controller: Failed to update contact {contact_id}: {str(e)}")
            raise

    def delete_contact(self, contact_id: int) -> Dict[str, str]:
        """Delete contact"""
        logger.info(f"Controller: Deleting contact {contact_id}")
        
        try:
            self.employee_related_service.delete_contact(contact_id)
            logger.info(f"Controller: Contact deleted successfully {contact_id}")
            return {"message": f"Contact {contact_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete contact {contact_id}: {str(e)}")
            raise

    # ===================== DOCUMENT OPERATIONS =====================
    
    def create_document(self, employee_id: int, request: EmployeeDocumentCreate) -> EmployeeDocumentResponse:
        """Create a new document"""
        logger.info(f"Controller: Creating document for Employee {employee_id}")
        
        try:
            document = self.employee_related_service.create_document(employee_id, request)
            logger.info(f"Controller: Document created successfully for Employee {employee_id} (ID: {document.id})")
            return document
        except Exception as e:
            logger.error(f"Controller: Document creation failed: {str(e)}")
            raise

    def get_document(self, document_id: int) -> EmployeeDocumentResponse:
        """Get document by ID"""
        logger.info(f"Controller: Getting document {document_id}")
        
        try:
            document = self.employee_related_service.get_document(document_id)
            logger.info(f"Controller: Retrieved document {document_id}")
            return document
        except Exception as e:
            logger.error(f"Controller: Failed to get document {document_id}: {str(e)}")
            raise

    def get_documents_by_employee(self, employee_id: int) -> List[EmployeeDocumentResponse]:
        """Get all documents for an Employee"""
        logger.info(f"Controller: Getting documents for Employee {employee_id}")
        
        try:
            documents = self.employee_related_service.get_documents_by_employee(employee_id)
            logger.info(f"Controller: Retrieved {len(documents)} documents for Employee {employee_id}")
            return documents
        except Exception as e:
            logger.error(f"Controller: Failed to get documents for Employee {employee_id}: {str(e)}")
            raise

    def update_document(self, document_id: int, request: EmployeeDocumentUpdate) -> EmployeeDocumentResponse:
        """Update document"""
        logger.info(f"Controller: Updating document {document_id}")
        
        try:
            document = self.employee_related_service.update_document(document_id, request)
            logger.info(f"Controller: Document updated successfully {document_id}")
            return document
        except Exception as e:
            logger.error(f"Controller: Failed to update document {document_id}: {str(e)}")
            raise

    def delete_document(self, document_id: int) -> Dict[str, str]:
        """Delete document"""
        logger.info(f"Controller: Deleting document {document_id}")
        
        try:
            self.employee_related_service.delete_document(document_id)
            logger.info(f"Controller: Document deleted successfully {document_id}")
            return {"message": f"Document {document_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete document {document_id}: {str(e)}")
            raise

    # ===================== EDUCATION OPERATIONS =====================
    
    def create_education(self, employee_id: int, request: EmployeeEducationCreate) -> EmployeeEducationResponse:
        """Create a new education record"""
        logger.info(f"Controller: Creating education {request.school_name} for Employee {employee_id}")
        
        try:
            education = self.employee_related_service.create_education(employee_id, request)
            logger.info(f"Controller: Education created successfully - {education.school_name} (ID: {education.id})")
            return education
        except Exception as e:
            logger.error(f"Controller: Education creation failed: {str(e)}")
            raise

    def get_education(self, education_id: int) -> EmployeeEducationResponse:
        """Get education by ID"""
        logger.info(f"Controller: Getting education {education_id}")
        
        try:
            education = self.employee_related_service.get_education(education_id)
            logger.info(f"Controller: Retrieved education {education_id}")
            return education
        except Exception as e:
            logger.error(f"Controller: Failed to get education {education_id}: {str(e)}")
            raise

    def get_education_by_employee(self, employee_id: int) -> List[EmployeeEducationResponse]:
        """Get all education records for an Employee"""
        logger.info(f"Controller: Getting education for Employee {employee_id}")
        
        try:
            education_records = self.employee_related_service.get_education_by_employee(employee_id)
            logger.info(f"Controller: Retrieved {len(education_records)} education records for Employee {employee_id}")
            return education_records
        except Exception as e:
            logger.error(f"Controller: Failed to get education for Employee {employee_id}: {str(e)}")
            raise

    def update_education(self, education_id: int, request: EmployeeEducationUpdate) -> EmployeeEducationResponse:
        """Update education"""
        logger.info(f"Controller: Updating education {education_id}")
        
        try:
            education = self.employee_related_service.update_education(education_id, request)
            logger.info(f"Controller: Education updated successfully {education_id}")
            return education
        except Exception as e:
            logger.error(f"Controller: Failed to update education {education_id}: {str(e)}")
            raise

    def delete_education(self, education_id: int) -> Dict[str, str]:
        """Delete education"""
        logger.info(f"Controller: Deleting education {education_id}")
        
        try:
            self.employee_related_service.delete_education(education_id)
            logger.info(f"Controller: Education deleted successfully {education_id}")
            return {"message": f"Education {education_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete education {education_id}: {str(e)}")
            raise

    # ===================== LANGUAGE OPERATIONS =====================
    
    def create_language(self, employee_id: int, request: EmployeeLanguageCreate) -> EmployeeLanguageResponse:
        """Create a new language"""
        logger.info(f"Controller: Creating language {request.language_name} for Employee {employee_id}")
        
        try:
            language = self.employee_related_service.create_language(employee_id, request)
            logger.info(f"Controller: Language created successfully - {language.language_name} (ID: {language.id})")
            return language
        except Exception as e:
            logger.error(f"Controller: Language creation failed: {str(e)}")
            raise

    def get_language(self, language_id: int) -> EmployeeLanguageResponse:
        """Get language by ID"""
        logger.info(f"Controller: Getting language {language_id}")
        
        try:
            language = self.employee_related_service.get_language(language_id)
            logger.info(f"Controller: Retrieved language {language_id}")
            return language
        except Exception as e:
            logger.error(f"Controller: Failed to get language {language_id}: {str(e)}")
            raise

    def get_languages_by_employee(self, employee_id: int) -> List[EmployeeLanguageResponse]:
        """Get all languages for an Employee"""
        logger.info(f"Controller: Getting languages for Employee {employee_id}")
        
        try:
            languages = self.employee_related_service.get_languages_by_employee(employee_id)
            logger.info(f"Controller: Retrieved {len(languages)} languages for Employee {employee_id}")
            return languages
        except Exception as e:
            logger.error(f"Controller: Failed to get languages for Employee {employee_id}: {str(e)}")
            raise

    def update_language(self, language_id: int, request: EmployeeLanguageUpdate) -> EmployeeLanguageResponse:
        """Update language"""
        logger.info(f"Controller: Updating language {language_id}")
        
        try:
            language = self.employee_related_service.update_language(language_id, request)
            logger.info(f"Controller: Language updated successfully {language_id}")
            return language
        except Exception as e:
            logger.error(f"Controller: Failed to update language {language_id}: {str(e)}")
            raise

    def delete_language(self, language_id: int) -> Dict[str, str]:
        """Delete language"""
        logger.info(f"Controller: Deleting language {language_id}")
        
        try:
            self.employee_related_service.delete_language(language_id)
            logger.info(f"Controller: Language deleted successfully {language_id}")
            return {"message": f"Language {language_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete language {language_id}: {str(e)}")
            raise

    # ===================== TECHNICAL SKILL OPERATIONS =====================
    
    def create_technical_skill(self, employee_id: int, request: EmployeeTechnicalSkillCreate) -> EmployeeTechnicalSkillResponse:
        """Create a new technical skill"""
        logger.info(f"Controller: Creating technical skill {request.skill_name} for Employee {employee_id}")
        
        try:
            skill = self.employee_related_service.create_technical_skill(employee_id, request)
            logger.info(f"Controller: Technical skill created successfully - {skill.skill_name} (ID: {skill.id})")
            return skill
        except Exception as e:
            logger.error(f"Controller: Technical skill creation failed: {str(e)}")
            raise

    def get_technical_skill(self, skill_id: int) -> EmployeeTechnicalSkillResponse:
        """Get technical skill by ID"""
        logger.info(f"Controller: Getting technical skill {skill_id}")
        
        try:
            skill = self.employee_related_service.get_technical_skill(skill_id)
            logger.info(f"Controller: Retrieved technical skill {skill_id}")
            return skill
        except Exception as e:
            logger.error(f"Controller: Failed to get technical skill {skill_id}:{str(e)}")
            raise
