from pyrogram import Client, idle
from config import API_ID, API_HASH, BOT_TOKEN
from pyromod import listen

# تعريف البوت
bot = Client(
    "JoyBoyIQ",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="Maker")
)

LOGGER_ID = 8457593460   # ← خليته ثابت فوق ومظبوط رقمياً

async def start_bot():
    print("[INFO]: STARTING BOT CLIENT")

    await bot.start()

    # ارسال رسالة للوج
    await bot.send_message(
        LOGGER_ID,
        "** تم تشفيل الصانع .**"
    )

    print("[INFO]: LOG MESSAGE SENT — BOT IS UP ✓")

    await idle()  # ← يخلي البوت شغال
