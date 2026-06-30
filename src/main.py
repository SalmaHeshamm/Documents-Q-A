from fastapi import FastAPI, APIRouter
from src.routes import base
from dotenv import load_dotenv

load_dotenv(".env")

app = FastAPI()

app.include_router(base.base_router)



