import os
from dotenv import load_dotenv

load_dotenv()

AI_MODEL = os.environ.get("MODEL", "gpt-4o-mini")