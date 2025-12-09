# from langchain_core.tools import tool
# from pydantic import BaseModel, Field
# from notion_client import Client
# from ..utils.md_to_notion import parse_markdown_to_blocks
# import os, dotenv

# dotenv.load_dotenv()

# class NotionCreatePageInput(BaseModel):
#     """Input schema for creating a Notion page from markdown content."""
#     title: str = Field(..., description="Title of the page to create")
#     content: str = Field(..., description="Markdown content to save in the page")

# @tool("notion_create_page_langgraph", args_schema=NotionCreatePageInput)
# def notion_create_page_langgraph(title: str, content: str) -> str:
#     """
#     Creates a new page in a Notion database with the specified title and markdown content.

#     Args:
#         notion_token: Notion integration token
#         database_id: Notion database ID
#         title: Title of the page to create
#         content: Markdown content to save in the page
#     Returns:
#         Success or error message.
#     """
#     try:
#         token = os.getenv("NOTION_TOKEN")
#         database_id = os.getenv("NOTION_DB_ID")
#         notion = Client(auth=token)
#         blocks = parse_markdown_to_blocks(content)
#         first_chunk = blocks[:100]
#         page = notion.pages.create(
#             parent={"database_id": database_id},
#             properties={
#                 "Name":    {"title": [{"text": {"content": title}}]},
#                 "Type":    {"multi_select": [{"name": "Video"}]},
#                 "Status":  {"status": {"name": "research"}},
#                 # You may want to make Channels configurable if needed
#             },
#             children=first_chunk
#         )
#         # If there are more blocks, append them in batches
#         remaining = blocks[100:]
#         for i in range(0, len(remaining), 100):
#             batch = remaining[i : i + 100]
#             notion.blocks.children.append(
#                 block_id=page["id"],
#                 children=batch
#             )
#         return f"✅ Created page '{title}' with {len(blocks)} blocks"
#     except Exception as e:
#         return f"❌ Error creating Notion page: {e}" 