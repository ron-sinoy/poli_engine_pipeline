from modules.providers import generate_llm_response


def llm_node(
    prompt: str | None = None,
    model: str | None = None,
    *,
    prompt_name: str | None = None,
    temperature: float | None = None,
    max_output_tokens: int | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
) -> str:
    return generate_llm_response(
        prompt,
        model=model,
        prompt_name=prompt_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=top_p,
        top_k=top_k,
    )
