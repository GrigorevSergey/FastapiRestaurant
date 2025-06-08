from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from src.interfaces.routers import auth, users

app = FastAPI(
    title="Users Service API",
    description="API для управления пользователями и аутентификацией",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router)
app.include_router(users.router)

@app.exception_handler(HTTPException)
async def app_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    ) 