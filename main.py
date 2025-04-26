from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from typing import List
from contextlib import asynccontextmanager
from bs4 import BeautifulSoup
from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from zapv2 import ZAPv2

driver = None

# Define the FastAPI app
app = FastAPI()

class NavigateRequest(BaseModel):
    url: str

class InputStep(BaseModel):
    selector: str
    content: str
    is_password_field: bool = False

class InputRequest(BaseModel):
    steps: List[InputStep]

class ClickRequest(BaseModel):
    selector: str

def get_html(soup):
    links = []
    inputs = []
    buttons = []
    forms = []

    for el in soup.find_all(["a", "input", "button", "form"]):
        if el.name == "a":
            href = el.get("href")
            text = el.get_text().strip()
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


# Startup and shutdown logic for the WebDriver
@asynccontextmanager
async def app_lifespan(app: FastAPI):  # Aceptar el argumento 'app'
    global driver
    # Startup
    options = Options()
    options.headless = False  # VISUAL MODE
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
        driver.get(request.url)
        # wait for the page to load
        driver.implicitly_wait(5)
        # Extract elements
        summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'))

        return {"success": True, "elements": summary}

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/input_text",
          operation_id="input_text")
async def input_text(request: InputRequest):
    "Input text into an input field specified by the selector."
    try:
        # Separar primero los que no son password y luego los que sí
        normal_inputs = [step for step in request.steps if not step.is_password_field]
        password_inputs = [step for step in request.steps if step.is_password_field]
        
        ordered_steps = normal_inputs + password_inputs

        for step in ordered_steps:
            element = driver.find_element(By.CSS_SELECTOR, step.selector)
            element.clear()
            element.send_keys(step.content)
            driver.implicitly_wait(5)

            if step.is_password_field:
                cookies_before = driver.get_cookies()
                element.send_keys(Keys.RETURN)
                driver.implicitly_wait(5)
                cookies_after = driver.get_cookies()
                if cookies_before != cookies_after:
                    return {"success": True, "isLogged": True, "cookies": cookies_after}
                else:
                    return {"success": True, "isLogged": False}
    
        return {"success": True, "isLogged": False}

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/click_element",
          operation_id="click_element")
async def click_element(request: ClickRequest):
    "Click an element specified by the selector."
    try:
        cookies_before = driver.get_cookies()
        element = driver.find_element(By.CSS_SELECTOR, request.selector)
        # wait for the page to load
        driver.implicitly_wait(5)
        #Obtain the new page source
        cookies_after = driver.get_cookies()
        # Check if the cookies have changed
        if cookies_before != cookies_after:
            # Extract elements
            summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'))
            # Return the new page source
            return {"success": True, "isLogged":True, "cookies": cookies_after}
        element.click()
        return {"success": True, "isLogged":False}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/get_cookies",
          operation_id="get_cookies")
async def get_cookies():
    "Retrieve the cookies stored by the WebDriver."
    try:
        cookies = driver.get_cookies()
        return {"success": True, "cookies": cookies}
    except Exception as e:
        return {"success": False, "error": str(e)}    

mcp = FastApiMCP(app,
                description="MCP Server for web scraping for cibersecurity",
                describe_all_responses=True,
                describe_full_response_schema=True)

mcp.mount()