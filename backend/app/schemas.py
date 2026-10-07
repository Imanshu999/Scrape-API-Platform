from pydantic import BaseModel, HttpUrl, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    password: str=Field(min_length=8,max_length=128)

class LoginIn(RegisterIn):
    pass

class ScrapeIn(BaseModel):
    url: HttpUrl
    max_pages: int=Field(default=25, ge=1, le=200)
    max_depth: int=Field(default=2, ge=0, le=5)
    render_js: bool=True

class SourceIn(BaseModel):
    url: HttpUrl
    max_pages: int=Field(default=25, ge=1, le=200)
    max_depth: int=Field(default=2, ge=0, le=5)
    refresh_minutes: int=Field(default=60, ge=5, le=10080)
    render_js: bool=True
