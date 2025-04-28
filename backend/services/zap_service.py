from zapv2 import ZAPv2
import logging
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

apiKey = os.getenv("ZAP_API_KEY")

# Initialize ZAP API
zap = ZAPv2(apikey=apiKey)

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

    logging.info("[*] Creating report")
    report_xml = zap.core.xmlreport()
    with open('zap_report.xml', 'w') as f:
        f.write(report_xml)
    logging.info("[*] Report saved!")