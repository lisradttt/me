import os
from os import getenv
from dotenv import load_dotenv

# استيراد بيانات المالك من ملف OWNER.py
from OWNER import (
    BOT_TOKEN,
    OWNER,
    OWNER_NAME,
    DATABASE,
    CHANNEL,
    GROUP,
    LOGS,
    VIDEO,
    bot_username,
    PHOTO
)

# تحميل env لو موجود
if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()

# قواعد تخزين بيانات البوت أثناء التشغيل
admins = {}
user = {}
call = {}
dev = {}
logger = {}
logger_mode = {}
botname = {}
appp = {}
helper = {}

# إعدادات أساسية
API_ID = int(getenv("API_ID", "14823185"))
API_HASH = getenv("API_HASH", "68493d4100bf829b3a84a43f0269bed6")

BOT_TOKEN = BOT_TOKEN
MONGO_DB_URL = DATABASE

OWNER = OWNER
OWNER_NAME = OWNER_NAME

CHANNEL = CHANNEL
GROUP = GROUP
LOGS = LOGS
PHOTO = PHOTO
bot_username = bot_username 
VIDEO = VIDEO
