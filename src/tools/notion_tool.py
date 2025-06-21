from crewai.tools import BaseTool
from typing import Any, Type
from pydantic import BaseModel, Field
from notion_client import Client
from ..utils.md_to_notion import parse_markdown_to_blocks
import os, math, dotenv

dotenv.load_dotenv()

class NotionToolInput(BaseModel):
    title: str = Field(..., description="Title of the page to create")
    content: str = Field(..., description="Markdown content to save in the page")

class NotionTool(BaseTool):
    name: str = "notion_tool"
    description: str = (
        "A tool that creates a new page in a Notion database with the specified title and markdown content."
    )
    args_schema: Type[BaseModel] = NotionToolInput
    class Config:
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("Set NOTION_TOKEN env var")
        self.notion = Client(auth=token)
        self.database_id = os.getenv("NOTION_DB_ID")

    def _run(self, title: str, content: str) -> str:
        blocks = parse_markdown_to_blocks(content)
        # first chunk (up to 100)
        first_chunk = blocks[:100]
        try:
            page = self.notion.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Name":    {"title": [{"text": {"content": title}}]},
                    "Type":    {"multi_select": [{"name": "Video"}]},
                    "Status":  {"status": {"name": "research"}},
                    "Channels":{"relation": [{"id": "1c8cee347a2181b2b55ee51aa66f9003"}]}
                },
                children=first_chunk
            )
            # if there are more blocks, append them in batches
            remaining = blocks[100:]
            if remaining:
                # Notion limits each append to 100 as well
                for i in range(0, len(remaining), 100):
                    batch = remaining[i : i + 100]
                    self.notion.blocks.children.append(
                        block_id=page["id"],
                        children=batch
                    )

            return f"✅ Created page '{title}' with {len(blocks)} blocks"
        except Exception as e:
            return f"❌ Error creating Notion page: {e}"
