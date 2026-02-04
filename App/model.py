from pydantic import BaseModel, field_validator
from typing import Optional, Any
from enum import Enum

class DiagramType(str, Enum):
    DATABASE = "DATABASE"
    API = "API"
    ERD = "ERD"
    SEQUENCE = "SEQUENCE"
    CLASS = "CLASS"
    USE_CASE = "USE_CASE"
    COMPONENT = "COMPONENT"


class GenerateRequest(BaseModel):
    diagramType: DiagramType
    requirementsText: str
    @field_validator("diagramType", mode="before")
    @classmethod
    def to_uppercase(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v

class RefineRequest(BaseModel):
    diagramType: str
    existingDiagramCode: str
    userInstruction: str

class ValidateRequest(BaseModel):
    diagramType: str
    diagramCode: str

class RenderRequest(BaseModel):
    diagramType: str
    diagramCode: str
    outputFormat: str   

class ErrorResponse(BaseModel):
    message: str
    code: str

class ApiResponse(BaseModel):
    status: str
    data: Optional[Any]
    error: Optional[ErrorResponse]

#NIKHIL