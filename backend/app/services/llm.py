# Talks to the LLM through OpenRouter. Nothing else in the project knows about OpenRouter.
import json
import re

import requests

from app import config

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class LLMError(Exception):
    """Raised when the AI call fails (timeout, bad key, rate limit...)."""


def call_llm(system_prompt, user_prompt):
    """Sends the prompts, returns the model's text."""
    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {config.OPENROUTER_API_KEY}"},
            json={
                "model": config.OPENROUTER_MODEL,
                "temperature": 0.2,  # low = stick to the facts
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            },
            timeout=40,
        )
        if response.status_code != 200:
            raise LLMError(f"{response.status_code}: {response.text}")
        return response.json()["choices"][0]["message"]["content"]
    except LLMError:
        raise
    except Exception as e:
        raise LLMError(str(e))


def parse_json(text):
    """Models sometimes add text or ``` around the JSON, so grab the first {...} block."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
