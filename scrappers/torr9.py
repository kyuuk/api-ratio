import asyncio
import os
import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Page
from dotenv import load_dotenv

from util import default_user_agent

load_dotenv()
logger = logging.getLogger()

async def get_torr9_token(page: Page) -> Optional[str]:
    """Automated login to get a fresh Torr9 token if missing or expired"""
    user = os.getenv("TORR9_USER") or os.getenv("TOR9_USER")
    psw = os.getenv("TORR9_PASSWORD") or os.getenv("TORR9_PASS") or os.getenv("TOR9_PASS")
    
    if not (user and psw):
        logger.error("Torr9: Credentials (USER/PASSWORD) missing in .env file!")
        return None
    

    try:
        logger.info("Torr9: Attempting automated login...")
        await page.goto("https://torr9.net/login")
        await page.fill('input[placeholder*="utilisateur"]', user)
        await page.fill('input[placeholder*="mot de passe"]', psw)
        await asyncio.sleep(1)
        
        btn = await page.query_selector('button:has-text("Se connecter")')
        if btn:
            await btn.click()
        else:
            await page.keyboard.press("Enter")
        
        await page.wait_for_load_state("networkidle", timeout=15000)
        
        for _ in range(10):
            token = await page.evaluate("() => localStorage.getItem('token')")
            if token:
                with open("torr9_token.txt", "w") as f:
                    f.write(token)
                logger.info("Torr9: New token obtained and saved.")
                return token
            await asyncio.sleep(1)
        
        logger.error("Torr9: Login appeared successful but no token found in localStorage.")
    except Exception as e:
        logger.error(f"Torr9 Login failed: {e}")
    return None
  
async def get_stats(headless: bool = True) -> Dict[str, Any]:
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=headless)
    context = await browser.new_context(user_agent=default_user_agent)
    page = await context.new_page()
    try:
        res : Dict[str, Any] = {"ratio": "N/A", "upload": "N/A", "download": "N/A"}
        token = None
        if os.path.exists("torr9_token.txt"):
            with open("torr9_token.txt", "r") as f:
                token = f.read().strip()
        
        if not token:
            token = await get_torr9_token(page)
        
        if not token:
            return {"ratio": "No Token", "upload": "N/A", "download": "N/A"}
        
        response = await context.request.get(
            "https://api.torr9.net/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status == 401:
            logger.warning("Torr9: Token expired, refreshing...")
            token = await get_torr9_token(page)
            if token:
                response = await context.request.get(
                    "https://api.torr9.net/api/v1/users/me",
                    headers={"Authorization": f"Bearer {token}"}
                )
        
        if not response.ok:
            return {"ratio": f"API Error {response.status}", "upload": "N/A", "download": "N/A"}
        
        api_data = await response.json()
        up = api_data.get("total_uploaded_bytes", 0)
        dl = api_data.get("total_downloaded_bytes", 0)
        res["raw_upload"] = up
        res["raw_download"] = dl

        return res
    except Exception as e:
        logger.error(f"Error : {e}")
        return {"ratio": "Error", "upload": "N/A", "download": "N/A"}
    finally:
        await browser.close()