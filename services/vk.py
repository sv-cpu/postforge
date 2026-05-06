import httpx


VK_API = "https://api.vk.com/method"


async def get_user_groups(api_key: str) -> list:
    url = f"{VK_API}/groups.get"
    params = {
        "access_token": api_key,
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


async def post_to_wall(api_key: str, owner_id: int, message: str, link: str = "") -> dict:
    url = f"{VK_API}/wall.post"
    params = {
        "access_token": api_key,
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
