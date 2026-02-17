import openai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.llm.client import client, OPENAI_MODEL, PROMPT_VERSION
from app.llm.prompts import load_prompt
from app.llm.schemas import TicketLLMOutput

_RETRYABLE = (
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.RateLimitError,
    openai.InternalServerError,
)

@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.8, min=1, max=8),
    retry=retry_if_exception_type(_RETRYABLE),
)
def analyze_ticket(raw_text: str) -> tuple[TicketLLMOutput, str | None]:
    system = load_prompt(PROMPT_VERSION, "ticket_process_system.txt")

    # Structured Outputs: Responses APIで text_format に Pydantic model を渡す :contentReference[oaicite:4]{index=4}
    resp = client.responses.parse(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": raw_text},
        ],
        text_format=TicketLLMOutput,
    )

    parsed = resp.output_parsed
    if parsed is None:
        raise RuntimeError("No parsed output returned (possible refusal or formatting issue).")

    return parsed, getattr(resp, "_request_id", None)

