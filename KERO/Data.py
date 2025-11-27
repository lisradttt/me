from config import API_ID, API_HASH, MONGO_DB_URL, user, dev, call, logger, logger_mode, botname, GROUP as GROUPOWNER, CHANNEL as CHANNELOWNER, OWNER, OWNER_NAME
from pymongo import MongoClient
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_

# Mongo connection
mo = MongoClient(MONGO_DB_URL)
moo = mo["data"]

# Collections
Bots = moo.alli
bot_name = moo.bot_name
channeldb = moo.ch
groupdb = moo.gr
channeldbsr = moo.chsr
groupdbsr = moo.grsr
mustdb = moo.must

# Caches
CHANNEL = {}
CHANNELsr = {}
GROUP = {}
GROUPsr = {}
dev_cache = {}
devname = {}
botss = Bots
must = {}
boot = {}

def dbb():
    global db
    db = {}

dbb()

# ───────────────────────────────
# Developer Id
# ───────────────────────────────
async def get_dev(bot_username: str):
    if bot_username in dev_cache:
        return dev_cache[bot_username]

    bot = botss.find_one({"bot_username": bot_username})
    if bot:
        dev_cache[bot_username] = bot["dev"]
        return bot["dev"]

    return None

# ───────────────────────────────
# Video Source Cache
# ───────────────────────────────
videosource = {}

# ───────────────────────────────
# Set Video Source (Logo)
# ───────────────────────────────
async def set_video_source(bot_username: str, link: str):
    # تحديث الكاش
    videosource[bot_username] = link

    # تحديث MongoDB
    botss.update_one(
        {"bot_username": bot_username},
        {"$set": {"video_source": link}},
        upsert=True
    )
    return True


# ───────────────────────────────
# Get Video Source (Logo)
# ───────────────────────────────
async def get_video_source(bot_username: str):
    # لو موجود في الكاش
    if bot_username in videosource:
        return videosource[bot_username]

    # البحث في قاعدة البيانات
    bot = botss.find_one({"bot_username": bot_username})
    if bot and "video_source" in bot:
        videosource[bot_username] = bot["video_source"]
        return bot["video_source"]

    return None


# ───────────────────────────────
# Developer Name
# ───────────────────────────────
async def get_dev_name(client, bot_username: str):
    if bot_username in devname:
        return devname[bot_username]

    bot = botss.find_one({"bot_username": bot_username})
    if bot:
        try:
            developer = await client.get_chat(bot["dev"])
            name = developer.first_name
            devname[bot_username] = name
            return name
        except Exception as e:
            print(f"Error getting dev name: {e}")
            return "المطور"

    return "المطور"


# ───────────────────────────────
# Developer Username
# ───────────────────────────────
async def get_dev_username(client, bot_username: str):
    # البحث في قاعدة البيانات
    bot = botss.find_one({"bot_username": bot_username})
    if bot:
        try:
            developer = await client.get_chat(bot["dev"])
            username = developer.username if developer.username else developer.first_name
            return username
        except Exception as e:
            print(f"Error getting dev username: {e}")
            return None

    return None

# Alias for compatibility with start.py
get_dev_user = get_dev_username

# ───────────────────────────────
# Set Developer User
# ───────────────────────────────
async def set_dev_user(bot_username: str, dev_id: int):
    """Set the developer ID for a bot"""
    botss.update_one(
        {"bot_username": bot_username},
        {"$set": {"dev": dev_id}},
        upsert=True
    )
    # Clear dev cache to force refresh
    if bot_username in dev_cache:
        del dev_cache[bot_username]
    return True

# ───────────────────────────────
# Bot Name
# ───────────────────────────────
async def get_bot_name(bot_username: str):
    if bot_username in botname:
        return botname[bot_username]

    bot = bot_name.find_one({"bot_username": bot_username})
    if not bot:
        return "ميمو"

    botname[bot_username] = bot["bot_name"]
    return bot["bot_name"]

async def set_bot_name(bot_username: str, BOT_NAME: str):
    botname[bot_username] = BOT_NAME
    bot_name.update_one(
        {"bot_username": bot_username},
        {"$set": {"bot_name": BOT_NAME}},
        upsert=True
    )


# ───────────────────────────────
# Bot Group
# ───────────────────────────────
async def get_group(bot_username: str):
    if bot_username in GROUP:
        return GROUP[bot_username]

    bot = groupdb.find_one({"bot_username": bot_username})
    if not bot:
        return GROUPOWNER

    GROUP[bot_username] = bot["group"]
    return bot["group"]

async def set_group(bot_username: str, group: str):
    GROUP[bot_username] = group
    groupdb.update_one(
        {"bot_username": bot_username},
        {"$set": {"group": group}},
        upsert=True
    )


# ───────────────────────────────
# Bot Channel
# ───────────────────────────────
async def get_channel(bot_username: str):
    if bot_username in CHANNEL:
        return CHANNEL[bot_username]

    bot = channeldb.find_one({"bot_username": bot_username})
    if not bot:
        return CHANNELOWNER

    CHANNEL[bot_username] = bot["channel"]
    return bot["channel"]

async def set_channel(bot_username: str, channel: str):
    CHANNEL[bot_username] = channel
    channeldb.update_one(
        {"bot_username": bot_username},
        {"$set": {"channel": channel}},
        upsert=True
    )


# ───────────────────────────────
# SR Group
# ───────────────────────────────
async def get_groupsr(bot_username: str):
    if bot_username in GROUPsr:
        return GROUPsr[bot_username]

    bot = groupdbsr.find_one({"bot_username": bot_username})
    if not bot:
        return GROUPOWNER

    GROUPsr[bot_username] = bot["groupsr"]
    return bot["groupsr"]


async def set_groupsr(bot_username: str, groupsr: str):
    GROUPsr[bot_username] = groupsr
    groupdbsr.update_one(
        {"bot_username": bot_username},
        {"$set": {"groupsr": groupsr}},
        upsert=True
    )

# ───────────────────────────────
# SR Channel
# ───────────────────────────────
async def get_channelsr(bot_username: str):
    name = CHANNELsr.get(bot_username)
    if not name:
        bot = channeldbsr.find_one({"bot_username": bot_username})
        if not bot:
            return CHANNELOWNER
        CHANNELsr[bot_username] = bot["channelsr"]
        return bot["channelsr"]
    return name

async def set_channelsr(bot_username: str, channelsr: str):
    CHANNELsr[bot_username] = channelsr
    channeldbsr.update_one(
        {"bot_username": bot_username},
        {"$set": {"channelsr": channelsr}},
        upsert=True
    )

# ───────────────────────────────
# Commands for setting channels/groups
# ───────────────────────────────
@Client.on_message(filters.command("• تعين قناة البوت •", ""))
async def set_botch(client: Client, message):
    if message.chat.username in OWNER:
        NAME = await client.ask(message.chat.id, "ارسل رابط القناة البوت الجديدة", filters=filters.text)
        channel = NAME.text
        bot_username = client.me.username
        await set_channel(bot_username, channel)
        await message.reply_text("**تم تعيين قناة البوت بنجاح 🖱️**")
        return

@Client.on_message(filters.command("• تعين مجموعة البوت •", ""))
async def set_botgr(client: Client, message):
    if message.chat.username in OWNER:
        NAME = await client.ask(message.chat.id, "ارسل رابط الجروب الجديد", filters=filters.text)
        group = NAME.text
        bot_username = client.me.username
        await set_group(bot_username, group)
        await message.reply_text("**تم تعيين مجموعة البوت بنجاح 🖱️**")
        return


@Client.on_message(filters.command("• تعين قناة السورس •", ""))
async def set_botchsr(client: Client, message):
    if message.chat.username in OWNER:
        NAME = await client.ask(message.chat.id, "ارسل رابط القناة البوت الجديدة", filters=filters.text)
        channelsr = NAME.text
        bot_username = client.me.username
        await set_channelsr(bot_username, channelsr)
        await message.reply_text("**تم تعيين قناة السورس بنجاح 🖱️**")
        return

@Client.on_message(filters.command("• تعين مجموعة السورس •", ""))
async def set_botgrsr(client: Client, message):
    if message.chat.username in OWNER:
        NAME = await client.ask(message.chat.id, "ارسل رابط الجروب الجديد", filters=filters.text)
        groupsr = NAME.text
        bot_username = client.me.username
        await set_groupsr(bot_username, groupsr)
        await message.reply_text("**تم تعيين مجموعة السورس بنجاح 🖱️**")
        return


# ───────────────────────────────
# Mongo DB
# ───────────────────────────────
async def get_data(client):
    mongodb = _mongo_client_(MONGO_DB_URL)
    bot_username = client.me.username
    mongodb = mongodb[bot_username]
    return mongodb


# ───────────────────────────────
# Assistant Client
# ───────────────────────────────
async def get_userbot(bot_username):
    userbot = user.get(bot_username)
    if not userbot:
        Bots = botss.find({})
        for i in Bots:
            bot = i["bot_username"]
            if bot == bot_username:
                session = i["session"]
                userbot = Client("KERO", api_id=API_ID, api_hash=API_HASH, session_string=session)
                user[bot_username] = userbot
                return userbot
    return userbot

# ───────────────────────────────
# Call Client
# ───────────────────────────────
async def get_call(bot_username):
    calll = call.get(bot_username)
    if not calll:
        Bots = botss.find({})
        for i in Bots:
            bot = i["bot_username"]
            if bot == bot_username:
                userbot = await get_userbot(bot_username)
                callo = PyTgCalls(userbot, cache_duration=100)
                await callo.start()
                call[bot_username] = callo
                return callo
    return calll

# ───────────────────────────────
# App Client
# ───────────────────────────────
async def get_app(bot_username):
    app = boot.get(bot_username)
    if not app:
        Bots = botss.find({})
        for i in Bots:
            bot = i["bot_username"]
            if bot == bot_username:
                token = i["token"]
                app = Client("KERO", api_id=API_ID, api_hash=API_HASH, bot_token=token, plugins=dict(root="KERO"))
                boot[bot_username] = app
                return app
    return app


# ───────────────────────────────
# Logger
# ───────────────────────────────
async def get_logger(bot_username):
    loggero = logger.get(bot_username)
    if not loggero:
        Bots = botss.find({})
        for i in Bots:
            bot = i["bot_username"]
            if bot == bot_username:
                loggero = i["logger"]
                logger[bot_username] = loggero
                return loggero
    return loggero


async def get_logger_mode(bot_username):
    logger_m = logger_mode.get(bot_username)
    if not logger_m:
        Bots = botss.find({})
        for i in Bots:
            bot = i["bot_username"]
            if bot == bot_username:
                logger_m = i["logger_mode"]
                logger_mode[bot_username] = logger_m
                return logger_m
    return logger_m

# ───────────────────────────────
# Must Join
# ───────────────────────────────
async def must_join(bot_username):
    name = must.get(bot_username)
    if not name:
        bot = mustdb.find_one({"bot_username": bot_username})
        if not bot:
            return "معطل"
        must[bot_username] = bot["getmust"]
        return bot["getmust"]
    return name

async def set_must(bot_username: str, m: str):
    if m == "• تعطيل الاشتراك الإجباري •":
        ii = "معطل"
    else:
        ii = "مفعل"
    must[bot_username] = ii
    mustdb.update_one(
        {"bot_username": bot_username},
        {"$set": {"getmust": ii}},
        upsert=True
    )

@Client.on_message(filters.command(["• تعطيل الاشتراك الإجباري •", "• تفعيل الاشتراك الإجباري •"], ""))
async def set_join_must(client: Client, message):
    if message.chat.username in OWNER:
        bot_username = client.me.username
        m = message.command[0]
        await set_must(bot_username, m)
        if message.command[0] == "• تعطيل الاشتراك الإجباري •":
            await message.reply_text("**تم تعطيل الاشتراك الإجباري بنجاح 🖱️**")
        else:
            await message.reply_text("**تم تفعيل الاشتراك الإجباري بنجاح 🖱️**")
        return


# Explicit exports for start.py and other modules
__all__ = [
    'get_dev',
    'get_bot_name',
    'set_bot_name',
    'get_logger',
    'get_group',
    'get_channel',
    'get_dev_name',
    'get_dev_user',
    'get_dev_username',
    'get_video_source',
    'set_video_source',
    'get_groupsr',
    'get_channelsr',
    'get_userbot',
    'set_dev_user',
    'set_group',
    'set_channel',
    'set_groupsr',
    'set_channelsr',
    'get_call',
    'get_app',
    'get_logger_mode',
    'must_join',
    'set_must',
    'get_data',
    '_mongo_client_',
    'MONGO_DB_URL',
    'botss',
    'Bots',
    'db',
    'dev_cache',
    'dev',
    'devname',
]