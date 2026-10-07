import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User,ScrapeCache,Source
from ..schemas import ScrapeIn,SourceIn
from .auth import current_user
from ..scraper.engine import scrape

router=APIRouter(prefix="/scrape",tags=["scrape"])

async def run_source(db,source,render_js=True):
    data=await scrape(source.url,source.max_pages,source.max_depth,render_js)
    q=(await db.execute(select(ScrapeCache).where(ScrapeCache.url==source.url))).scalar_one_or_none()
    if not q: q=ScrapeCache(url=source.url); db.add(q)
    q.title=data.get("title"); q.description=data.get("description"); q.image=data.get("image")
    q.data_json=json.dumps(data); q.updated_at=datetime.now(timezone.utc)
    source.last_status="ok"; source.last_error=None; source.last_synced_at=datetime.now(timezone.utc)
    await db.commit()
    return data

@router.post("")
async def run(x:ScrapeIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    try:
        source=Source(user_id=u.id,url=str(x.url),max_pages=x.max_pages,max_depth=x.max_depth)
        data=await scrape(str(x.url),x.max_pages,x.max_depth,x.render_js)
        q=(await db.execute(select(ScrapeCache).where(ScrapeCache.url==str(x.url)))).scalar_one_or_none()
        if not q: q=ScrapeCache(url=str(x.url)); db.add(q)
        q.title=data.get("title"); q.description=data.get("description"); q.image=data.get("image")
        q.data_json=json.dumps(data); q.updated_at=datetime.now(timezone.utc)
        existing=(await db.execute(select(Source).where(Source.url==str(x.url)))).scalar_one_or_none()
        if not existing: db.add(source)
        await db.commit()
        return data
    except Exception as e:
        raise HTTPException(400,str(e))

@router.post("/sources")
async def add_source(x:SourceIn,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    existing=(await db.execute(select(Source).where(Source.url==str(x.url)))).scalar_one_or_none()
    if existing and existing.user_id!=u.id: raise HTTPException(409,"Source already belongs to another account")
    if not existing:
        existing=Source(user_id=u.id,url=str(x.url),max_pages=x.max_pages,max_depth=x.max_depth,refresh_minutes=x.refresh_minutes)
        db.add(existing); await db.commit(); await db.refresh(existing)
    return {"id":existing.id,"url":existing.url,"active":existing.active,"refresh_minutes":existing.refresh_minutes}

@router.get("/sources")
async def sources(u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(Source).where(Source.user_id==u.id).order_by(Source.id.desc()))).scalars().all()
    return [{"id":s.id,"url":s.url,"active":s.active,"status":s.last_status,"last_synced_at":s.last_synced_at,"error":s.last_error} for s in rows]

@router.post("/sources/{source_id}/refresh")
async def refresh(source_id:int,u:User=Depends(current_user),db:AsyncSession=Depends(get_db)):
    s=await db.get(Source,source_id)
    if not s or s.user_id!=u.id: raise HTTPException(404,"Source not found")
    try: return await run_source(db,s)
    except Exception as e:
        s.last_status="error"; s.last_error=str(e); await db.commit()
        raise HTTPException(400,str(e))
