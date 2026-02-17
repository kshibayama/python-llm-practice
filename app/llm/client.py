import os
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06")
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "v1")

# SDK側にも max_retries / timeout がある（ここでは二重リトライを避けて0に）:contentReference[oaicite:3]{index=3}
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=20.0,
    max_retries=0,
)

