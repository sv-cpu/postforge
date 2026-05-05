import httpx
from bs4 import BeautifulSoup


async def parse_url(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "lxml")

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_desc = meta["content"].strip()
    if not meta_desc:
        meta = soup.find("meta", attrs={"property": "og:description"})
        if meta and meta.get("content"):
            meta_desc = meta["content"].strip()

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    body = soup.find("body")
    text = body.get_text(separator="\n", strip=True) if body else ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines[:200])

    return {
        "title": title,
        "description": meta_desc,
        "text": text,
    }
