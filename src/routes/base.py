from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import get_settings, Settings

base_router = APIRouter(prefix="/api/v1", tags=["api_v1"])

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):

    application_name = app_settings.APP_NAME

    return{
         'message': f'Welcome to the {application_name}!'
    }
