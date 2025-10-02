import pandas as pd
import re
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from src.core.enums.employee import GenderEnum, MaritalStatusEnum, SkillCategoryEnum

logger = logging.getLogger(__name__)


class ExcelDataMapper:

    @staticmethod
    def map_employee_data(row: pd.Series) -> Dict[str, Any]:
        return {
            "id": ExcelDataMapper._clean_id(row.get("ID1")),
            "full_name": ExcelDataMapper._clean_text(row.get("Họ và tên (VIẾT HOA CÓ DẤU)")),
            "email": ExcelDataMapper._clean_text(row.get("Email cá nhân")),
            "phone": ExcelDataMapper._clean_number(row.get("Số điện thoại (vui lòng thêm dấu ' trước số điện thoại)")),
            "gender": ExcelDataMapper._parse_gender(row.get("Giới tính")),
            "date_of_birth": ExcelDataMapper._parse_date(row.get("Ngày tháng năm sinh")),
            "marital_status": ExcelDataMapper._parse_marital_status(row.get("Tình trạng hôn nhân")),
            "join_date": ExcelDataMapper._parse_date(row.get("Ngày vào công ty")),
            "permanent_address": ExcelDataMapper._clean_text(row.get("Hộ khẩu thường trú (theo địa giới hành chính mới)\nxã/phường, huyện/quận, tỉnh/thành\n")),
            "current_address": ExcelDataMapper._clean_text(row.get("Nơi ở hiện tại (theo địa giới hành chính mới)\nxã/phường, huyện/quận, tỉnh/thành\n")),
            "current_position": ExcelDataMapper._clean_text(row.get("Vị trí làm việc hiện tại")),
        }

    @staticmethod
    def map_employee_profile_data(row: pd.Series) -> Dict[str, Any]:
        return {
            "facebook_link": ExcelDataMapper._extract_facebook_link(row.get("Ten + link facebook của anh/chị (nếu có)")),
            "how_heard_about_company": ExcelDataMapper._clean_text(row.get("Anh/chị biết đến SETA qua kênh nào?")),
            "hobbies": ExcelDataMapper._clean_text(row.get("Sở thích, thế mạnh cá nhân của anh/chị")),
        }

    @staticmethod
    def map_employee_all_technical_skills(row: pd.Series) -> List[Dict[str, Any]]:
        skill_columns = [
            "Vui lòng liệt kê các ngôn ngữ lập trình, framework, công nghệ anh/chị đã và đang sử dụng.\n (Ví dụ: Java, Spring Boot, ReactJS, PostgreSQL…)",
            "Ngoài các công nghệ chính, anh/chị còn có kỹ năng hoặc kinh nghiệm ở những mảng nào khác?\n (Ví dụ: DevOps, Automation Testing, UI/UX, Data Analysis…)",
        ]

        skills = set()
        for col in skill_columns:
            skills.update(map(str.strip, ExcelDataMapper._parse_skills(row.get(col))))

        description = ExcelDataMapper._clean_text(
            row.get("Mô tả ngắn gọn kinh nghiệm của anh/chị với các công nghệ trên\n (Số năm kinh nghiệm, vai trò, loại dự án đã tham gia…)")
        )

        return [
            {"skill_name": skill, "description": description, "category": ExcelDataMapper._categorize_skill(skill)}
            for skill in skills
        ]

    @staticmethod
    def map_employee_education(row: pd.Series) -> List[Dict[str, Any]]:
        base = {
            "school_name": ExcelDataMapper._clean_text(row.get("Trường đào tạo")),
            "degree": ExcelDataMapper._clean_text(row.get("Bằng cấp")),
            "major": ExcelDataMapper._clean_text(row.get("Chuyên ngành")),
        }

        years = ExcelDataMapper._parse_graduation_year(row.get("Năm tốt nghiệp"))
        return [{**base, "graduation_year": y} for y in years] or [base]

    @staticmethod
    def map_employee_contacts(row: pd.Series) -> List[Dict[str, str]]:
        raw = ExcelDataMapper._clean_text(row.get("Số điện thoại người thân khi cần liên hệ (Vợ, bố, mẹ, anh chị...)"))
        if not raw:
            return []

        contacts = []
        for entry in raw.split(";"):
            parts = [p.strip() for p in entry.split("-")]
            if len(parts) == 3:
                relation, name, phone = parts
                phone_digits = re.sub(r"\D", "", phone)
                if relation and name and phone_digits:
                    contacts.append({"relation": relation, "name": name, "phone": phone_digits})
        return contacts

    @staticmethod
    def map_employee_children(row: pd.Series) -> List[Dict[str, Any]]:
        raw = ExcelDataMapper._clean_text(row.get("Họ tên các con\xa0 - ngày tháng năm sinh tương ứng"))
        if not raw:
            return []

        children = []
        for entry in raw.split(";"):
            parts = [p.strip() for p in entry.split("-")]
            if len(parts) == 2:
                full_name, dob = parts
                date_parsed = ExcelDataMapper._parse_date(dob)
                if date_parsed:
                    children.append({"full_name": full_name, "date_of_birth": date_parsed})
        return children

    @staticmethod
    def map_employee_documents(row: pd.Series) -> Dict[str, Any]:
        account_number, bank_name, branch_name = ExcelDataMapper.normalize_account(
            row.get("Số tài khoản ngân hàng Vietcombank ghi rõ tên chi nhánh mở thẻ. Vui lòng thêm dấu ' trước STK nếu STK bắt đầu bằng số 0\nLưu ý: Chỉ điền số tài khoản của VCB chính chủ, không điền số tài khoản của ngân")
        )
        return {
            "identity_number": ExcelDataMapper._clean_number(row.get("Số CCCD\xa0(vui lòng thêm dấu ' trước số CCCDi)")),
            "tax_id_number": ExcelDataMapper._clean_number(row.get("Mã số thuế.\xa0")),
            "identity_place": ExcelDataMapper._clean_text(row.get("Nơi cấp")),
            "identity_date": ExcelDataMapper._parse_date(row.get("Ngày cấp")),
            "social_insurance_number": ExcelDataMapper._clean_number(row.get("Số sổ bảo hiểm xã hội (nếu có).")),
            "account_bank_number": account_number,
            "bank_name": bank_name,
            "branch_name": branch_name,
            "motorbike_plate": ExcelDataMapper._clean_text(row.get("Biển số xe máy (nếu có).")),
            "old_identity_number": ExcelDataMapper._clean_number(row.get("CMTND cũ.")),
        }

    # ================= VALIDATE =================

    @staticmethod
    def _clean_id(value) -> Optional[str]:
        if not value or pd.isna(value):
            return None
        digits = "".join(filter(str.isdigit, str(value)))
        return digits if len(digits) <= 5 else None

    @staticmethod
    def _clean_text(value) -> Optional[str]:
        if not value or pd.isna(value):
            return None
        text = str(value).strip()
        return text if text and text.lower() != "nan" else None

    @staticmethod
    def _clean_number(value) -> Optional[str]:
        if not value or pd.isna(value):
            return None
        num = str(value).replace("'", "").strip()
        if num.endswith(".0"):
            num = num[:-2]
        return num if num.isdigit() else None

    @staticmethod
    def _parse_date(value) -> Optional[datetime.date]:
        if not value or pd.isna(value):
            return None
        if isinstance(value, datetime):
            return value.date()
        try:
            return datetime.strptime(str(value).strip(), "%d/%m/%Y").date()
        except Exception:
            return None

    @staticmethod
    def _parse_gender(value) -> Optional[GenderEnum]:
        mapping = {"Nam": GenderEnum.MALE, "Nữ": GenderEnum.FEMALE}
        return mapping.get(ExcelDataMapper._clean_text(value))

    @staticmethod
    def _parse_marital_status(value) -> Optional[MaritalStatusEnum]:
        mapping = {
            "Độc thân": MaritalStatusEnum.SINGLE,
            "Đã kết hôn": MaritalStatusEnum.MARRIED,
            "Ly dị": MaritalStatusEnum.DIVORCED,
            "Góa phụ": MaritalStatusEnum.WIDOWED,
        }
        return mapping.get(ExcelDataMapper._clean_text(value))

    @staticmethod
    def _extract_facebook_link(value) -> Optional[str]:
        text = ExcelDataMapper._clean_text(value)
        if not text:
            return None
        urls = re.findall(r"https?://[^\s]+|(?:fb\.com|facebook\.com)/[^\s]+", text)
        return urls[0] if urls else (text if "fb.com" in text else None)

    @staticmethod
    def _parse_skills(value) -> List[str]:
        text = ExcelDataMapper._clean_text(value)
        return [s.strip() for s in text.split(";")] if text else []

    @staticmethod
    def _parse_graduation_year(value) -> List[int]:
        if not value or pd.isna(value):
            return []
        return [int(y) for y in re.findall(r"\b\d{4}\b", str(value))]

    @staticmethod
    def normalize_account(raw: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if not raw or str(raw).lower() == "nan":
            return None, None, None
        text = str(raw).replace("'", "").strip()
        if "-" in text:
            parts = [p.strip() for p in text.split("-")]
            return parts[0], parts[1].title() if len(parts) > 1 else None, parts[2].title() if len(parts) > 2 else None
        if text.isdigit():
            return text, None, None
        match = re.search(r"\d{8,20}", text)
        return (match.group(0), None, None) if match else (None, None, None)

    @staticmethod
    def _categorize_skill(skill: str) -> SkillCategoryEnum:
        skill_lower = skill.lower()
        if any(lang in skill_lower for lang in ["python", "java", "javascript", "c++", "go", "c#", "ruby"]):
            return SkillCategoryEnum.PROGRAMMING_LANGUAGE
        if any(db in skill_lower for db in ["mysql", "postgresql", "mongodb", "oracle", "sql server"]):
            return SkillCategoryEnum.DATABASE
        if any(fw in skill_lower for fw in ["spring", "django", "react", "angular", "vue", "flask"]):
            return SkillCategoryEnum.FRAMEWORK
        if any(tool in skill_lower for tool in ["docker", "kubernetes", "git", "jenkins", "ansible"]):
            return SkillCategoryEnum.TOOL
        if any(hw in skill_lower for hw in ["arduino", "raspberry", "fpga"]):
            return SkillCategoryEnum.HARDWARE
        return SkillCategoryEnum.TOOL
