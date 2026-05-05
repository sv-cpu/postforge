from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db, SessionLocal, get_settings, SavedPost
from services.parser import parse_url
from services.openrouter import generate_post

app = FastAPI(title="PostForge")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def db_session():
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()


@app.on_event("startup")
def startup():
    init_db()


# --- Pages ---


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    s = next(db_session())
    settings = get_settings(s)
    s.close()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "model": settings.model},
    )


@app.get("/archive", response_class=HTMLResponse)
async def archive_page(request: Request):
    return templates.TemplateResponse("archive.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    s = next(db_session())
    settings = get_settings(s)
    s.close()
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "api_key": settings.api_key, "model": settings.model},
    )


# --- API ---


@app.post("/api/generate")
async def api_generate(request: Request):
    body = await request.json()
    url = body.get("url", "").strip()
    tone = body.get("tone", "friendly")
    model = body.get("model", "")

    if not url:
        return JSONResponse({"error": "URL обязателен"}, status_code=400)

    s = next(db_session())
    settings = get_settings(s)
    api_key = settings.api_key
    default_model = settings.model
    s.close()

    if not api_key:
        return JSONResponse({"error": "API ключ не настроен"}, status_code=400)

    model = model or default_model or "openai/gpt-4o-mini"

    try:
        page_content = await parse_url(url)
    except Exception as e:
        return JSONResponse({"error": f"Ошибка парсинга URL: {str(e)}"}, status_code=400)

    try:
        post = await generate_post(api_key, page_content, tone, model)
    except Exception as e:
        return JSONResponse({"error": f"Ошибка генерации: {str(e)}"}, status_code=500)

    return {"content": post, "title": page_content.get("title", "")}


@app.get("/api/archive")
async def api_archive_list():
    s = next(db_session())
    posts = s.query(SavedPost).order_by(SavedPost.created_at.desc()).all()
    s.close()
    return [
        {
            "id": p.id,
            "original_url": p.original_url,
            "tone": p.tone,
            "model": p.model,
            "content": p.content,
            "created_at": p.created_at.isoformat() if p.created_at else "",
        }
        for p in posts
    ]


@app.post("/api/archive")
async def api_archive_save(request: Request):
    body = await request.json()
    s = next(db_session())
    post = SavedPost(
        original_url=body.get("original_url", ""),
        tone=body.get("tone", "friendly"),
        model=body.get("model", ""),
        content=body.get("content", ""),
        created_at=datetime.now(timezone.utc),
    )
    s.add(post)
    s.commit()
    post_id = post.id
    s.close()
    return {"id": post_id}


@app.delete("/api/archive/{post_id}")
async def api_archive_delete(post_id: int):
    s = next(db_session())
    post = s.get(SavedPost, post_id)
    if not post:
        s.close()
        return JSONResponse({"error": "Пост не найден"}, status_code=404)
    s.delete(post)
    s.commit()
    s.close()
    return {"ok": True}


@app.get("/api/settings")
async def api_settings_get():
    s = next(db_session())
    settings = get_settings(s)
    s.close()
    return {"api_key": settings.api_key, "model": settings.model}


@app.put("/api/settings")
async def api_settings_update(request: Request):
    body = await request.json()
    s = next(db_session())
    settings = get_settings(s)
    if "api_key" in body:
        settings.api_key = body["api_key"]
    if "model" in body:
        settings.model = body["model"]
    s.commit()
    s.close()
    return {"ok": True}
