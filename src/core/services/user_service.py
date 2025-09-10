from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from src.core.models.user import User
from src.present.request.user import UserCreate, UserUpdate
from src.repository.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """User service with business logic for user operations"""
    
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
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
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if self.user_repository.get_by_username(user_create.username):
            logger.warning(f"User creation failed: Username {user_create.username} already taken")
            raise ValueError("Username already taken")
        
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
            raise ValueError("User creation failed due to database constraints")
    
    def get(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.user_repository.get(user_id)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.user_repository.get_by_email(email)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.user_repository.get_by_username(username)
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination"""
        return self.user_repository.get_multi(skip, limit)
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        return self.user_repository.get_active_users(skip, limit)
    
    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update a user with business logic validation"""
        logger.info(f"Starting user update process for user ID: {user_id}")
        
        user = self.user_repository.get(user_id)
        if not user:
            logger.warning(f"User update failed: User with ID {user_id} not found")
            return None
        
        logger.debug(f"Updating user: {user.email}")
        
        # Check for email conflicts if email is being updated
        if user_update.email and user_update.email != user.email:
            existing_user = self.user_repository.get_by_email(user_update.email)
            if existing_user:
                logger.warning(f"User update failed: Email {user_update.email} already registered")
                raise ValueError("Email already registered")
        
        # Check for username conflicts if username is being updated
        if user_update.username and user_update.username != user.username:
            existing_user = self.user_repository.get_by_username(user_update.username)
            if existing_user:
                logger.warning(f"User update failed: Username {user_update.username} already taken")
                raise ValueError("Username already taken")
        
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
    
    def delete(self, user_id: int) -> bool:
        """Delete a user"""
        logger.info(f"Starting user deletion process for user ID: {user_id}")
        
        user = self.user_repository.get(user_id)
        if not user:
            logger.warning(f"User deletion failed: User with ID {user_id} not found")
            return False
        
        logger.debug(f"Deleting user: {user.email}")
        result = self.user_repository.delete(user_id)
        
        if result:
            logger.info(f"User deleted successfully: {user.email} (ID: {user_id})")
        else:
            logger.error(f"User deletion failed for user ID: {user_id}")
        
        return result
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user (soft delete)"""
        return self.user_repository.deactivate_user(user_id)
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user"""
        return self.user_repository.activate_user(user_id)
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password"""
        user = self.user_repository.get_by_email(email)
        if not user:
            return None
        
        if not self._verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.user_repository.get(user_id)
        if not user:
            return False
        
        if not self._verify_password(old_password, user.hashed_password):
            return False
        
        hashed_new_password = self._hash_password(new_password)
        user.hashed_password = hashed_new_password
        self.user_repository.db.commit()
        return True
