# main.py
import asyncio
from bot import start_bot  # استيراد الدالة من bot.py

async def main():
    await start_bot()  # تشغيل البوت

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())