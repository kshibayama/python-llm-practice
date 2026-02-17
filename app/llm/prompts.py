from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"

def load_prompt(prompt_version: str, filename: str) -> str:
    path = PROMPTS_DIR / prompt_version / filename
    return path.read_text(encoding="utf-8")

