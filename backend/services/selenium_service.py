from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import asyncio
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Setup ZAP Proxy
zap_proxy = os.getenv("ZAP_PROXY")  # ZAP proxy by default

# Configure the proxy for the Selenium browser
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = zap_proxy
proxy.ssl_proxy = zap_proxy

driver = None
driver_lock = asyncio.Lock()

def create_driver():
    # Start Selenium WebDriver
    options = Options()
    options.headless = False  # Visual mode
    options.proxy = proxy
    options.add_argument("--proxy-bypass-list=<-loopback>")  # Bypass localhost
    return webdriver.Chrome(options=options)

def selenium_startup():
    global driver
    if driver is None:
        driver = create_driver()
        
def selenium_shutdown():
    global driver
    if driver:
            driver.quit()
            driver = None
    
def get_driver():
    global driver
    if driver is None:
        driver = create_driver()
    return driver
