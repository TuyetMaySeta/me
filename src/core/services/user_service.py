from typing import List, Optional
import logging
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from src.core.models.user import User
from src.present.request.user import UserCreate, UserUpdate
from src.common.exception.exceptions import ValidationException, ConflictException, NotFoundException, InternalServerException
from src.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """User service with business logic for user operations"""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create(self, user_create: UserCreate) -> User:
        """Create a new user with business logic validation"""
        logger.info(f"Starting user creation process for email: {user_create.email}")
        
        # Check if email already exists
        if self.user_repository.get_by_email(user_create.email):
            logger.warning(f"User creation failed: Email {user_create.email} already registered")
            raise ConflictException("Email already registered", "EMAIL_EXISTS")
        
        # Check if username already exists
        if self.user_repository.get_by_username(user_create.username):
            logger.warning(f"User creation failed: Username {user_create.username} already taken")
            raise ConflictException("Username already taken", "USERNAME_EXISTS")
        
        # Hash the password
        logger.debug(f"Hashing password for user: {user_create.email}")
        hashed_password = self._hash_password(user_create.password)
        
        # Create user data
        user_data = {
            "email": user_create.email,
            "username": user_create.username,
            "full_name": user_create.full_name,
            "hashed_password": hashed_password,
            "is_active": user_create.is_active
        }
        
        try:
            logger.debug(f"Saving user to database: {user_create.email}")
            user = self.user_repository.create(user_data)
            logger.info(f"User created successfully: {user.email} (ID: {user.id})")
            return user
        except IntegrityError as e:
            logger.error(f"Database integrity error during user creation: {str(e)}")
            raise InternalServerException("User creation failed due to database constraints", "DATABASE_INTEGRITY_ERROR")
    
    def get(self, user_id: int) -> User:
        """Get a user by ID"""
        user = self.user_repository.get(user_id)
        if not user:
            logger.warning(f"User with ID {user_id} not found")
            raise NotFoundException(f"User with ID {user_id} not found", "USER_NOT_FOUND")
        return user
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.user_repository.get_by_email(email)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.user_repository.get_by_username(username)
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination"""
        logger.info(f"Getting multiple users with pagination: {skip}, {limit}")
        return self.user_repository.get_multi(skip, limit)
    
    def update(self, user_id: int, user_update: UserUpdate) -> User:
        """Update a user with business logic validation"""
        logger.info(f"Starting user update process for user ID: {user_id}")
        
        user = self.user_repository.get(user_id)
        if not user:
            logger.warning(f"User update failed: User with ID {user_id} not found")
            raise NotFoundException(f"User with ID {user_id} not found", "USER_NOT_FOUND")
        
        logger.debug(f"Updating user: {user.email}")
        
        # Check for email conflicts if email is being updated
        if user_update.email and user_update.email != user.email:
            existing_user = self.user_repository.get_by_email(user_update.email)
            if existing_user:
                logger.warning(f"User update failed: Email {user_update.email} already registered")
                raise ConflictException("Email already registered", "EMAIL_EXISTS")
        
        # Check for username conflicts if username is being updated
        if user_update.username and user_update.username != user.username:
            existing_user = self.user_repository.get_by_username(user_update.username)
            if existing_user:
                logger.warning(f"User update failed: Username {user_update.username} already taken")
                raise ConflictException("Username already taken", "USERNAME_EXISTS")
        
        # Prepare update data
        update_data = user_update.model_dump(exclude_unset=True)
        logger.debug(f"Update data prepared for user {user.email}: {list(update_data.keys())}")
        
        try:
            updated_user = self.user_repository.update(user, update_data)
            logger.info(f"User updated successfully: {updated_user.email} (ID: {updated_user.id})")
            return updated_user
        except IntegrityError as e:
            logger.error(f"Database integrity error during user update: {str(e)}")
            raise ValueError("User update failed due to database constraints")
    
    def delete(self, user_id: int) -> None:
        """Delete a user"""
        logger.info(f"Starting user deletion process for user ID: {user_id}")
        
        user = self.user_repository.get(user_id)
        if not user:
            logger.warning(f"User deletion failed: User with ID {user_id} not found")
            raise NotFoundException(f"User with ID {user_id} not found", "USER_NOT_FOUND")
        
        logger.debug(f"Deleting user: {user.email}")
        result = self.user_repository.delete(user_id)
        
        if result:
            logger.info(f"User deleted successfully: {user.email} (ID: {user_id})")
        else:
            logger.error(f"User deletion failed for user ID: {user_id}")
            raise InternalServerException("Failed to delete user", "DELETE_FAILED")
    
    def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user with email and password"""
        user = self.user_repository.get_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: User with email {email} not found")
            raise UnauthorizedException("Incorrect email or password", "INVALID_CREDENTIALS")
        
        if not self._verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for email {email}")
            raise UnauthorizedException("Incorrect email or password", "INVALID_CREDENTIALS")
        
        if not user.is_active:
            logger.warning(f"Authentication failed: User {email} is not active")
            raise UnauthorizedException("Account is not active", "ACCOUNT_INACTIVE")
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """Change user password"""
        user = self.user_repository.get(user_id)
        if not user:
            logger.warning(f"Password change failed: User with ID {user_id} not found")
            raise NotFoundException(f"User with ID {user_id} not found", "USER_NOT_FOUND")
        
        if not self._verify_password(old_password, user.hashed_password):
            logger.warning(f"Password change failed: Invalid old password for user ID {user_id}")
            raise ValidationException("Invalid old password", "INVALID_OLD_PASSWORD")
        
        hashed_new_password = self._hash_password(new_password)
        user.hashed_password = hashed_new_password
        self.user_repository.db.commit()
        logger.info(f"Password changed successfully for user ID: {user_id}")
