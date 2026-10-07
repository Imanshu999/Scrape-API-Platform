import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User,ScrapeCache
from ..schemas import ScrapeIn
from .auth import current_user
from ..scraper.engine import scrape
router=APIRouter(prefix="/scrape",tags=["scrape"])

@router.post("")
async def run(x:ScrapeIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    try: data=await scrape(str(x.url))
    except Exception as e: raise HTTPException(400,str(e))
    q=(await db.execute(select(ScrapeCache).where(ScrapeCache.url==str(x.url)))).scalar_one_or_none()
    if not q: q=ScrapeCache(url=str(x.url)); db.add(q)
    q.title=data.get("title"); q.description=data.get("description"); q.image=data.get("image"); q.data_json=json.dumps(data); q.updated_at=datetime.now(timezone.utc)
    await db.commit(); return data
