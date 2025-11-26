import os
import sys
import random
import asyncio
from pyromod import listen
from pyrogram import Client
from pyromod import listen
from pytgcalls import idle

from config import API_ID, API_HASH, BOT_TOKEN
from bot import start_bot   # ← مهم جداً

# ─────────────────────────────
# تشغيل البوت الأساسي
# ─────────────────────────────

async def main():
    await start_bot()   # يبدأ البوت
    await idle()        # يخليه شغال على طول

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
