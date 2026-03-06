# AlHilo Backend API

FastAPI backend for AlHilo - Textile Adjustment and Repair Management System.

## 🏗️ Architecture

This project follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── core/           # Core configuration and utilities
│   ├── config.py       # Settings and environment variables
│   ├── database.py     # Database connection and session management
│   └── security.py     # JWT and password hashing utilities
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic schemas for validation
├── repositories/   # Data access layer (Repository Pattern)
├── services/       # Business logic layer
├── api/            # API routes and endpoints
│   └── v1/
│       ├── endpoints/  # Route handlers
│       └── api.py      # API router configuration
└── middlewares/    # Custom middleware
```

## 🚀 Tech Stack

- **FastAPI** - Modern, fast web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL** - Database
- **JWT** - Authentication
- **Pydantic** - Data validation
- **Asyncpg** - Async PostgreSQL driver

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Virtual environment (recommended)

## ⚙️ Installation

1. **Clone the repository**
```bash
cd BackEnd
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your configuration
# Update DATABASE_URL, SECRET_KEY, etc.
```

6. **Setup database**
```bash
# Run Liquibase migrations from DB Scripts folder
cd "DB Scripts"
.\migrate.bat  # Windows
# or
./migrate.sh   # Linux/Mac

# Select option 1 to update database
```

## 🔧 Configuration

Edit `.env` file with your settings:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/alhilo_db

# JWT Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_V1_STR=/api/v1
PROJECT_NAME=AlHilo API
DEBUG=True

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 🏃 Running the Application

### Development Mode
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/v1/docs
- Alternative Docs: http://localhost:8000/api/v1/redoc

## 📚 API Documentation

Once running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Login
```bash
POST /api/v1/auth/login
{
  "email": "admin@alhilo.com",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Using the token
Include the token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### Refresh Token
```bash
POST /api/v1/auth/refresh
{
  "refresh_token": "your_refresh_token"
}
```

## 🗂️ API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/me` - Get current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user

### Clients
- `POST /api/v1/clients/` - Create client
- `GET /api/v1/clients/{client_id}` - Get client
- `PUT /api/v1/clients/{client_id}` - Update client
- `GET /api/v1/clients/?query=name` - Search clients

### Repairs
- `POST /api/v1/repairs/` - Create repair
- `GET /api/v1/repairs/{repair_id}` - Get repair
- `PUT /api/v1/repairs/{repair_id}` - Update repair
- `GET /api/v1/repairs/client/{client_id}` - Get repairs by client
- `GET /api/v1/repairs/status/{status_id}` - Get repairs by status

## 🏛️ Architecture Patterns

### Repository Pattern
Abstracts data access logic, making it easier to test and maintain.

```python
# Repository handles database operations
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, db: AsyncSession, email: str):
        # Database query logic
        pass
```

### Service Layer
Contains business logic, orchestrates repositories.

```python
# Service contains business logic
class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
    
    async def create_user(self, db: AsyncSession, user_data: UserCreate):
        # Business logic
        # Validation
        # Call repository
        pass
```

### Dependency Injection
FastAPI's dependency injection system for clean, testable code.

```python
@router.get("/users/me")
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    return current_user
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📦 Database Models

- **Users** - System users with role-based access
- **Roles** - User roles (Admin, Receptionist, Seamstress)
- **Clients** - Customer information
- **Repairs** - Repair orders
- **RepairTypes** - Types of repairs with pricing
- **RepairStatus** - Status of repairs (Pending, In Progress, Completed)

## 🔒 Security Features

- Password hashing with bcrypt
- JWT token authentication
- Token expiration and refresh
- Protected endpoints with authentication
- CORS configuration
- Input validation with Pydantic

## 📝 Environment Variables

| Variable                    | Description                  | Default  |
|-----------------------------|------------------------------|----------|
| DATABASE_URL                | PostgreSQL connection string | Required |
| SECRET_KEY                  | JWT secret key               | Required |
| ALGORITHM                   | JWT algorithm                | HS256    |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime        | 30       |
| REFRESH_TOKEN_EXPIRE_DAYS   | Refresh token lifetime       | 7        |
| API_V1_STR                  | API version prefix           | /api/v1  |
| DEBUG                       | Debug mode                   | True     |

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### Module Import Errors
- Activate virtual environment
- Install requirements: `pip install -r requirements.txt`

### JWT Errors
- Verify SECRET_KEY is set in .env
- Check token expiration

## 📄 License

Private project for AlHilo.

## 👥 Support

For issues or questions, contact the development team.
