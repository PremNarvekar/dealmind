"""
Configuration — loads and validates all required environment variables.

Security rules enforced here:
- Variables are only read from the environment (via .env or real env).
- No secrets are ever printed or logged.
- Missing required variables fail fast with a clear message at startup.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Look for .env in backend/ first, then in the project root (parent of backend/)
_backend_dir = Path(__file__).resolve().parent
load_dotenv(_backend_dir / ".env")              # backend/.env (if exists)
load_dotenv(_backend_dir.parent / ".env")        # dealmind/.env (project root)

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "")

# ── Gemini model to use across all agents ───────────────────────────────────
# Use an env var so it can be changed without code changes.
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ── Validation — fail fast so the problem is obvious at startup ─────────────
_missing: list[str] = []

if not GOOGLE_API_KEY:
    _missing.append("GOOGLE_API_KEY")
if not TAVILY_API_KEY:
    _missing.append("TAVILY_API_KEY")

if _missing:
    raise ValueError(
        f"Missing required environment variables: {', '.join(_missing)}. "
        "Set them in your .env file or environment."
    )