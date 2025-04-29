from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from models.requests import NavigateRequest, InputRequest, ClickRequest, LatitudeRequest
from services.selenium_service import get_driver
from services.orchestrator_service import orchestrate_scan
from utils.utils import cookies_changed, get_html
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import asyncio
import io

router = APIRouter()

@router.get("/mcp/sse", operation_id="redirect_sse")
async def redirect_sse():
    return RedirectResponse(url="/mcp")

@router.post("/navigate",
             operation_id="navigate")
async def navigate(request: NavigateRequest):
    try:
        # Validate URL format
        parsed_url = urlparse(request.url)
        if not parsed_url.scheme in ["http", "https"] or not parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL format.")
        
        # Navigate to the URL
        driver = get_driver()
        driver.get(request.url)
        WebDriverWait(driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'), request.url)
        return {"success": True, "elements": summary}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/input_text",
             operation_id="input_text")
async def input_text(request: InputRequest):
    try:
        driver = get_driver()
        element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, request.selector))
        )
        element.clear()
        element.send_keys(request.content)
        return {"success": True}
    except TimeoutException:
        raise HTTPException(status_code=404, detail=f"Element not found with selector: {request.selector}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/click_element",
             operation_id="click_element")
async def click_element(request: ClickRequest):
    try:
        driver = get_driver()

        # Esperamos al botón (hasta 5 segundos)
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, request.selector))
            )
        except TimeoutException:
            raise HTTPException(status_code=404, detail=f"Element not found or not clickable: {request.selector}")

        is_logged = None
        if request.isLogInButton:
            cookies_before = driver.get_cookies()
            current_url = driver.current_url
            element.click()
            try:
                # Esperamos a que cambie la URL (indicativo de login exitoso)
                WebDriverWait(driver, 5).until(EC.url_changes(current_url))
                cookies_after = driver.get_cookies()
                is_logged = cookies_changed(cookies_before, cookies_after)
            except TimeoutException:
                # Click ocurrió pero no hubo login (ni cambio de URL)
                raise HTTPException(status_code=401, detail="Login failed: credentials likely invalid")
        else:
            element.click()
        return {"success": True, "isLogged": is_logged}
    except HTTPException as http_exc:
        raise http_exc  
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unhandled server error: {str(e)}")


@router.post("/start_latitude",
             operation_id="start_latitude")
async def execute_scan(request: LatitudeRequest):
    try:
        asyncio.create_task(orchestrate_scan(request.url, request.username, request.password))
        return {"success": True, "message": "Scan started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/screenshot",
            operation_id="screenshot")
async def get_screenshot():
    try:
        driver = get_driver()
        if driver is None:
            #Scraping finished
            return {"message": "Scraping finished. Now starting the ZAP scan..."}
        else:
            png = driver.get_screenshot_as_png()
            return StreamingResponse(io.BytesIO(png), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))