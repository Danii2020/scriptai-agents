from crewai.tools import BaseTool
from typing import Any, Type
from pydantic import BaseModel, Field
import os
import docx


class DocxReadToolInput(BaseModel):
    """Input schema for DocxReadTool."""
    file_path: str = Field(..., description="Path to the DOCX file to read")

class DocxReadTool(BaseTool):
    name: str = "docx_read_tool"
    description: str = (
        "A tool that reads a DOCX file and returns its text content."
    )
    args_schema: Type[BaseModel] = DocxReadToolInput
    class Config:
        extra = "allow"

    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        if file_path is not None:
            self.file_path = file_path
            self.description = f"A tool that reads the DOCX file at {file_path} and returns its text content."
            self.args_schema = DocxReadToolInput
            self._generate_description()

    def _run(self, **kwargs: Any) -> str:
        """
        Reads the specified DOCX file and returns its text content.
        """
        file_path = kwargs.get("file_path", self.file_path)
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        if not file_path.lower().endswith(".docx"):
            return f"Error: File {file_path} is not a DOCX file"
            
        try:
            doc = docx.Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            return f"Error reading DOCX file: {str(e)}"
