from pydantic import BaseModel

class NavigateRequest(BaseModel):
    url: str

class InputRequest(BaseModel):
    selector: str
    content: str

class ClickRequest(BaseModel):
    selector: str
    isLogInButton: bool = False

class LatitudeRequest(BaseModel):
    url: str
    username: str
    password: str