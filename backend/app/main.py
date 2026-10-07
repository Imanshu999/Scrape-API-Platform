from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base,engine
from .routers import auth,scrape,public_api
from .models import Source,ScrapeCache

app=FastAPI(title="Scrape API Platform",version="2.0.0",description="Authorized/public webpage extraction and API delivery platform.")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])
app.include_router(auth.router); app.include_router(scrape.router); app.include_router(public_api.router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status":"ok","service":"scrape-api-platform","version":"2.0.0"}
