from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from routes import router
from services.selenium_service import selenium_driver
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Include routes from routes.py
app.include_router(router)

# Setup FastApiMCP
mcp = FastApiMCP(app, description="MCP Server for web scraping for cibersecurity")
mcp.mount()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
