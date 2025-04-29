from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

zap_proxy = os.getenv("ZAP_PROXY")

driver = None
driver_lock = asyncio.Lock()

def create_driver():
    options = Options()
    options.headless = False
    options.add_argument("--proxy-bypass-list=<-loopback>")
    
    # Setup proxy if ZAP is configured
    if zap_proxy:
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = zap_proxy
        proxy.ssl_proxy = zap_proxy
        proxy.add_to_capabilities(options.to_capabilities())

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
