import json
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import ApiKey,ScrapeCache,Source
from ..security import key_hash

router=APIRouter(prefix="/v1",tags=["public-api"])

async def auth_key(x_api_key,db):
    if not x_api_key: raise HTTPException(401,"X-API-Key header required")
    k=(await db.execute(select(ApiKey).where(ApiKey.key_hash==key_hash(x_api_key),ApiKey.active==True))).scalar_one_or_none()
    if not k: raise HTTPException(401,"Invalid API key")
    return k

@router.get("/data")
async def data(url:str,x_api_key:str|None=Header(default=None),db:AsyncSession=Depends(get_db)):
    k=await auth_key(x_api_key,db)
    source=(await db.execute(select(Source).where(Source.url==url,Source.user_id==k.user_id))).scalar_one_or_none()
    if not source: raise HTTPException(404,"Source not found for this API key")
    item=(await db.execute(select(ScrapeCache).where(ScrapeCache.url==url))).scalar_one_or_none()
    if not item: raise HTTPException(404,"No cached data. Scrape the source first.")
    return json.loads(item.data_json)

@router.get("/data/{source_id}")
async def source_data(source_id:int,x_api_key:str|None=Header(default=None),db:AsyncSession=Depends(get_db)):
    k=await auth_key(x_api_key,db)
    s=await db.get(Source,source_id)
    if not s or s.user_id!=k.user_id: raise HTTPException(404,"Source not found for this API key")
    item=(await db.execute(select(ScrapeCache).where(ScrapeCache.url==s.url))).scalar_one_or_none()
    if not item: raise HTTPException(404,"Source has no cached data yet")
    return json.loads(item.data_json)
