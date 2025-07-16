from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, RedirectResponse, PlainTextResponse, HTMLResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from models.requests import NavigateRequest, InputRequest, ClickRequest, LatitudeRequest
from services.selenium_service import get_driver
from services.orchestrator_service import orchestrate_scan
from services.zap_service import create_zap_report
from utils.utils import cookies_changed, get_html, close_all_popups
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import asyncio
import io
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH")

router = APIRouter()

def validate_selector(selector: str, context: str = "selector") -> None:
    """
    Validate that a selector is not a URL and appears to be a valid CSS selector or XPath.
    
    Args:
        selector: The selector string to validate
        context: Context for error messages (e.g., "selector", "CSS selector")
    
    Raises:
        HTTPException: If the selector appears to be invalid
    """
    # Check if it's a URL
    if selector.startswith(("http://", "https://", "ftp://", "file://", "www.")):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid {context}: URLs cannot be used as selectors. Received: {selector}"
        )
    
    # Check for common invalid characters that suggest it's not a proper selector
    if selector.strip() == "":
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {context}: Empty selector not allowed"
        )
    
    # Basic validation for CSS selector format (not exhaustive but catches obvious issues)
    if not selector.startswith("//"):  # Not XPath
        # Check for some obviously invalid CSS selector patterns
        invalid_patterns = [
            r"^\w+://",  # Protocol patterns
            r"^[^#.\[\]:\w\s>+~*-]",  # CSS selectors should start with valid characters
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, selector):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid CSS {context}: '{selector}' does not appear to be a valid CSS selector"
                )

@router.get("/mcp/sse", operation_id="redirect_sse")
async def redirect_sse():
    return RedirectResponse(url="/mcp")

@router.post("/navigate",
             operation_id="navigate")
async def navigate(request: NavigateRequest):
    """
    Navigate to a web page and extract its structure.
    
    This tool navigates to a specified URL using a web browser and extracts
    structured information about the page's interactive elements including
    links, input fields, buttons, and forms. It automatically closes any
    popups that might appear and waits for the page to fully load.
    
    Args:
        request: NavigateRequest containing the URL to navigate to
        
    Returns:
        dict: Contains success status and extracted elements:
            - success (bool): Whether navigation was successful
            - elements (dict): Structured data with links, inputs, buttons, forms
            
    Raises:
        HTTPException: 400 for invalid URL format, 500 for navigation errors
        
    Example:
        Navigate to "https://example.com" to analyze its structure
    """
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
        
        close_all_popups(driver, timeout=5)
        return {"success": True, "elements": summary}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/input_text",
             operation_id="input_text")
async def input_text(request: InputRequest):
    """
    Input text into a specific form field on the current web page.
    
    This tool finds an input field using a CSS selector and enters the specified
    text. It automatically clears any existing content before entering new text.
    The selector must target a valid input element that is visible and interactable.
    
    Args:
        request: InputRequest containing:
            - selector (str): CSS selector to locate the input field (e.g., "#username", "input[name='email']")
            - content (str): Text content to enter into the field
            
    Returns:
        dict: Contains success status
            - success (bool): Whether the text input was successful
            
    Raises:
        HTTPException: 
            - 400 for invalid selector format
            - 404 if element not found
            - 500 for interaction errors
            
    Example:
        Input "john@example.com" into selector "#email-field"
    """
    try:
        driver = get_driver()
        
        # Validate selector
        validate_selector(request.selector, "input selector")
        
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
    """
    Click on a specific element on the current web page.
    
    This tool finds and clicks on an element using either a CSS selector or XPath.
    It supports both regular clicks and login button clicks with special handling
    for authentication state detection. For login buttons, it monitors cookie
    changes and URL changes to determine if login was successful.
    
    Args:
        request: ClickRequest containing:
            - selector (str): CSS selector or XPath to locate the element
                            CSS examples: "#submit-btn", ".login-button", "button[type='submit']"
                            XPath examples: "//button[@id='login']", "//input[@value='Submit']"
            - isLogInButton (bool): Whether this is a login button requiring auth detection
            
    Returns:
        dict: Contains success status and login state if applicable:
            - success (bool): Whether the click was successful
            - isLogged (bool|None): Login status if isLogInButton=True, None otherwise
            
    Raises:
        HTTPException:
            - 400 for invalid selector format
            - 401 if login failed (for login buttons)
            - 404 if element not found or not clickable
            - 500 for interaction errors
            
    Example:
        Click login button: selector="//button[@type='submit']", isLogInButton=true
    """
    try:
        driver = get_driver()
        
        # Validate selector
        validate_selector(request.selector, "click selector")
        
        # Determinar si el selector es CSS o XPath
        by = By.XPATH if request.selector.strip().startswith("//") else By.CSS_SELECTOR

        print(f"Waiting for element with selector: {request.selector} (By: {by})")
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((by, request.selector))
            )
        except TimeoutException:
            raise HTTPException(status_code=404, detail=f"Element not found or not clickable: {request.selector}")

        is_logged = None
        if request.isLogInButton:
            cookies_before = driver.get_cookies()
            current_url = driver.current_url
            element.click()
            try:
                WebDriverWait(driver, 5).until(EC.url_changes(current_url))
                cookies_after = driver.get_cookies()
                is_logged = cookies_changed(cookies_before, cookies_after)
            except TimeoutException:
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
    """
    Start a comprehensive security scan of a web application.
    
    This tool initiates a complete DAST (Dynamic Application Security Testing) 
    scan that includes AI-powered login automation, intelligent web scraping,
    and vulnerability assessment using OWASP ZAP. The scan runs in the background
    and combines multiple security testing approaches.
    
    The scan process includes:
    1. AI-powered login using Latitude service
    2. Concurrent web crawling with ZAP spider and AI scraping
    3. Active vulnerability scanning with ZAP
    4. Report generation
    
    Args:
        request: LatitudeRequest containing:
            - url (str): Target web application URL to scan
            - username (str): Username for authentication
            - password (str): Password for authentication
            
    Returns:
        dict: Immediate response indicating scan initiation:
            - success (bool): Whether the scan was successfully started
            - message (str): Status message about background execution
            
    Raises:
        HTTPException: 500 if scan initialization fails
        
    Note:
        This is an asynchronous operation. Use /screenshot and /logs endpoints
        to monitor progress, and /report to get final results.
        
    Example:
        Start scan of "https://testapp.com" with credentials
    """
    try:
        asyncio.create_task(orchestrate_scan(request.url, request.username, request.password))
        return {"success": True, "message": "Scan started in background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/screenshot",
            operation_id="screenshot")
async def get_screenshot():
    """
    Get a real-time screenshot of the current browser state during scanning.
    
    This tool captures the current state of the web browser that is performing
    the security scan. It provides visual feedback about what the scanner is
    currently doing. When scanning is complete, it returns a JSON message
    instead of an image.
    
    Returns:
        Response: Either:
            - StreamingResponse with PNG image of current browser state
            - JSON message indicating scanning has finished
            
    Raises:
        HTTPException: 500 if screenshot capture fails
        
    Note:
        This endpoint is primarily used for monitoring scan progress.
        Call periodically during an active scan to see visual progress.
        
    Example:
        Monitor scanning progress by checking screenshot every few seconds
    """
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

@router.get("/logs", response_class=PlainTextResponse)
async def get_logs():
    """
    Retrieve detailed logs from the current or most recent security scan.
    
    This tool provides access to comprehensive logging information from the
    DAST scanning process, including details about navigation, authentication
    attempts, crawling progress, and any errors encountered during the scan.
    
    Returns:
        str: Plain text log content containing:
            - Timestamp entries for all scan activities
            - Authentication status and attempts
            - Crawling and spidering progress
            - Error messages and debugging information
            - Vulnerability detection progress
            
    Raises:
        HTTPException:
            - 404 if log file doesn't exist
            - 500 if unable to read log file
            
    Note:
        Logs are continuously updated during scanning. Check periodically
        for the latest information about scan progress and any issues.
        
    Example:
        Monitor scan progress and troubleshoot issues using log output
    """
    try:
        if not os.path.exists(LOG_FILE_PATH):
            raise HTTPException(status_code=404, detail="Log file not found")

        with open(LOG_FILE_PATH, "r", encoding='utf-8') as file:
            logs = file.read()
            # Log the contents to see what's inside
            print("File content:", repr(logs))

        return logs  # Return logs as plain text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")


@router.get("/report", response_class=HTMLResponse)
async def get_report():
    """
    Generate and retrieve the final security assessment report.
    
    This tool creates a comprehensive HTML report of all vulnerabilities and
    security issues discovered during the DAST scan. The report includes
    detailed findings from OWASP ZAP's analysis, risk ratings, and remediation
    recommendations.
    
    Returns:
        str: HTML-formatted security report containing:
            - Executive summary of findings
            - Detailed vulnerability descriptions
            - Risk severity ratings (High, Medium, Low)
            - Affected URLs and parameters
            - Remediation recommendations
            - Technical details for each finding
            
    Raises:
        HTTPException: 500 if report generation fails
        
    Note:
        This should only be called after a scan has completed.
        The report includes findings from all scanning phases.
        
    Example:
        Retrieve final security assessment report after scan completion
    """
    try:
        html_response = create_zap_report()
        return html_response  # Return the xml

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")
