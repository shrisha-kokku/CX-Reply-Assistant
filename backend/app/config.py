# Reads secrets from the .env file.
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")

# Frontend URLs allowed to call this API (comma separated). "*" = anyone.
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")