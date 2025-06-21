from langchain_core.tools import tool
from pydantic import BaseModel, Field
import os
import docx

class DocxReadInput(BaseModel):
    """Input schema for reading a DOCX file."""
    file_path: str = Field(..., description="Path to the DOCX file to read.")

@tool("docx_read_tool_langgraph", args_schema=DocxReadInput)
def docx_read_tool_langgraph(file_path: str) -> str:
    """
    Reads the specified DOCX file and returns its text content.

    Args:
        file_path: Path to the DOCX file to read.
    Returns:
        The text content of the DOCX file, or an error message if the file is missing or invalid.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    if not file_path.lower().endswith(".docx"):
        return f"Error: File {file_path} is not a DOCX file"
    try:
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"Error reading DOCX file: {str(e)}" 