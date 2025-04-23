from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from typing import List
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

driver = None

class NavigateRequest(BaseModel):
    url: str

class InputRequest(BaseModel):
    selector: str
    content: str

class ClickRequest(BaseModel):
    selector: str

# Create a named server
mcp = FastMCP("input_mcp")

@asynccontextmanager
async def app_lifespan(server: FastMCP):
    global driver
    # Startup
    options = Options()
    options.headless = False  # VISUAL MODE
    driver = webdriver.Chrome(options=options)
    try:
        yield
    finally:
        # Shutdowns
        if driver:
            driver.quit()

# Pass lifespan to server
mcp = FastMCP("input_mcp", lifespan=app_lifespan)

@mcp.tool()
def navigate(request: NavigateRequest):
    "Navigate to a URL and extract elements like links, inputs, buttons, and forms from the page."
    try:
        driver.get(request.url)

        # Extract elements
        summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'))

        return {"success": True, "elements": summary}

    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def input_text(request: InputRequest):
    "Input text into an input field specified by the selector."
    try:
        # Find the input field and clear it
        element = driver.find_element(By.CSS_SELECTOR, request.selector)
        element.clear()
        # Input the text
        element.send_keys(request.content)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def submit_login(request: ClickRequest):
    "Submit a login form by press enter or clicking the submit button"
    try:
        # Obtain the html
        pre_summary = get_html(BeautifulSoup(driver.page_source, 'html.parser'))

        # Find the input field and clear it
        element.send_keys(Keys.RETURN)

        # Wait for the page to load
        driver.implicitly_wait(10)  # Wait for 10 seconds

        # Obtain the html again
        post_sumarry = get_html(BeautifulSoup(driver.page_source, 'html.parser'))

        # Check if the page has changed
        if pre_summary == post_sumarry:
            # Find the input field and submit button
            element = driver.find_element(By.CSS_SELECTOR, request.selector)
            element.click()
            
            # Obtain the html again
            post_sumarry = get_html(BeautifulSoup(driver.page_source, 'html.parser'))
            if pre_summary == post_sumarry:
                return {"success": False, "error": "Login failed"}
            return {"success": True}
        else:
            return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def click_element(request: ClickRequest):
    "Click an element specified by the selector."
    try:
        element = driver.find_element(By.CSS_SELECTOR, request.selector)
        element.click()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_cookies():
    "Retrieve the cookies stored by the WebDriver."
    try:
        cookies = driver.get_cookies()
        return {"success": True, "cookies": cookies}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_html(soup):
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
    return summary 

if __name__ == "__main__":
    mcp.run()