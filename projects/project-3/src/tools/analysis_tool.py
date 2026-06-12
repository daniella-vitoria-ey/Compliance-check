from src.services.compliance_service import analyze_text

def analyze_document_tool(text: str, client_profile: str) -> dict:
    return analyze_text(text=text, client_profile=client_profile)