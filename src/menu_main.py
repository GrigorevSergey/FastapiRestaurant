from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from src.redis import close_redis
from debug_toolbar.middleware import DebugToolbarMiddleware
from src.interfaces.routers.v1 import menu as menu_v1
from src.interfaces.routers.v2 import menu as menu_v2

app = FastAPI(
    title="Menu Service API",
    description="API для управления меню ресторана",
    version="1.0.0",
    debug=True
)

app.add_middleware(DebugToolbarMiddleware)

app.include_router(menu_v1.router, prefix="/menu1", tags=["v1"])
app.include_router(menu_v2.router, prefix="/menu2", tags=["v2"])

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
    
@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()