from urllib.parse import urljoin, urlparse, urldefrag
import asyncio, ipaddress, socket, json, re, xml.etree.ElementTree as ET
import httpx
from bs4 import BeautifulSoup
from ..config import settings

USER_AGENT="ScrapeAPI/2.0 (+authorized-public-data)"
BLOCKED_HOSTS={"localhost","localhost.localdomain"}

def validate_public_url(url:str):
    p=urlparse(url)
    if p.scheme not in {"http","https"} or not p.hostname:
        raise ValueError("Only public HTTP(S) URLs are allowed")
    host=p.hostname.lower()
    if host in BLOCKED_HOSTS:
        raise ValueError("Local targets are blocked")
    try:
        for info in socket.getaddrinfo(host,None):
            ip=ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                raise ValueError("Private or local targets are blocked")
    except socket.gaierror as e:
        raise ValueError("Hostname could not be resolved") from e
    return url

def clean_url(base, href):
    if not href or href.startswith(("#","mailto:","javascript:","tel:")):
        return None
    u=urldefrag(urljoin(base,href))[0]
    try: validate_public_url(u)
    except ValueError: return None
    return u

def same_origin(a,b):
    pa,pb=urlparse(a),urlparse(b)
    return pa.scheme==pb.scheme and pa.netloc.lower()==pb.netloc.lower()

def extract_page(url, html):
    soup=BeautifulSoup(html,"html.parser")
    title=(soup.title.get_text(" ",strip=True) if soup.title else "")
    desc=(soup.find("meta",attrs={"name":"description"}) or {}).get("content","")
    og=soup.find("meta",attrs={"property":"og:image"})
    image=urljoin(url,og.get("content")) if og and og.get("content") else None
    meta={}
    for m in soup.find_all("meta"):
        k=m.get("name") or m.get("property")
        v=m.get("content")
        if k and v: meta[k]=v
    links=[]
    for a in soup.find_all("a",href=True):
        u=clean_url(url,a["href"])
        if u: links.append({"text":a.get_text(" ",strip=True)[:300],"url":u})
    images=[]
    for tag in soup.find_all(["img","source"]):
        src=tag.get("src") or tag.get("srcset","").split(",")[0].strip().split(" ")[0]
        u=clean_url(url,src) if src else None
        if u: images.append({"url":u,"alt":tag.get("alt","")})
    jsonld=[]
    for s in soup.find_all("script",type="application/ld+json"):
        try: jsonld.append(json.loads(s.string or s.get_text()))
        except Exception: pass
    text=re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
    return {
        "url":url,"title":title,"description":desc,"image":image,
        "meta":meta,"json_ld":jsonld,"links":links[:500],"images":images[:500],
        "text":text[:100000]
    }

async def fetch_html(client,url,render_js=False):
    validate_public_url(url)
    if render_js:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser=await p.chromium.launch(headless=True)
                page=await browser.new_page(user_agent=USER_AGENT)
                await page.goto(url,wait_until="domcontentloaded",timeout=settings.scrape_timeout_seconds*1000)
                html=await page.content()
                final=str(page.url)
                await browser.close()
                validate_public_url(final)
                return final,html
        except Exception:
            pass
    r=await client.get(url)
    r.raise_for_status()
    final=str(r.url)
    validate_public_url(final)
    if len(r.content)>settings.max_response_bytes:
        raise ValueError("Response is too large")
    return final,r.text

async def discover_sitemap(client,root):
    for path in ("/sitemap.xml","/sitemap_index.xml"):
        u=urljoin(root,path)
        try:
            r=await client.get(u); 
            if r.status_code>=400: continue
            root_xml=ET.fromstring(r.text)
            urls=[x.text for x in root_xml.iter() if x.tag.lower().endswith("loc") and x.text]
            return [u for u in urls if same_origin(root,u)][:500]
        except Exception: pass
    return []

async def scrape(url:str,max_pages=25,max_depth=2,render_js=True):
    root=validate_public_url(url)
    seen=set(); queue=[(root,0)]; pages=[]; sitemap=[]
    async with httpx.AsyncClient(follow_redirects=False,timeout=settings.scrape_timeout_seconds,headers={"User-Agent":USER_AGENT}) as client:
        sitemap=await discover_sitemap(client,root)
        for u in sitemap[:max_pages]:
            queue.append((u,0))
        while queue and len(pages)<max_pages:
            current,depth=queue.pop(0)
            if current in seen or depth>max_depth: continue
            seen.add(current)
            try:
                final,html=await fetch_html(client,current,render_js=render_js)
                if not same_origin(root,final): continue
                item=extract_page(final,html)
                item["depth"]=depth
                pages.append(item)
                if depth<max_depth:
                    for link in item["links"]:
                        if same_origin(root,link["url"]) and link["url"] not in seen:
                            queue.append((link["url"],depth+1))
            except Exception as e:
                pages.append({"url":current,"depth":depth,"error":str(e)})
    first=next((p for p in pages if "error" not in p),pages[0] if pages else {})
    return {
        "source":root,"page_count":len(pages),"pages":pages,
        "title":first.get("title",""),"description":first.get("description",""),
        "image":first.get("image"),"sitemap_urls":sitemap[:500]
    }
