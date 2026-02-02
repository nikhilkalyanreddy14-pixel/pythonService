import re
from App.kadalClient import get_chat_completion
from App.Services.utils import ERD_SPECIFIC_RULES, SEQUENCE_RULES, CLASS_RULES, COMPONENT_RULES, DATABASE_CODE_RULES, API_CONTRACT_RULES, USE_CASE_RULES

def generate_derived_artifact(artifact_type: str, requirements: str, source_uml: str) -> str:
    """
    New function to generate Code based on existing UML + Requirements.
    """
    diag_type_key = artifact_type.upper()
    
    if "DATABASE" in diag_type_key:
        extra_context = DATABASE_CODE_RULES
    else:
        extra_context = API_CONTRACT_RULES

    prompt = f"""
    {extra_context}
    
    [Source PlantUML Code]:
    {source_uml}
    
    [Original User Requirements]:
    {requirements}

    Constraint: Return ONLY the raw code/JSON. No markdown blocks.
    """
    
    messages = [
        {"role": "system", "content": "You are a technical architect specializing in code generation from UML."},
        {"role": "user", "content": prompt}
    ]

    responseGot = get_chat_completion(messages)
    print("\n")
    print(f"--------------{diag_type_key} Response ---------------------- ")
    print(responseGot)
    return responseGot


def clean_plantuml_code(raw_code: str) -> str:
    """Removes Markdown and ensures clean raw string for Draw.io."""
    if not raw_code: return ""
    cleaned = re.sub(r'```(?:plantuml|puml|text)?', '', raw_code)
    cleaned = cleaned.replace('```', '').strip()
    return cleaned

def generate_diagram(diagram_type: str, requirements: str) -> str:
    diag_type_key = diagram_type.upper()
    
    # Selection Mapping (The "Case" Logic)
    if any(x in diag_type_key for x in ["ERD", "ENTITY RELATIONSHIP"]):
        extra_context = ERD_SPECIFIC_RULES
    elif "SEQUENCE" in diag_type_key:
        extra_context = SEQUENCE_RULES
    elif "CLASS" in diag_type_key:
        extra_context = CLASS_RULES
    elif "USE CASE" in diag_type_key or "USECASE" in diag_type_key:
        extra_context = USE_CASE_RULES
    elif "COMPONENT" in diag_type_key:
        extra_context = COMPONENT_RULES
    else:
        extra_context = "Generate a standard, clean PlantUML diagram."

    prompt = f"""
    Task: Generate a {diagram_type} in PlantUML.
    
    Critical Formatting Rules:
    {extra_context}
    
    User Requirements:
    {requirements}

    Constraint: Return ONLY raw PlantUML code. 
    NO markdown (```), NO introductory text. 
    Ensure code starts with @startuml and ends with @enduml.
    """
    
    messages = [
        {"role": "system", "content": "You are a software architect. You output ONLY valid, error-free PlantUML code without markdown decoration."},
        {"role": "user", "content": prompt}
    ]

    raw_response = get_chat_completion(messages)
    actual_response = clean_plantuml_code(raw_response)
    
    print(f"--- Final Code for {diagram_type} ---\n{actual_response}\n")
    return actual_response



