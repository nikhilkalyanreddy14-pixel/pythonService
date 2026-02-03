def getPromptMessage(diagramType:  str, extraContext: str, requirements: str):
    prompt = f"""
    Task: Generate a {diagramType} in PlantUML.
    
    Critical Formatting Rules:
    {extraContext}
    
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
    return messages

def getPromptDerivedArtifact(extraContext, sourceUML, requirements):
    prompt = f"""
    {extraContext}
    [Source PlantUML Code]:
    {sourceUML}
    [Original User Requirements]:
    {requirements}
    Constraint: Return ONLY the raw code/JSON. No markdown blocks.
    """
    messages = [
        {"role": "system", "content": "You are a technical architect specializing in code generation from UML."},
        {"role": "user", "content": prompt}
    ]
    return messages