
import asyncio
from services.latitude_service import start_latitude_login, start_latitude_scraping
from services.zap_service import run_zap_full_scan

# Funciton to orchestrate the scan
# This function will call the login function, then run the spider and AI scrapper concurrently, and finally run the ZAP scan.
async def orchestrate_scan(url: str, username: str, password: str):
    try:
        # First call: Login
        login_result = await start_latitude_login(url, username, password)

        # Launch the spider and AI scrapper concurrently
        zap_task = asyncio.create_task(run_zap_full_scan(url))
        ai_scrapper_task = asyncio.create_task(start_latitude_scraping(url))

        # Wait for both tasks to complete
        zap_result, ai_scrapper_result = await asyncio.gather(zap_task, ai_scrapper_task)

        # Return the results
        return {
            "success": True,
            "login_result": login_result,
            "ai_scrapper_result": ai_scrapper_result,
            "zap_result": zap_result
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
