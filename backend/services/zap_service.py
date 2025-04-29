from zapv2 import ZAPv2
from config.logs_config import setup_logger
import asyncio
import time
from dotenv import load_dotenv
import os

# Setup logger
logger = setup_logger()

# Load environment variables
load_dotenv()

apiKey = os.getenv("ZAP_API_KEY")

# Initialize ZAP API
zap = ZAPv2(apikey=apiKey)

async def run_zap_spider(target_url):
    logger.info("[*] Starting traditional Spider...")

    spider_id = zap.spider.scan(target_url)
    timeout = time.time() + 60  # 1 minuto de timeout
    while int(zap.spider.status(spider_id)) < 100:
        if time.time() > timeout:
            logger.warning("[!] Traditional Spider timeout reached (1 min).")
            break
        await asyncio.sleep(2)
    logger.info("[*] Spider completed or timed out.")

    logger.info("[*] Starting AJAX Spider...")
    zap.ajaxSpider.scan(target_url)
    timeout = time.time() + 60  # 1 minuto de timeout
    while True:
        status = zap.ajaxSpider.status
        if status == 'stopped':
            logger.info("[*] AJAX Spider completed!")
            break
        if time.time() > timeout:
            logger.warning("[!] AJAX Spider timeout reached (1 min).")
            break
        await asyncio.sleep(2)

async def run_zap_scan(target_url):
    logger.info("[*] Starting Active Scan...")
    active_scan_id = zap.ascan.scan(target_url)
    while int(zap.ascan.status(active_scan_id)) < 100:
        await asyncio.sleep(5)
    logger.info("[*] Active Scan completed!")

    logger.info("[*] Full scan completed successfully!")

    logger.info("[*] Creating report")
    report_xml = zap.core.xmlreport()
    with open('zap_report.xml', 'w') as f:
        f.write(report_xml)
    logger.info("[*] Report saved!")
