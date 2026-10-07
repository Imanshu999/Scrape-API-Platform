from pydantic import BaseModel, HttpUrl, EmailStr, Field
class RegisterIn(BaseModel): email: EmailStr; password: str=Field(min_length=8,max_length=128)
class LoginIn(RegisterIn): pass
class ScrapeIn(BaseModel): url: HttpUrl
