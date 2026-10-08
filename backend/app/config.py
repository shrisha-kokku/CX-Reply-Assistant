# Reads settings from the .env file (see .env.example)
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")

# Frontend URLs allowed to call this API (comma separated). "*" = anyone, fine for the demo.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
