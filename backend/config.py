import os

from dotenv import load_dotenv


load_dotenv()


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")


if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is not set")