# tiktok_live_bot.py
import asyncio
import os
from typing import List, Dict
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "30"))
TIKTOK_USERNAMES: List[str] = os.getenv("TIKTOK_USERNAMES", "username1,username2").split(",")

if not TELEGRAM_TOKEN or not CHAT_ID:
    raise SystemExit("Set TELEGRAM_TOKEN and CHAT_ID environment variables.")

bot = Bot(token=TELEGRAM_TOKEN)

async def check_user_live(page, username: str) -> bool:
    url = f"https://www.tiktok.com/@{username}"
    try:
        await page.goto(url, timeout=15000)
    except PlaywrightTimeoutError:
        return False

    try:
        live_el = await page.query_selector('text="LIVE"')
        if live_el:
            return True

        badge = await page.query_selector('[data-e2e="live-badge"], div:has-text("Live"), span:has-text("Live")')
        if badge:
            return True

        try:
            live_page = await page.goto(f"https://www.tiktok.com/@{username}/live", timeout=8000)
            if live_page and live_page.status == 200:
                html = await page.content()
                if "watching" in html.lower() or "live" in html.lower():
                    return True
        except Exception:
            pass

    except Exception:
        pass

    return False

async def monitor_loop(usernames: List[str], interval: int):
    known_live: Dict[str, bool] = {u: False for u in usernames}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context()
        page = await context.new_page()
        while True:
            for user in usernames:
                user = user.strip()
                if not user:
                    continue
                try:
                    is_live = await check_user_live(page, user)
                except Exception as e:
                    print(f"[ERROR] checking {user}: {e}")
                    is_live = False

                if is_live and not known_live.get(user, False):
                    known_live[user] = True
                    text = f"🔴 @{user} دابا فـ LIVE على TikTok!
https://www.tiktok.com/@{user}"
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=text)
                        print(f"Notified live: {user}")
                    except Exception as e:
                        print(f"Telegram send error: {e}")

                if not is_live and known_live.get(user, False):
                    known_live[user] = False
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=f"⚪ @{user} خرج من الـ LIVE.")
                    except Exception:
                        pass

                await asyncio.sleep(1)

            await asyncio.sleep(interval)

def main():
    usernames = [u.strip() for u in TIKTOK_USERNAMES if u.strip()]
    if not usernames:
        raise SystemExit("No usernames set in TIKTOK_USERNAMES.")
    print("Monitoring:", usernames)
    asyncio.run(monitor_loop(usernames, CHECK_INTERVAL_SECONDS))

if __name__ == "__main__":
    main()
