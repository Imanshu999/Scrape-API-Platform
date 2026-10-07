from urllib.parse import urlparse
import ipaddress, socket
import httpx
from bs4 import BeautifulSoup
from ..config import settings

def safe_url(url:str):
    p=urlparse(url)
    if p.scheme not in {"http","https"} or not p.hostname: raise ValueError("Only public HTTP(S) URLs are allowed")
    host=p.hostname.lower()
    if host in {"localhost","localhost.localdomain"}: raise ValueError("Local targets are blocked")
    try:
        infos=socket.getaddrinfo(host,None)
        for info in infos:
            ip=ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast: raise ValueError("Private or local targets are blocked")
    except socket.gaierror: pass
    return url

async def scrape(url:str):
    safe_url(url)
    async with httpx.AsyncClient(follow_redirects=True, timeout=settings.scrape_timeout_seconds, headers={"User-Agent":"ScrapeAPI/1.0"}) as client:
        r=await client.get(url)
        r.raise_for_status()
        if len(r.content)>settings.max_response_bytes: raise ValueError("Response is too large")
        soup=BeautifulSoup(r.text,"html.parser")
        title=(soup.title.string or "").strip() if soup.title else ""
        desc=(soup.find("meta",attrs={"name":"description"}) or {}).get("content","")
        og=soup.find("meta",attrs={"property":"og:image"})
        image=og.get("content") if og else None
        links=[]
        for a in soup.find_all("a",href=True)[:200]: links.append({"text":a.get_text(" ",strip=True),"url":a["href"]})
        return {"url":str(r.url),"title":title,"description":desc,"image":image,"links":links,"status_code":r.status_code}
