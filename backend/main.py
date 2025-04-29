from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router
from services.selenium_service import selenium_startup, selenium_shutdown
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

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

app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes from routes.py
app.include_router(router)

# Setup FastApiMCP
mcp = FastApiMCP(app, description="MCP Server for web scraping for cibersecurity")
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
