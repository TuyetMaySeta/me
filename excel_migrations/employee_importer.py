import pandas as pd
from typing import Dict, Any, List,Tuple
import logging
from sqlalchemy.orm import Session
from datetime import datetime
from src.core.models.employee import Employee
from src.core.models.employee_related import (
    EmployeeProfile, 
    EmployeeTechnicalSkill,
    EmployeeChild, 
    EmployeeEducation,
    EmployeeContact,
    EmployeeDocument
)
import asyncio
from src.core.models.employee_related import EmployeeProfile, EmployeeTechnicalSkill,EmployeeChild, EmployeeEducation,EmployeeContact,EmployeeDocument
from src.utils.password_utils import hash_password, generate_random_password
from src.core.services.verification_service import MailService

from .data_mapper import ExcelDataMapper

logger = logging.getLogger(__name__)

class EmployeeImporter:
    def __init__(self, session: Session, mail_service: MailService):
        self.session = session
        self.mail_service = mail_service
        self.success_count = 0
        self.error_count = 0
        self.errors: List[str] = []

    def import_from_excel(self, file_path: str) -> Dict[str, Any]:
        logger.info(f"Bắt đầu import từ: {file_path}")
        try:
            df = pd.read_excel(file_path)
            self.success_count = self.error_count = 0
            self.errors.clear()

            for idx, row in df.iterrows():
                try:
                    employee,temp_password = self._create_employee(row)
                    self._create_employee_profile(employee, row)
                    self._create_employee_technical_skill(employee,row)
                    self._create_employee_education(employee,row)
                    self._create_employee_contacts(employee,row)
                    self._create_employee_children(employee,row)
                    self._create_employee_documents(employee, row)
                    # Send email with temporary password
                    try:
                        asyncio.run(self.mail_service.send_temporary_password_email(
                            recipient_email=employee.email,
                            temporary_password=temp_password,
                            full_name=employee.full_name
                        )
                        )
                        logger.info(f" Email send to {employee.email}")
                        self.session.commit()
                        self.success_count += 1
                    except Exception as email_error:
                        self.session.rollback()
                        error_msg = f"Failed to send email to {employee.email}: {email_error}"
                        self.errors.append(f"Row {idx+1}: {error_msg}")
                        logger.error(f" Row {idx+1}: {error_msg}")
                        self.error_count += 1
                        
                except Exception as e:
                    self.session.rollback()
                    self.error_count += 1
                    self.errors.append(f"Dòng {idx+1}: {e}")
                    logger.error(f" Dòng {idx+1}: {e}")
            return {
                "success": True,
                "total_rows": len(df),
                "success_count": self.success_count,
                "error_count": self.error_count,
                "errors": self.errors,
            }

        except Exception as e:
            self.session.rollback()
            logger.error(f"Import thất bại: {e}")
            return {"success": False, "error": str(e)}


    def _create_employee(self, row: pd.Series) -> tuple[Employee, str]:
        employee_data = ExcelDataMapper.map_employee_data(row)

        if employee_data.get('id'):
            existing = (
                self.session.query(Employee)
                .filter_by(id=employee_data['id'])
                .first()
            )
            if existing:
                raise ValueError(f"ID {employee_data['id']} đã tồn tại")
        
        employee = Employee(**employee_data)
        # generate and hash password
        temporary_password = generate_random_password()
        employee.hashed_password = hash_password(temporary_password)
        self.session.add(employee)
        self.session.flush()

        # Todo: Send email to employee with password
        return employee , temporary_password


    def _create_employee_profile(self, employee: Employee, row: pd.Series):
        profile_data = ExcelDataMapper.map_employee_profile_data(row)
        self.session.add(EmployeeProfile(employee_id=employee.id, **profile_data))
    
    def _create_employee_technical_skill(self, employee: Employee, row: pd.Series):
        skills_data = ExcelDataMapper.map_employee_all_technical_skills(row)
    
        for skill_data in skills_data:  
            skill = EmployeeTechnicalSkill(  #
                employee_id=employee.id,
                **skill_data
            )
            self.session.add(skill)
    def _create_employee_education(self, employee: Employee, row: pd.Series):
        educations_data = ExcelDataMapper.map_employee_education(row)  # Now returns List
    
        for education_data in educations_data:
            education = EmployeeEducation(employee_id=employee.id, **education_data)
            self.session.add(education)
    def _create_employee_contacts(self, employee: Employee, row: pd.Series):
        contacts_data = ExcelDataMapper.map_employee_contacts(row) 
        
        for contact_data in contacts_data:
            contact = EmployeeContact(
                employee_id=employee.id,
                **contact_data
            )
            self.session.add(contact)
    
    def _create_employee_children(self, employee: Employee, row: pd.Series):
        children_data = ExcelDataMapper.map_employee_children(row)
        for child_data in children_data:
            child = EmployeeChild(employee_id=employee.id, **child_data)
            self.session.add(child)

    def _create_employee_documents(self, employee: Employee, row: pd.Series):
        document_data = ExcelDataMapper.map_employee_documents(row)
        self.session.add(EmployeeDocument(employee_id=employee.id, **document_data))