import httpx

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"

TONE_PROMPTS = {
    "expert": (
        "Ты — экспертный копирайтер. Напиши пост для Telegram/LinkedIn на русском языке "
        "на основе предоставленного контента. Используй профессиональную лексику, "
        "глубокий анализ, подкрепляй фактами. Объем: 3-5 абзацев. "
        "Пост должен выглядеть как готовый к публикации текст."
    ),
    "friendly": (
        "Ты — дружелюбный копирайтер. Напиши легкий, увлекательный пост для соцсетей "
        "на русском языке. Общайся с читателем на 'ты', используй простые слова, "
        "добавь вовлекающий вопрос в конце. Объем: 3-4 абзаца."
    ),
    "brief": (
        "Ты — копирайтер. Напиши очень краткий пост на русском языке (2-3 предложения). "
        "Только суть, без воды."
    ),
}

DEFAULT_MODEL = "openai/gpt-4o-mini"


async def generate_post(
    api_key: str,
    page_content: dict,
    tone: str = "friendly",
    model: str = DEFAULT_MODEL,
) -> str:
    system_prompt = TONE_PROMPTS.get(tone, TONE_PROMPTS["friendly"])

    user_content = (
        f"Заголовок страницы: {page_content.get('title', '')}\n\n"
        f"Описание: {page_content.get('description', '')}\n\n"
        f"Содержимое:\n{page_content.get('text', '')}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "PostForge",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(OPENROUTER_API, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
