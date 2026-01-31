# ISIDRO Web API

FastAPI application with PostgreSQL 17 database connectivity.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your `secrets.env` file contains the PostgreSQL connection string.

3. Run the application:
```bash
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
├── main.py          # FastAPI application entry point
├── database.py      # Database configuration and connection
├── models.py        # SQLAlchemy models and Pydantic schemas
├── routes.py        # API route handlers
├── requirements.txt # Python dependencies
├── secrets.env      # Database credentials
└── README.md        # This file
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
