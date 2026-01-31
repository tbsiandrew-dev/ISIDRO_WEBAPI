from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from web.database import get_db, engine, Base
from contextlib import asynccontextmanager
from web.routes import router as user_router
from web.api.auth import router as auth_router
from web.api.personal_info import router as personal_info_router
from web.api.disciple import router as disciple_router
from web.api.devotion import router as devotion_router
from web.api.training import router as training_router

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: Close connections
    await engine.dispose()

# Create FastAPI app
app = FastAPI(
    title="ISIDRO Web API",
    description="FastAPI application with PostgreSQL 17 database",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(personal_info_router)
app.include_router(disciple_router)
app.include_router(devotion_router)
app.include_router(training_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ISIDRO Web API",
        "status": "running",
        "database": "PostgreSQL 17 (Neon)"
    }

# Health check endpoint
@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check API and database health"""
    try:
        # Test database connection
        result = await db.execute(text("SELECT version()"))
        db_version = result.scalar()
        
        return {
            "status": "healthy",
            "database": "connected",
            "db_version": db_version
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

# Database info endpoint
@app.get("/db/info")
async def database_info(db: AsyncSession = Depends(get_db)):
    """Get database information"""
    try:
        # Get PostgreSQL version
        version_result = await db.execute(text("SELECT version()"))
        version = version_result.scalar()
        
        # Get current database name
        db_result = await db.execute(text("SELECT current_database()"))
        database_name = db_result.scalar()
        
        # Get current user
        user_result = await db.execute(text("SELECT current_user"))
        current_user = user_result.scalar()
        
        return {
            "version": version,
            "database": database_name,
            "user": current_user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching database info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
