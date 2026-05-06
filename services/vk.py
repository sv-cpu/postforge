import httpx


VK_API = "https://api.vk.com/method"


VK_CALLBACK = "https://postforge-1ksf.onrender.com/vk-callback"

async def get_auth_url(client_id: str) -> str:
    scopes = "wall,groups,offline"
    return (
        f"https://oauth.vk.com/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect}&"
        f"scope={scopes}&"
        f"response_type=code&"
        f"v=5.199"
    )


async def exchange_code(code: str, client_id: str, client_secret: str) -> dict:
    url = (
        f"https://oauth.vk.com/access_token?"
        f"client_id={client_id}&"
        f"client_secret={client_secret}&"
        f"redirect_uri={VK_CALLBACK}&"
        f"code={code}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def get_user_groups(token: str) -> list:
    url = f"{VK_API}/groups.get"
    params = {
        "access_token": token,
        "v": "5.199",
        "filter": "editor",
        "extended": 1,
        "fields": "name",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        if "error" in data:
            raise Exception(data["error"].get("error_msg", "VK API error"))
        return data.get("response", {}).get("items", [])


async def post_to_wall(token: str, owner_id: int, message: str, link: str = "") -> dict:
    url = f"{VK_API}/wall.post"
    params = {
        "access_token": token,
        "v": "5.199",
        "owner_id": owner_id,
        "message": message,
        "attachments": link if link else "",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=params)
        data = resp.json()
        if "error" in data:
            raise Exception(data["error"].get("error_msg", "VK API error"))
        return data.get("response", {})
