import json
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import ApiKey,ScrapeCache
from ..security import key_hash
router=APIRouter(prefix="/v1",tags=["public-api"])

@router.get("/data")
async def data(url:str,x_api_key:str|None=Header(default=None),db:AsyncSession=Depends(get_db)):
    if not x_api_key: raise HTTPException(401,"X-API-Key header required")
    k=(await db.execute(select(ApiKey).where(ApiKey.key_hash==key_hash(x_api_key),ApiKey.active==True))).scalar_one_or_none()
    if not k: raise HTTPException(401,"Invalid API key")
    item=(await db.execute(select(ScrapeCache).where(ScrapeCache.url==url))).scalar_one_or_none()
    if not item: raise HTTPException(404,"No cached data. Scrape the URL first.")
    return json.loads(item.data_json)
