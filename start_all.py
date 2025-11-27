#!/usr/bin/env python3
"""Unified startup module for JoyBoy Music Bot

Loads both Maker (صانع) and KERO (المصنوع) handlers in a single bot instance.
Uses in-memory storage to avoid database corruption issues.
"""

import asyncio
import sys
import traceback
import importlib
from pyrogram import Client
from pytgcalls import idle

from config import API_ID, API_HASH, BOT_TOKEN

# Create bot with in_memory=True to avoid SQLite storage issues
bot = Client(
    "JoyBoyIQ",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    in_memory=True,  # ← Avoid database corruption
    plugins=dict(root="plugins")
)


async def main():
    """Main entry point - starts bot and loads plugins"""
    try:
        print("[INFO] Starting unified client and loading plugins...")
        
        # Start the bot client - THIS LOADS PLUGINS
        await bot.start()
        print(f"[INFO] Bot started as @{bot.me.username}")
        print("[INFO] Client started. Plugins (Maker + KERO) should be loaded.")

        # Try to schedule Maker.auto_bot() to start all manufactured bots
        try:
            maker = importlib.import_module("Maker.KERO")
            if hasattr(maker, "auto_bot"):
                asyncio.create_task(maker.auto_bot())
                print("[INFO] Scheduled Maker.auto_bot() to start manufactured bots.")

                # Small reporting task: after a short delay, report how many manufactured
                # bots were registered into the runtime `appp` cache by Maker.
                async def _report_started():
                    await asyncio.sleep(5)
                    try:
                        from config import appp
                        started = len(appp)
                        print(f"[INFO] Manufactured bots started: {started}")
                        if started == 0:
                            print("[INFO] No manufactured bots found.\n"
                                  "Verify your MongoDB 'alli' collection contains bot entries\n"
                                  "or add a bot via the Maker 'صنع بوت' command.")
                    except Exception as e:
                        print(f"[WARNING] Could not report started bots: {e}")

                asyncio.create_task(_report_started())
            else:
                print("[INFO] Maker.KERO.auto_bot not found; skipping auto-start.")
        except Exception as e:
            print(f"[WARNING] Could not schedule Maker.auto_bot(): {e}")

        # Keep bot running
        await idle()
        
    except Exception as e:
        print(f"[ERROR] Failed to start bot: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            await bot.stop()
            print("[INFO] Bot stopped cleanly")
        except Exception as e:
            print(f"[WARNING] Error stopping bot: {e}")


if __name__ == "__main__":
    asyncio.run(main())
