from fastapi import FastAPI, Request
from App.model import *
from App.Services.generate import generate_diagram, generate_derived_artifact
from App.handlers import global_exception_handler, global_response_middleware
from fastapi.exceptions import RequestValidationError

app = FastAPI(title="Archie AI Service")

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, global_exception_handler)

@app.middleware("http")
async def wrap_response(request: Request, call_next):
    return await global_response_middleware(request, call_next)

@app.post("/generate")
async def generate(request: GenerateRequest):
    diagramType = request.diagramType
    if diagramType in [DiagramType.DATABASE, DiagramType.API]:
        is_db = (diagramType == DiagramType.DATABASE)
        base_type = "ERD" if is_db else "Sequence Diagram"
        
        uml_context = await generate_diagram(base_type, request.requirementsText)
        final_output = await generate_derived_artifact(diagramType.value, request.requirementsText, uml_context)
        return {
            "diagramType": diagramType,
            "diagramLanguage": "JSON/SQL" if is_db else "OPENAPI",
            "diagramCode": final_output,
            "isRenderable": False
        }
    diagram_code = await generate_diagram(diagramType.value, request.requirementsText)
    return {
        "diagramType": diagramType,
        "diagramLanguage": "PLANTUML",
        "diagramCode": diagram_code,
        "isRenderable": True
    }