# bot.py
import asyncio
from pyrogram import Client, idle
from pyromod import listen
from OWNER import API_ID, API_HASH, BOT_TOKEN

# Plugins
bot = Client(
    "mo",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Maker")  #  
)

#  
async def start_bot():
    print("[INFO]: STARTING BOT CLIENT")
    await bot.start()

    # ID   
    AFROTOO = 8457593460
    try:
        await bot.send_message(AFROTOO, "**Bot has started successfully!**")
        print("[INFO]: Message sent successfully to AFROTOO")
    except Exception as e:
        print(f"[ERROR]: Failed to send message to AFROTOO: {e}")

    #   
    await idle()