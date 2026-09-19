from pydantic import BaseModel
from typing import Optional
from models import ProjectModel

class PushRequest(BaseModel):
    do_reset: Optional[int] = 0

class QueryRequest(BaseModel):
    text: str
    limit: Optional[int] = 5