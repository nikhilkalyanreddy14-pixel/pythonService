import re
from App.kadalClient import get_chat_completion, run_gpt, run_gemini, run_claude
from App.Services.rules import ERD_SPECIFIC_RULES, SEQUENCE_RULES, CLASS_RULES, COMPONENT_RULES, DATABASE_CODE_RULES, API_CONTRACT_RULES, USE_CASE_RULES
from App.Services.prompts import getPromptMessage, getPromptDerivedArtifact

async def generate_derived_artifact(artifact_type: str, requirements: str, source_uml: str) -> str:
    diag_type_key = artifact_type.upper()
    
    if "DATABASE" in diag_type_key:
        extra_context = DATABASE_CODE_RULES
    else:
        extra_context = API_CONTRACT_RULES
    messages = getPromptDerivedArtifact(extra_context, source_uml, requirements)

    responseGot = await get_chat_completion(messages)
    return responseGot

def clean_plantuml_code(raw_code: str) -> str:
    if not raw_code: return ""
    cleaned = re.sub(r'```(?:plantuml|puml|text)?', '', raw_code)
    cleaned = cleaned.replace('```', '').strip()
    return cleaned

async def generate_diagram(diagram_type: str, requirements: str) -> str:
    diag_type_key = diagram_type.upper()

    CONTEXT_MAP = {
        ("ERD", "ENTITY RELATIONSHIP"): ERD_SPECIFIC_RULES,
        ("SEQUENCE",): SEQUENCE_RULES,
        ("CLASS",): CLASS_RULES,
        ("USE CASE", "USECASE"): USE_CASE_RULES,
        ("COMPONENT",): COMPONENT_RULES,
    }
    extra_context = "Generate a standard, clean PlantUML diagram."
    for keywords, context in CONTEXT_MAP.items():
        if any(key in diag_type_key for key in keywords):
            extra_context = context
            break
    
    messages = getPromptMessage(diagram_type, extra_context, requirements)
    raw_response = await run_gpt(messages)
    # raw_response = await run_gemini(messages)
    # raw_response = await run_claude(messages)
    # raw_response = await get_chat_completion(messages)
    actual_response = clean_plantuml_code(raw_response)
    return actual_response