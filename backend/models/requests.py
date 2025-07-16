from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated

class NavigateRequest(BaseModel):
    """Request model for navigating to a web page and extracting its structure."""
    
    url: Annotated[str, Field(
        description="The URL to navigate to. Must be a valid HTTP or HTTPS URL.",
        examples=["https://example.com", "http://localhost:3000", "https://testapp.com/login"],
        min_length=1
    )]

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com"
            }
        }

class InputRequest(BaseModel):
    """Request model for inputting text into form fields on a web page."""
    
    selector: Annotated[str, Field(
        description="CSS selector or XPath to locate the input field. Examples: '#username', 'input[name=\"email\"]', '//input[@type=\"password\"]'",
        examples=["#username", "input[name='email']", ".form-control", "//input[@type='password']"],
        min_length=1
    )]
    
    content: Annotated[str, Field(
        description="The text content to input into the field. Can be any string value.",
        examples=["john@example.com", "mypassword123", "John Doe", "+1234567890"]
    )]

    class Config:
        json_schema_extra = {
            "example": {
                "selector": "#email-field",
                "content": "user@example.com"
            }
        }

class ClickRequest(BaseModel):
    """Request model for clicking elements on a web page."""
    
    selector: Annotated[str, Field(
        description="CSS selector or XPath to locate the clickable element. Examples: '#submit-btn', 'button[type=\"submit\"]', '//a[@class=\"login-link\"]'",
        examples=["#submit-button", "button[type='submit']", ".btn-primary", "//button[@id='login']"],
        min_length=1
    )]
    
    isLogInButton: Annotated[bool, Field(
        default=False,
        description="Whether this element is a login button. If True, the system will monitor authentication state changes (cookies, URL changes) to determine if login was successful."
    )]

    class Config:
        json_schema_extra = {
            "example": {
                "selector": "//button[@type='submit']",
                "isLogInButton": True
            }
        }

class LatitudeRequest(BaseModel):
    """Request model for starting a comprehensive security scan with AI-powered automation."""
    
    url: Annotated[str, Field(
        description="The target web application URL to scan. Must be a valid HTTP or HTTPS URL.",
        examples=["https://testapp.com", "http://localhost:3000", "https://vulnerable-app.example.com"],
        min_length=1
    )]
    
    username: Annotated[str, Field(
        description="Username for authentication during the scan. Used by AI to automatically log into the application.",
        examples=["admin", "testuser", "john.doe@example.com"],
        min_length=1
    )]
    
    password: Annotated[str, Field(
        description="Password for authentication during the scan. Used by AI to automatically log into the application.",
        examples=["password123", "admin123", "secretpass"],
        min_length=1
    )]

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://vulnerable-app.com",
                "username": "testuser",
                "password": "testpass123"
            }
        }