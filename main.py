from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from typing import List
from contextlib import asynccontextmanager
from bs4 import BeautifulSoup

driver = None

class NavigateRequest(BaseModel):
    url: str

class InputRequest(BaseModel):
    selector: str
    content: str

class ClickRequest(BaseModel):
    selector: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global driver
    options = Options()
    options.headless = False  # VISUAL MODE
    driver = webdriver.Chrome(options=options)
    yield
    # Shutdowns
    if driver:
        driver.quit()

app = FastAPI(lifespan=lifespan)
@app.post("/navigate", operation_id="navigate")
def navigate(request: NavigateRequest):
    """
    Navigate to a URL and extract elements like links, inputs, buttons, and forms from the page.
    """
    try:
        driver.get(request.url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        links = []
        inputs = []
        buttons = []
        forms = []

        for el in soup.find_all(["a", "input", "button", "form"]):
            if el.name == "a":
                links.append({"href": el.get("href"), "text": el.get_text().strip()})
            elif el.name == "input":
                inputs.append({
                    "type": el.get("type"),
                    "name": el.get("name"),
                    "id": el.get("id"),
                    "value": el.get("value")
                })
            elif el.name == "button":
                buttons.append({
                    "type": el.get("type"),
                    "name": el.get("name"),
                    "text": el.get_text().strip()
                })
            elif el.name == "form":
                forms.append({
                    "action": el.get("action"),
                    "method": el.get("method"),
                    "fields": [input_el.get("name") for input_el in el.find_all("input")]
                })

        summary = {
            "links": links,
            "inputs": inputs,
            "buttons": buttons,
            "forms": forms
        }

        return {"success": True, "elements": summary}

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/input", operation_id="input_text")
def input_text(request: InputRequest):
    """
    Input text into an input field specified by the selector.
    """
    try:
        element = driver.find_element(By.CSS_SELECTOR, request.selector)
        element.clear()
        element.send_keys(request.content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/click", operation_id="click_element")
def click_element(request: ClickRequest):
    """
    Click an element specified by the selector.
    """
    try:
        element = driver.find_element(By.CSS_SELECTOR, request.selector)
        element.click()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/cookies", operation_id="get_cookies")
def get_cookies():
    """
    Retrieve the cookies stored by the WebDriver.
    """
    try:
        cookies = driver.get_cookies()
        return {"success": True, "cookies": cookies}
    except Exception as e:
        return {"success": False, "error": str(e)}

mcp = FastApiMCP(app)
mcp.mount()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)