from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from .database import Base,engine,SessionLocal
from .routers import auth,scrape,public_api
from .models import Source
from .routers.scrape import run_source

app=FastAPI(title="Scrape API Platform",version="2.1.0",description="Authorized/public webpage extraction and API delivery platform.")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
app.include_router(auth.router); app.include_router(scrape.router); app.include_router(public_api.router)

scheduler=AsyncIOScheduler()

async def refresh_due_sources():
    async with SessionLocal() as db:
        rows=(await db.execute(select(Source).where(Source.active==True))).scalars().all()
        for source in rows:
            try:
                await run_source(db,source,render_js=True)
            except Exception as e:
                source.last_status="error"; source.last_error=str(e)
                await db.commit()

@app.on_event("startup")
async def startup():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
    scheduler.add_job(refresh_due_sources,"interval",minutes=5,id="source-refresh",replace_existing=True,max_instances=1)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown():
    if scheduler.running: scheduler.shutdown(wait=False)

@app.get("/health")
async def health():
    return {"status":"ok","service":"scrape-api-platform","version":"2.1.0","scheduler":scheduler.running}
