from modules.providers.gemini import generate_gemini_response
from modules.providers.openrouter import generate_openrouter_response


def generate_llm_response(
    prompt: str | None = None,
    model: str | None = None,
    *,
    prompt_name: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
) -> str:
    try:
        return generate_gemini_response(
            prompt,
            model=model,
            prompt_name=prompt_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            top_k=top_k,
        )
    except Exception as gemini_error:
        print(f"Gemini primary failed, falling back to OpenRouter: {gemini_error}")

    return generate_openrouter_response(
        prompt,
        model=None,
        prompt_name=prompt_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=top_p,
        top_k=top_k,
    )
