
import asyncio
from services.selenium_service import selenium_startup, selenium_shutdown
from services.latitude_service import start_latitude_login, start_latitude_scraping
from services.zap_service import run_zap_spider, run_zap_scan

# Funciton to orchestrate the scan
# This function will call the login function, then run the spider and AI scrapper concurrently, and finally run the ZAP scan.
async def orchestrate_scan(url: str, username: str, password: str):
    try:
        selenium_startup()  # Ensure the Selenium WebDriver is started

        # First call: Login
        login_result = await start_latitude_login(url, username, password)

        # Launch the spider and AI scrapper concurrently
        zap_task = asyncio.create_task(run_zap_spider(url))
        ai_scrapper_task = asyncio.create_task(start_latitude_scraping(url))

        # Wait for both tasks to complete
        zap_spider_result, ai_scrapper_result = await asyncio.gather(zap_task, ai_scrapper_task)

        selenium_shutdown()  # Ensure the Selenium WebDriver is shut down

        #Run active scan
        zap_results = await asyncio.create_task(run_zap_scan(url))

        # Return the results
        return {
            "success": True,
            "login_result": login_result,
            "ai_scrapper_result": ai_scrapper_result,
            "zap_spider_result": zap_spider_result,
            "zap_results": zap_results

        }

    except Exception as e:
        return {"success": False, "message": str(e)}
