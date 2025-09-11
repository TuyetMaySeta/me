"""
EMS-IAM Client for calling EMS-IAM service with basic authentication
"""

import base64
import logging
from typing import Dict, Any, Optional
import httpx
from src.config.config import settings
from src.common.exception.exceptions import InternalServerException

logger = logging.getLogger(__name__)


class EMSIAMClient:
    """Client for EMS-IAM service with basic authentication"""
    
    def __init__(self, 
                 base_url: Optional[str] = None,
                 username: Optional[str] = None, 
                 password: Optional[str] = None,
                 timeout: int = 30):
        self.base_url = (base_url or settings.iam_service_url).rstrip('/')
        self.username = username or settings.iam_username
        self.password = password or settings.iam_password
        self.timeout = timeout
        self._client = None
        self._auth_header = self._create_auth_header()
    
    def _create_auth_header(self) -> str:
        """Create basic authentication header"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        return {
            "Authorization": self._auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make authenticated request to IAM service"""
        url = f"/api/v1/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        logger.debug(f"Making {method} request to {url}")
        
        try:
            client = self._get_client()
            response = client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers
            )
            
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise InternalServerException(
                f"IAM service error: {e.response.status_code}",
                f"IAM_ERROR_{e.response.status_code}"
            )
        except Exception as e:
            logger.error(f"Error calling IAM service: {str(e)}")
            raise InternalServerException(
                "Failed to communicate with IAM service",
                "IAM_COMMUNICATION_ERROR"
            )
    
    # User Management
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user in IAM service"""
        logger.info(f"Creating user in IAM: {user_data.get('email', 'unknown')}")
        return self._make_request("POST", "users", data=user_data)
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user by ID from IAM service"""
        logger.debug(f"Getting user from IAM: {user_id}")
        return self._make_request("GET", f"users/{user_id}")
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """Get user by email from IAM service"""
        logger.debug(f"Getting user by email from IAM: {email}")
        return self._make_request("GET", "users", params={"email": email})
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user in IAM service"""
        logger.info(f"Updating user in IAM: {user_id}")
        return self._make_request("PUT", f"users/{user_id}", data=user_data)
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete user from IAM service"""
        logger.info(f"Deleting user from IAM: {user_id}")
        return self._make_request("DELETE", f"users/{user_id}")
    
    def list_users(self, page: int = 1, limit: int = 50) -> Dict[str, Any]:
        """List users from IAM service"""
        logger.debug(f"Listing users from IAM: page={page}, limit={limit}")
        return self._make_request("GET", "users", params={"page": page, "limit": limit})
    
    # Authentication
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with IAM service"""
        logger.info(f"Authenticating user with IAM: {email}")
        return self._make_request("POST", "auth/login", data={
            "email": email,
            "password": password
        })
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate token with IAM service"""
        logger.debug("Validating token with IAM")
        return self._make_request("POST", "auth/validate", data={"token": token})
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh token with IAM service"""
        logger.debug("Refreshing token with IAM")
        return self._make_request("POST", "auth/refresh", data={"refresh_token": refresh_token})
    
    # Role Management
    def assign_role_to_user(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Assign role to user in IAM service"""
        logger.info(f"Assigning role {role_id} to user {user_id} in IAM")
        return self._make_request("POST", f"users/{user_id}/roles", data={"role_id": role_id})
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> Dict[str, Any]:
        """Remove role from user in IAM service"""
        logger.info(f"Removing role {role_id} from user {user_id} in IAM")
        return self._make_request("DELETE", f"users/{user_id}/roles/{role_id}")
    
    def get_user_roles(self, user_id: str) -> Dict[str, Any]:
        """Get user roles from IAM service"""
        logger.debug(f"Getting roles for user {user_id} from IAM")
        return self._make_request("GET", f"users/{user_id}/roles")
    
    # Permission Check
    def check_user_permission(self, user_id: str, resource: str, action: str) -> Dict[str, Any]:
        """Check if user has permission for resource and action"""
        logger.debug(f"Checking permission for user {user_id}: {action} on {resource}")
        return self._make_request("POST", "permissions/check", data={
            "user_id": user_id,
            "resource": resource,
            "action": action
        })
    
    # Health Check
    def health_check(self) -> Dict[str, Any]:
        """Check IAM service health"""
        logger.debug("Checking IAM service health")
        return self._make_request("GET", "health")
    
    def close(self):
        """Close the HTTP client"""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Create a global instance using settings
ems_iam_client = EMSIAMClient()


# Usage examples:
"""
# Basic usage with global instance
result = ems_iam_client.create_user({
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "password": "password123"
})

# Or use as context manager
with EMSIAMClient() as client:
    health = client.health_check()
    user = client.authenticate_user("user@example.com", "password123")
    
# Custom configuration
custom_client = EMSIAMClient(
    base_url="https://custom-iam.com",
    username="custom_user",
    password="custom_pass"
)
"""
