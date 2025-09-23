from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from src.config.config import settings
from src.present.routers.health_router import router as health_router
from src.present.routers.employee_router import router as employee_router
from src.present.routers.auth_router import router as auth_router
from src.present.middleware.request_id_middleware import RequestIDMiddleware
from src.common.exception.exceptions import EMSException
from src.common.log import setup_logging

from sqlalchemy import text
from src.bootstrap.database_bootstrap import database_bootstrap

logger = logging.getLogger(__name__)


async def ems_exception_handler(request: Request, exc: EMSException) -> JSONResponse:
    logger.warning(f"EMS Exception: {exc.error_code} - {exc.message}")

    error_response = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "http_status": exc.http_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    }

    # Add specific suggestions for common errors
    if exc.error_code == "DUPLICATE_EMAIL":
        error_response["error"]["suggestion"] = "Please use a different email address."
        error_response["error"]["action"] = "Use unique email."

    elif exc.error_code == "DUPLICATE_EMPLOYEE_ID":
        error_response["error"]["suggestion"] = "Please use a different employee ID."
        error_response["error"]["action"] = "Use unique employee ID."

    elif exc.error_code == "DUPLICATE_PHONE":
        error_response["error"]["suggestion"] = "Please use a different phone number."
        error_response["error"]["action"] = "Use unique phone number."

    elif exc.error_code == "EMPLOYEE_NOT_FOUND":
        error_response["error"]["suggestion"] = "Check Employee ID or if it has been deleted."
        error_response["error"]["action"] = "Verify Employee ID."

    elif "VALIDATION" in exc.error_code:
        error_response["error"]["suggestion"] = "Check your input data format and requirements."
        error_response["error"]["action"] = "Correct the data according to validation rules."

    # Authentication specific errors
    elif exc.error_code == "INVALID_CREDENTIALS":
        error_response["error"]["suggestion"] = "Check your employee ID/email and password."
        error_response["error"]["action"] = "Verify login credentials."

    elif exc.error_code == "ACCOUNT_INACTIVE":
        error_response["error"]["suggestion"] = "Contact your administrator to reactivate your account."
        error_response["error"]["action"] = "Contact HR or IT support."

    elif exc.error_code == "TOKEN_EXPIRED":
        error_response["error"]["suggestion"] = "Your session has expired. Please login again."
        error_response["error"]["action"] = "Re-authenticate."

    elif exc.error_code == "INVALID_TOKEN":
        error_response["error"]["suggestion"] = "Invalid authentication token. Please login again."
        error_response["error"]["action"] = "Re-authenticate."

    elif exc.error_code == "NO_PASSWORD":
        error_response["error"]["suggestion"] = "Your account password is not set. Contact administrator."
        error_response["error"]["action"] = "Contact HR to set password."

    return JSONResponse(
        status_code=exc.http_status,
        content=error_response
    )

# -----------------------------
# Database Check Functions
# -----------------------------
def check_database_connection() -> bool:
    """Check database connection"""
    print("🔍 Checking database connection...")
    if database_bootstrap.test_connection():
        print("✅ Database connection successful!")
        print(f"📊 Database URL: {settings.database_url}")
        return True
    else:
        print("❌ Database connection failed! Check DB server and .env")
        return False

def check_database_tables() -> bool:
    """Check required tables exist"""
    print("🔍 Checking required tables...")
    try:
        with database_bootstrap.engine.connect() as conn:
            # Check if employees table exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'employees'
            """))
            table_exists = result.scalar() > 0
            
            if table_exists:
                employee_count = conn.execute(text("SELECT COUNT(*) FROM employees")).scalar()
                print(f"✅ Employees table exists. Records: {employee_count}")
                
                # Check employee_sessions table
                sessions_result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = 'employee_sessions'
                """))
                sessions_exist = sessions_result.scalar() > 0
                
                if sessions_exist:
                    sessions_count = conn.execute(text("SELECT COUNT(*) FROM employee_sessions")).scalar()
                    print(f"✅ Employee sessions table exists. Records: {sessions_count}")
                else:
                    print("⚠️  Employee sessions table not found. Authentication may not work.")
                
                # Check related tables
                related_tables = [
                    'employee_contacts', 'employee_documents', 'employee_education',
                    'employee_certifications', 'employee_profiles', 'languages',
                    'employee_technical_skills', 'employee_projects', 'employee_children'
                ]
                
                existing_related = []
                for table in related_tables:
                    try:
                        result = conn.execute(text(f"""
                            SELECT COUNT(*) FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        """))
                        if result.scalar() > 0:
                            existing_related.append(table)
                    except:
                        pass
                
                print(f"📋 Related tables found: {len(existing_related)}/{len(related_tables)}")
                return True
            else:
                print("❌ Employees table not found. Run migrations: python migrate.py upgrade")
                return False
    except Exception as e:
        print(f"❌ Could not check tables: {e}")
        return False

# -----------------------------
# Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*70)
    print("🚀 Starting EMS Employee Management System...")
    print("="*70)

    # Database check
    db_connected = check_database_connection()
    if db_connected:
        tables_exist = check_database_tables()
        if not tables_exist:
            print("\n⚠️  Tables missing. App may not work properly until migrations run.")
            print("💡 Run: python migrate.py upgrade")
    else:
        print("\n🚨 Critical: DB connection failed. App will start but may not work.")
        print("💡 Check: docker-compose up -d")

    # Initialize application layers
    try:
        from src.bootstrap.application_bootstrap import app_bootstrap
        print("✅ Application layers initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize app layers: {e}")
        raise

    print("\n🎉 EMS Employee Management System is ready!")
    print(f"🌐 Server: http://{settings.host}:{settings.port}")
    print(f"📖 API Docs: http://{settings.host}:{settings.port}/ems/api/v1/docs")
    print(f"💓 Health Check: http://{settings.host}:{settings.port}/ems/api/v1/health")
    print(f"🔐 Auth Login: http://{settings.host}:{settings.port}/ems/api/v1/auth/login")
    print("="*70 + "\n")

    yield

    print("\n🛑 Shutting down EMS Employee Management System...")
    try:
        app_bootstrap.shutdown()
        print("✅ Cleanup completed successfully!")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="EMS Employee Management System",
    version=settings.app_version,
    description="""
    **Employee Management System** with FastAPI + PostgreSQL + Authentication
    
    ## Features:
    - 🔐 **JWT Authentication** with refresh tokens
    - 👥 **Employee CRUD** with validation
    - 📱 **Vietnamese phone number validation** (10-11 digits, starts with 0)
    - 📄 **Vietnamese document validation** (CCCD, CMND, Tax ID, etc.)
    - 🏢 **Comprehensive employee profiles** with contacts, documents, skills
    - 📊 **Pagination support**
    - 🔗 **Database constraints** and foreign key cascading
    - 🛡️ **Session management** with device tracking
    
    ## Authentication:
    - **Login**: `POST /auth/login` with employee ID/email + password
    - **Refresh**: `POST /auth/refresh` to get new access token
    - **Verify**: `POST /auth/verify` to check token validity
    
    ## Validation Rules:
    - **Phone**: 10-11 digits, mobile must start with 03/05/07/08/09
    - **Employee ID**: 3-50 chars, alphanumeric with dash/underscore
    - **Age**: Must be 16-100 years old
    - **CCCD**: Exactly 12 digits
    - **Tax ID**: 10-13 digits
    - **Bank Account**: 6-30 digits
    
    ## Security:
    - **JWT tokens**: Access (24h) + Refresh (30d) tokens
    - **HTTP-only cookies**: Secure token storage
    - **Session tracking**: Device info, IP, user agent
    - **Password hashing**: bcrypt with 12 rounds
    """,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/ems/api/v1/docs",
    redoc_url="/ems/api/v1/redoc",
    openapi_url="/ems/api/v1/openapi.json"
)

# Logging setup
setup_logging(settings.log_level)

# Middleware
app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
app.add_exception_handler(EMSException, ems_exception_handler)

# API Routes
api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(health_router)      # Health endpoints
api_router.include_router(employee_router)    # Employee management
api_router.include_router(auth_router)        # Authentication endpoints
app.include_router(api_router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with system information
    """
    return {
        "message": "🚀 EMS Employee Management System",
        "version": settings.app_version,
        "status": "running",
        "api_prefix": settings.api_prefix,
        "documentation": {
            "swagger_ui": "/ems/api/v1/docs",
            "redoc": "/ems/api/v1/redoc"
        },
        "endpoints": {
            "health_check": f"{settings.api_prefix}/health",
            "authentication": {
                "login": f"{settings.api_prefix}/auth/login",
                "refresh": f"{settings.api_prefix}/auth/refresh", 
                "verify": f"{settings.api_prefix}/auth/verify"
            },
            "employees": {
                "list": f"{settings.api_prefix}/employees/",
                "create": f"{settings.api_prefix}/employees/",
                "get_by_id": f"{settings.api_prefix}/employees/{{id}}",
                "update": f"{settings.api_prefix}/employees/{{id}}",
                "delete": f"{settings.api_prefix}/employees/{{id}}"
            }
        },
        "features": [
            "JWT Authentication with refresh tokens",
            "Session management with device tracking",
            "Vietnamese phone number validation",
            "Document validation (CCCD, CMND, Tax ID)",
            "Employee profiles with related data",
            "Pagination support",
            "Database constraints and cascading",
            "Secure HTTP-only cookies"
        ],
        "validation_rules": {
            "phone": "10-11 digits starting with 0, mobile: 03/05/07/08/09",
            "employee_id": "3-50 chars, alphanumeric + dash/underscore",
            "age": "16-100 years old",
            "cccd": "exactly 12 digits",
            "tax_id": "10-13 digits"
        },
        "security": {
            "jwt_algorithm": settings.jwt_algorithm,
            "access_token_expiry": f"{settings.access_token_expire_minutes} minutes",
            "refresh_token_expiry": f"{settings.refresh_token_expire_days} days",
            "password_hashing": "bcrypt with 12 rounds"
        }
    }

# Simple status endpoint
@app.get("/status", tags=["Root"])
async def status():
    """
    Simple status check
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "EMS Employee Management System",
        "version": settings.app_version,
        "database": "connected" if database_bootstrap.test_connection() else "disconnected"
    }

# Authentication info endpoint
@app.get("/auth-info", tags=["Root"])
async def auth_info():
    """
    Authentication information and setup guide
    """
    return {
        "message": "EMS Authentication System",
        "login_endpoint": f"{settings.api_prefix}/auth/login",
        "required_fields": {
            "employee_id": "Employee ID or email address",
            "password": "Employee password"
        },
        "optional_fields": {
            "remember_me": "Extend session duration (default: false)"
        },
        "response_includes": [
            "access_token (JWT, 24h expiry)",
            "refresh_token (30d expiry)", 
            "employee information",
            "session details"
        ],
        "security_features": [
            "HTTP-only secure cookies",
            "Device and IP tracking",
            "Session management",
            "Automatic token refresh"
        ],
        "example_request": {
            "employee_id": "EMP001 or employee@company.com",
            "password": "employee_password",
            "remember_me": False
        },
        "setup_notes": [
            "Default employee password is '12345'",
            "Employees should change password on first login",
            "Contact administrator if account is inactive"
        ]
    }

# -----------------------------
# Run Uvicorn
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        access_log=True
    )
