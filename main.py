from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from database import init_db, SessionLocal, get_settings, get_vk_settings, SavedPost
from services.parser import parse_url
from services.openrouter import generate_post
from services.vk import (
    get_auth_url, exchange_code, get_user_groups, post_to_wall,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="PostForge")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))


def render(name: str, **ctx):
    tpl = jinja_env.get_template(name)
    content = tpl.render(**ctx)
    return HTMLResponse(content)


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
    return render("index.html", request=request, model=settings.model)


@app.get("/archive", response_class=HTMLResponse)
async def archive_page(request: Request):
    return render("archive.html", request=request)


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    s = next(db_session())
    settings = get_settings(s)
    s.close()
    return render(
        "settings.html",
        request=request,
        api_key=settings.api_key,
        model=settings.model,
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


# --- VK API ---


@app.get("/api/vk/auth-url")
async def vk_auth_url():
    s = next(db_session())
    vk = get_vk_settings(s)
    s.close()
    if not vk.client_id:
        return JSONResponse({"error": "VK Client ID не настроен"}, status_code=400)
    url = await get_auth_url(vk.client_id)
    return {"url": url}


@app.post("/api/vk/callback")
async def vk_callback(request: Request):
    body = await request.json()
    code = body.get("code", "")
    s = next(db_session())
    vk = get_vk_settings(s)
    if not vk.client_id or not vk.client_secret:
        s.close()
        return JSONResponse({"error": "VK App не настроен"}, status_code=400)
    try:
        data = await exchange_code(code, vk.client_id, vk.client_secret)
        vk.access_token = data.get("access_token", "")
        exp = data.get("expires_in", 0)
        if exp and exp > 0:
            from datetime import timedelta
            vk.token_expires = datetime.now(timezone.utc) + timedelta(seconds=exp)
        s.commit()
    except Exception as e:
        s.close()
        return JSONResponse({"error": f"Ошибка получения токена: {str(e)}"}, status_code=400)
    s.close()
    return {"ok": True}


@app.get("/api/vk/groups")
async def vk_groups():
    s = next(db_session())
    vk = get_vk_settings(s)
    s.close()
    if not vk.access_token:
        return JSONResponse({"error": "VK не авторизован"}, status_code=401)
    try:
        groups = await get_user_groups(vk.access_token)
        return [{"id": g["id"], "name": g["name"]} if isinstance(g, dict) else g for g in groups]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/api/vk/post")
async def vk_post(request: Request):
    body = await request.json()
    owner_id = body.get("owner_id")
    message = body.get("message", "")
    link = body.get("link", "")
    if not owner_id or not message:
        return JSONResponse({"error": "owner_id и message обязательны"}, status_code=400)
    s = next(db_session())
    vk = get_vk_settings(s)
    s.close()
    if not vk.access_token:
        return JSONResponse({"error": "VK не авторизован"}, status_code=401)
    try:
        result = await post_to_wall(vk.access_token, owner_id, message, link)
        return {"ok": True, "post_id": result.get("post_id")}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/vk-callback", response_class=HTMLResponse)
async def vk_callback_page(request: Request):
    return render("vk_callback.html")

