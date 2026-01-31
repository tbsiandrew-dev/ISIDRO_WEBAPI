# ISIDRO Web API

FastAPI application with PostgreSQL 17 database connectivity using Neon.

## Setup

1. Create and activate virtual environment:
```bash
cd web
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
# or
source venv/bin/activate  # On macOS/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure your `secrets.env` file exists in the root directory with database credentials:
```
DATABASE_USER=your_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=your_host
DATABASE_NAME=your_database
```

4. Run the application from the root directory:
```bash
cd ..
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

## API Endpoints

### General
- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint (tests database connection)
- `GET /db/info` - Database information

### Users (CRUD)
- `POST /users/` - Create a new user
- `GET /users/` - Get all users (with pagination)
- `GET /users/{user_id}` - Get a specific user
- `PUT /users/{user_id}` - Update a user
- `DELETE /users/{user_id}` - Delete a user

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
ISIDRO_WEBAPI/
├── main.py              # FastAPI application entry point
├── secrets.env          # Database credentials (root level)
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── web/
    ├── database.py      # Database configuration and connection
    ├── models.py        # SQLAlchemy models and Pydantic schemas
    ├── routes.py        # API route handlers
    ├── requirements.txt # Python dependencies
    ├── venv/            # Virtual environment
    └── README.md        # Web app documentation
```

## Example Usage

### Create a user:
```bash
curl -X POST "http://localhost:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### Get all users:
```bash
curl "http://localhost:8000/users/"
```

## Database

The application connects to a PostgreSQL 17 database hosted on Neon using credentials from `secrets.env`.

- Uses SQLAlchemy 2.0 with async support
- Uses asyncpg driver for async PostgreSQL operations
- Automatic table creation on startup
