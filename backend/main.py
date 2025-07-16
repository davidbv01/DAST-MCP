from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router
from services.selenium_service import selenium_startup, selenium_shutdown
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)

# Startup and shutdown logic for the WebDriver
@asynccontextmanager
async def app_lifespan(app: FastAPI):  # Aceptar el argumento 'app'
    # Startup
    try:
        #selenium_startup()
        yield
    finally:
        # Shutdown
        selenium_shutdown()

app = FastAPI(
    title="DAST Security Scanner API",
    description="Dynamic Application Security Testing (DAST) API with AI-powered web automation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=app_lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from routes.py
app.include_router(router)

# Setup FastApiMCP with enhanced configuration
mcp = FastApiMCP(
    app, 
    name="DAST Security Scanner",
    description="""
    MCP Server for Dynamic Application Security Testing (DAST) with AI-powered automation.
    
    This server provides tools for:
    • Web application navigation and analysis
    • Automated form interaction and input
    • AI-powered authentication and login
    • Comprehensive security vulnerability scanning
    • Real-time scan monitoring with screenshots
    • Detailed security reporting
    
    Built with OWASP ZAP, Selenium WebDriver, and Latitude AI services.
    Perfect for security testing, penetration testing, and automated vulnerability assessment.
    """
)
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
