import httpx
from app.core.config import settings

async def query(q):
    if settings.demo_mode: return None
    async with httpx.AsyncClient(timeout=8) as c:
        r=await c.get(f"{settings.prometheus_url}/api/v1/query",params={"query":q})
        r.raise_for_status()
        return r.json()
