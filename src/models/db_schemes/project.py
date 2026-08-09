from pydantic import BaseModel, Field, validator
from typing import Optional
from bson import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_name: str = Field(..., min_length=1)

    @validator('project_name')
    def validate_project_name(cls, value):
        if not value.isalnum():
            raise ValueError('project_name must be alphanumeric')
        
        return value

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):

        return [
            {
                "key": [
                    ("project_name", 1)
                ],
                "name": "project_name_index",
                "unique": True
            }
        ]

