import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MEDIA_ROOT = os.path.join(BASE_DIR, "media", "cbse12")

def validate_config():
    """Validates that the required configuration is present."""
    if not GEMINI_API_KEY:
        # We can also fall back to Google GenAI's default environment variables, 
        # but it's good to raise a warning or check.
        import warnings
        warnings.warn("GEMINI_API_KEY environment variable is not set. The Gemini API client might fail if default credentials are not configured.")
