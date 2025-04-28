from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models.requests import NavigateRequest, InputRequest, ClickRequest, LatitudeRequest
from services.selenium_service import get_driver
from services.zap_service import run_zap_full_scan
from services.latitude_service import start_latitude
from utils.utils import cookies_changed, get_html
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import asyncio
import io

router = APIRouter()

@router.post("/navigate")
async def navigate(request: NavigateRequest):
    try:
        async with get_driver() as driver:
            driver.get(request.url)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'), request.url)
        return {"success": True, "elements": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/input_text")
async def input_text(request: InputRequest):
    try:
        async with get_driver() as driver:
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, request.selector))
            )
            element.clear()
            element.send_keys(request.content)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/click_element")
async def click_element(request: ClickRequest):
    try:
        async with get_driver() as driver:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, request.selector))
            )
            is_logged = None
            if request.isLogInButton:
                cookies_before = driver.get_cookies()
                element.click()
                WebDriverWait(driver, 15).until(EC.url_changes(driver.current_url))
                cookies_after = driver.get_cookies()
                is_logged = cookies_changed(cookies_before, cookies_after)
            else:
                element.click()
        return {"success": True, "isLogged": is_logged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute_scan")
async def execute_scan(request: NavigateRequest):
    try:
        asyncio.create_task(run_zap_full_scan(request.url))
        return {"success": True, "message": "Scan started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start_latitude")
async def execute_scan(request: LatitudeRequest):
    try:
        asyncio.create_task(start_latitude(request.url, request.username, request.password))
        return {"success": True, "message": "Scan started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/screenshot")
async def get_screenshot():
    try:
        driver = get_driver()  # get_driver() debe devolverte un driver ya levantado
        png = driver.get_screenshot_as_png()
        return StreamingResponse(io.BytesIO(png), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))