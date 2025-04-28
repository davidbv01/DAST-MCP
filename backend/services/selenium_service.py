from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import asyncio
import logging
from contextlib import asynccontextmanager
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

@asynccontextmanager
async def selenium_driver():
    global driver
    # Start Selenium WebDriver
    options = Options()
    options.headless = False  # Visual mode
    options.proxy = proxy
    options.add_argument("--proxy-bypass-list=<-loopback>")  # Bypass localhost
    driver = webdriver.Chrome(options=options)
    try:
        yield driver
    finally:
        if driver:
            driver.quit()
