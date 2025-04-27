from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from contextlib import asynccontextmanager
from bs4 import BeautifulSoup
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi_mcp import FastApiMCP
from urllib.parse import urljoin
from zapv2 import ZAPv2
import asyncio
import logging

apiKey = 'e2q0nlun84j194hscevlrem7d0'
driver = None
driver_lock = asyncio.Lock()
logging.basicConfig(level=logging.INFO)

# Configurar ZAP como proxy
zap_proxy = 'localhost:8080'  # ZAP proxy por defecto

# Configurar el proxy en el navegador de Selenium
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = zap_proxy
proxy.ssl_proxy = zap_proxy

# Define the FastAPI app
app = FastAPI()

# Iniciar ZAP API
zap = ZAPv2(apikey=apiKey)

class NavigateRequest(BaseModel):
    url: str

class InputRequest(BaseModel):
    selector: str
    content: str

class ClickRequest(BaseModel):
    selector: str
    isLogInButton: bool = False

def get_html(soup, base_url):
    links = []
    inputs = []
    buttons = []
    forms = []

    for el in soup.find_all(["a", "input", "button", "form"]):
        if el.name == "a":
            href = el.get("href")
            text = el.get_text().strip()
            # Ensure the href is absolute
            if href:
                href = urljoin(base_url, href)  # Convert to absolute URL
            # Guardamos solo si tiene href y texto
            if href or text:
                links.append({
                    "href": href,
                    "text": text
                })

        elif el.name == "input":
            input_type = el.get("type")
            input_name = el.get("name")
            input_id = el.get("id")
            input_value = el.get("value")
            # Guardamos solo si tiene ID o NAME
            if input_id or input_name:
                inputs.append({
                    "type": input_type,
                    "name": input_name,
                    "id": input_id,
                    "value": input_value
                })

        elif el.name == "button":
            button_type = el.get("type")
            button_name = el.get("name")
            button_text = el.get_text().strip()
            # Guardamos solo si tiene texto o nombre
            if button_text or button_name:
                buttons.append({
                    "type": button_type,
                    "name": button_name,
                    "text": button_text
                })

        elif el.name == "form":
            form_action = el.get("action")
            form_method = el.get("method")
            form_fields = [input_el.get("name") for input_el in el.find_all("input") if input_el.get("name")]
            # Ensure the action is absolute
            if form_action:
                form_action = urljoin(base_url, form_action)  # Convert to absolute URL
            # Guardamos aunque no haya fields (algunos forms no tienen inputs directos)
            forms.append({
                "action": form_action,
                "method": form_method,
                "fields": form_fields
            })

    summary = {
        "links": links,
        "inputs": inputs,
        "buttons": buttons,
        "forms": forms
    }
    return summary

def cookies_changed(before, after):
    """Compares two cookie lists and returns True if they have changed."""
    # Convert the cookies to simpler dictionaries for comparison
    before_set = {cookie['name']: cookie['value'] for cookie in before}
    after_set = {cookie['name']: cookie['value'] for cookie in after}
    
    return before_set != after_set


# Startup and shutdown logic for the WebDriver
@asynccontextmanager
async def app_lifespan(app: FastAPI):  # Aceptar el argumento 'app'
    global driver
    # Startup
    options = Options()
    options.headless = False  # VISUAL MODE
    options.proxy = proxy  # Set the proxy
    options.add_argument("--proxy-bypass-list=<-loopback>") # Bypass localhost
    driver = webdriver.Chrome(options=options)
    try:
        yield
    finally:
        # Shutdown
        if driver:
            driver.quit()

# Asigna la función de lifespan a la app FastAPI
app = FastAPI(lifespan=app_lifespan)

@app.get("/mcp/sse",
          operation_id="redirect_sse")
async def redirect_sse():
    return RedirectResponse(url="/mcp")

@app.post("/navigate",
          operation_id="navigate")
async def navigate(request: NavigateRequest):
    "Navigate to a URL and extract elements like links, inputs, buttons, and forms from the page."
    try:
        async with driver_lock:
            driver.get(request.url)
            # wait for the page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # Extract elements
            summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'),request.url)

        return {"success": True, "elements": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/input_text",
          operation_id="input_text")
async def input_text(request: InputRequest):
    "Input text into an input field specified by the selector."
    try:
        async with driver_lock:
            # Wait for the element to be present and visible on the page
            element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, request.selector))
            )
            
            # Clear the input field and input the content
            element.clear()
            element.send_keys(request.content)
        
        return {"success": True}
    
    except Exception as e:
        # Raise an HTTP exception with a detailed error message
        raise HTTPException(status_code=500, detail=f"Error while inputting text: {str(e)}")

@app.post("/click_element",
          operation_id="click_element")
async def click_element(request: ClickRequest):
    "Click an element specified by the selector."
    try:
        async with driver_lock:
            # Find the element
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, request.selector))
            )
            
            is_logged = None

            if request.isLogInButton:
                # 1. Get cookies before clicking
                cookies_before = driver.get_cookies()

                # 2. Click the element
                element.click()

                # 3. Wait for login to finish processing
                WebDriverWait(driver, 15).until(
                    EC.url_changes(driver.current_url)  # Espera un cambio en la URL
                )

                # 4. Get cookies after clicking
                cookies_after = driver.get_cookies()

                # 5. Compare cookies
                is_logged = cookies_changed(cookies_before, cookies_after)

            else:
                # If it's not a login button, just click
                element.click()

        return {
            "success": True,
            "isLogged": is_logged 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/execute_scan", 
          operation_id="execute_scan")
async def execute_scan(request: NavigateRequest):
    "Execute a spider scan, then ajax scan, then active scan using ZAP API."
    try:
        asyncio.create_task(run_zap_full_scan(request.url))
        return {"success": True, "message": "Scan started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_zap_full_scan(target_url):
    logging.info("[*] Starting traditional Spider...")
    spider_id = zap.spider.scan(target_url)
    while int(zap.spider.status(spider_id)) < 100:
        await asyncio.sleep(2)
    logging.info("[*] Spider completed!")

    logging.info("[*] Starting AJAX Spider...")
    zap.ajaxSpider.scan(target_url)
    while zap.ajaxSpider.status == 'running':
        await asyncio.sleep(2)
    logging.info("[*] AJAX Spider completed!")

    logging.info("[*] Starting Active Scan...")
    active_scan_id = zap.ascan.scan(target_url)
    while int(zap.ascan.status(active_scan_id)) < 100:
        await asyncio.sleep(5)
    logging.info("[*] Active Scan completed!")

    logging.info("[*] Full scan completed successfully!")

mcp = FastApiMCP(app,
                description="MCP Server for web scraping for cibersecurity",
                describe_all_responses=False,
                describe_full_response_schema=False)

mcp.mount()


if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)