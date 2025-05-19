from fastapi import FastAPI
from src.interfaces.routers import auth


app = FastAPI()
app.include_router(auth.router)

