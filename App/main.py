from fastapi import FastAPI
from App.model import *
from App.Services.generate import generate_diagram
from App.Services.generate import generate_derived_artifact
app = FastAPI(title="Archie AI Service")


@app.post("/generate", response_model=ApiResponse)
def generate(request: GenerateRequest):
    try:
        diag_type = request.diagramType.upper()
        
        # Check if it's a "Derived" request
        is_db = "DATABASE" in diag_type
        is_api = "API" in diag_type

        if is_db or is_api:
            # STEP 1: Generate the base UML first for context
            base_type = "ERD" if is_db else "Sequence Diagram"
            uml_context = generate_diagram(base_type, request.requirementsText)
            
            # STEP 2: Generate the actual Code/Contract using the UML
            final_output = generate_derived_artifact(request.diagramType, request.requirementsText, uml_context)
            
            return ApiResponse(
                status="SUCCESS",
                data={
                    "diagramType": request.diagramType,
                    "diagramLanguage": "JSON/SQL" if is_db else "OPENAPI",
                    "diagramCode": final_output,
                    "isRenderable": False
                },
                error=None
            )
        
        # Standard Diagram path
        diagram_code = generate_diagram(request.diagramType, request.requirementsText)
        return ApiResponse(
            status="SUCCESS",
            data={
                "diagramType": request.diagramType,
                "diagramLanguage": "PLANTUML",
                "diagramCode": diagram_code,
                "isRenderable": True
            },
            error=None
        )

    except Exception as e:
        return ApiResponse(status="FAILURE", data=None, error={"message": str(e), "code": "ERR"})



# @app.post("/generate", response_model=ApiResponse)
# def generate(request: GenerateRequest):
#     try:
#         diagram_code = generate_diagram(
#             request.diagramType,
#             request.requirementsText
#         )

#         return ApiResponse(
#             status="SUCCESS",
#             data={
#                 "diagramType": request.diagramType,
#                 "diagramLanguage": "PLANTUML",
#                 "diagramCode": diagram_code,
#                 "isRenderable": True
#             },
#             error=None
#         )

#     except Exception as e:
#         return ApiResponse(
#             status="FAILURE",
#             data=None,
#             error={
#                 "message": "Failed to generate diagram",
#                 "code": "GENERATION_FAILED"
#             }
#         )
