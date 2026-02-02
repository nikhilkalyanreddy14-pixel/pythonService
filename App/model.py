from pydantic import BaseModel
from typing import Optional, Any

# -------- Requests --------

class GenerateRequest(BaseModel):
    diagramType: str
    requirementsText: str

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
    outputFormat: str   # SVG | PNG


# -------- Responses --------

class ErrorResponse(BaseModel):
    message: str
    code: str

class ApiResponse(BaseModel):
    status: str
    data: Optional[Any]
    error: Optional[ErrorResponse]
