from latitude_sdk import Latitude, LatitudeOptions, RunPromptOptions
from dotenv import load_dotenv
import os

last_message_count = 0

# Load environment variables
load_dotenv()

sdk = Latitude(os.getenv("LATITUDE_API_KEY"), LatitudeOptions(project_id=int(os.getenv("LATITUDE_PROJECT_ID"))))

# Function Log In
async def start_latitude_login(url, username, password): 
    result = await sdk.prompts.run('LoginAgent', RunPromptOptions(
        version_uuid='b02c79f6-502a-4297-8318-3105c8757793',
        parameters={
            'url': url,
            'username': username,
            'password': password
        },
        # Enable streaming
        stream=True,
        # Provide callbacks for events
        on_finished=lambda result: print('Run completed:', result.uuid),
        on_error=lambda error: print('Run error:', error.message)
    ))
    return result

# Function Scrapper
async def start_latitude_scraping(url): 
    result = await sdk.prompts.run('ScrapingAgent', RunPromptOptions(
        version_uuid='b02c79f6-502a-4297-8318-3105c8757793',
        parameters={
            'url': url
        },
        # Enable streaming
        stream=True,
        # Provide callbacks for events
        on_finished=lambda result: print('Run completed:', result.uuid),
        on_error=lambda error: print('Run error:', error.message)
    ))
    return result
