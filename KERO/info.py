import yt_dlp
import os
import asyncio
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import appp, OWNER, OWNER_NAME, VIDEO, PHOTO
from KERO.Data import get_data
from googletrans import Translator
# expose botss from Data so other modules importing from KERO.info
# (like `KERO.start`) can access the bots collection without importing
# KERO.Data directly and avoid ImportError for missing symbol.
from KERO.Data import (get_call, get_app, get_userbot, get_group, get_channel, must_join, botss)

from config import (
    API_ID,
    API_HASH,
    MONGO_DB_URL,
    user,
    dev,
    call,
    logger,
    logger_mode,
    botname,
    helper as ass,
)

from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient

from youtube_search import YoutubeSearch
from youtubesearchpython.__future__ import VideosSearch

# -------------------------
# pytgcalls imports
# -------------------------
from pytgcalls import PyTgCalls
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import StreamAudioEnded

from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityAudio,
    LowQualityVideo,
    MediumQualityAudio,
    MediumQualityVideo
)

# -------------------------
# باقي المكتبات
# -------------------------
import re
import textwrap
import aiofiles
import aiohttp
from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps
)

translator = Translator()


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


ahmed = "https://graph.org/file/bbe526c61648eebca422c.jpg"

async def gen_thumb(videoid, photo):
    if os.path.isfile(f"{photo}.png"):
        return f"{photo}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
                test = translator.translate(title, dest="en")
                title = test.text
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"thumb{videoid}.png")
        KEROv = Image.open(f"{photo}")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(5))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        Xcenter = KEROv.width / 2
        Ycenter = KEROv.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = KEROv.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), Image.LANCZOS)
        logo = ImageOps.expand(logo, border=15, fill="white")
        background.paste(logo, (50, 100))
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("font2.ttf", 40)
        font2 = ImageFont.truetype("font2.ttf", 70)
        arial = ImageFont.truetype("font2.ttf", 30)
        name_font = ImageFont.truetype("font.ttf", 30)
        para = textwrap.wrap(title, width=32)
        j = 0
        draw.text(
            (600, 150),
            "NoNa PlAYiNg",
            fill="white",
            stroke_width=2,
            stroke_fill="white",
            font=font2,
        )
        for line in para:
            if j == 1:
                j += 1
                draw.text(
                    (600, 340),
                    f"{line}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )
            if j == 0:
                j += 1
                draw.text(
                    (600, 280),
                    f"{line}",
                    fill="white",
                    stroke_width=1,
                    stroke_fill="white",
                    font=font,
                )

        draw.text(
            (600, 450),
            f"Views : {views[:23]}",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (600, 500),
            f"Duration : {duration[:23]} Mins",
            (255, 255, 255),
            font=arial,
        )
        draw.text(
            (600, 550),
            f"Channel : {channel}",
            (255, 255, 255),
            font=arial,
        )
        try:
            os.remove(f"{photo}")
            os.remove(f"thumb{videoid}.png")
        except:
            pass
        background.save(f"{photo}.png")
        return f"{photo}.png"
    except Exception as e:
        print(f"Error in gen_thumb: {e}")
        return ahmed


mongodb = _mongo_client_(MONGO_DB_URL)

db = {}

async def add(
    chat_id,
    bot_username,
    file_path,
    link,
    title,
    duration,
    videoid,
    vid,
    user_id):
    put = {
        "title": title,
        "dur": duration,
        "user_id": user_id,
        "chat_id": chat_id,
        "vid": vid,
        "file_path": file_path,
        "link": link,
        "videoid": videoid,
        "played": 0,
    }
    chat_id = f"{bot_username}{chat_id}"
    i = db.get(chat_id)
    if not i:
        db[chat_id] = []
    db[chat_id].append(put)
    return

# Users
async def is_served_user(client, user_id: int) -> bool:
    userdb = await get_data(client)
    userdb = userdb.users
    user = await userdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def get_served_users(client) -> list:
    userdb = await get_data(client)
    userdb = userdb.users 
    users_list = []
    async for user in userdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(client, user_id: int):
    userdb = await get_data(client)
    userdb = userdb.users
    is_served = await is_served_user(client, user_id)
    if is_served:
        return
    return await userdb.insert_one({"user_id": user_id})

async def del_served_user(client, user_id: int):
    chats = await get_data(client)
    chatsdb = chats.users
    is_served = await is_served_user(client, user_id)
    if not is_served:
        return
    return await chatsdb.delete_one({"user_id": user_id})

# Served Chats
async def get_served_chats(client) -> list:
    chats = await get_data(client)
    chatsdb = chats.chats
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(client, chat_id: int) -> bool:
    chats = await get_data(client)
    chatsdb = chats.chats
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_served_chat(client, chat_id: int):
    chats = await get_data(client)
    chatsdb = chats.chats
    is_served = await is_served_chat(client, chat_id)
    if is_served:
        return
    return await chatsdb.insert_one({"chat_id": chat_id})


async def del_served_chat(client, chat_id: int):
    chats = await get_data(client)
    chatsdb = chats.chats
    is_served = await is_served_chat(client, chat_id)
    if not is_served:
        return
    return await chatsdb.delete_one({"chat_id": chat_id})

# Served Call
activecall = {}

async def get_served_call(bot_username) -> list:
    return activecall.get(bot_username, [])


async def is_served_call(client, chat_id: int) -> bool:
    bot_username = client.me.username
    if bot_username not in activecall:
        activecall[bot_username] = []
    if chat_id not in activecall[bot_username]:
        return False
    else:
        return True


async def add_served_call(client, chat_id: int):
    bot_username = client.me.username
    if bot_username not in activecall:
        activecall[bot_username] = []
    if chat_id not in activecall[bot_username]:
        activecall[bot_username].append(chat_id)


async def remove_served_call(bot_username, chat_id: int):
    if bot_username in activecall and chat_id in activecall[bot_username]:
        activecall[bot_username].remove(chat_id)

# Active Voice Chats
active = []

async def get_active_chats() -> list:
    return active


async def is_active_chat(chat_id: int) -> bool:
    if chat_id not in active:
        return False
    else:
        return True


async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)


# Active Video Chats
activevideo = []

async def get_active_video_chats() -> list:
    return activevideo


async def is_active_video_chat(chat_id: int) -> bool:
    if chat_id not in activevideo:
        return False
    else:
        return True


async def add_active_video_chat(chat_id: int):
    if chat_id not in activevideo:
        activevideo.append(chat_id)


async def remove_active_video_chat(chat_id: int):
    if chat_id in activevideo:
        activevideo.remove(chat_id)

async def remove_active(bot_username, chat_id: int):
    chat = f"{bot_username}{chat_id}"
    try:
        db[chat] = []
    except Exception as e:
        print(f"Error clearing db: {e}")
    try:
        await remove_active_video_chat(chat_id)
    except Exception as e:
        print(f"Error removing video chat: {e}")
    try:
        await remove_active_chat(chat_id)
    except Exception as e:
        print(f"Error removing active chat: {e}")
    try:
        await remove_served_call(bot_username, chat_id)
    except Exception as e:
        print(f"Error removing served call: {e}")


async def download(bot_username, link, video: Union[bool, str] = None):
    loop = asyncio.get_running_loop()

    def audio_dl():
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"downloads/{bot_username}%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True
        }
        x = yt_dlp.YoutubeDL(ydl_opts)
        info = x.extract_info(link, False)
        file_path = os.path.join("downloads", f"{bot_username}{info['id']}.{info['ext']}")
        if os.path.exists(file_path):
            return file_path
        x.download([link])
        return file_path

    if video:
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "-g", "-f", "best[height<=?720][width<=?1280]", link,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            downloaded_file = stdout.decode().split("\n")[0]
        else:
            return None
    else:
        downloaded_file = await loop.run_in_executor(None, audio_dl)

    return downloaded_file

# تغيير الاغاني التلقائي
async def change_stream(bot_username, client, chat_id):
    try:
        chat_key = f"{bot_username}{chat_id}"
        check = db.get(chat_key, [])
        if check:
            try:
                check.pop(0)
            except:
                pass
        if not check:
            await remove_active(bot_username, chat_id)
            try:
                return await client.leave_group_call(chat_id)
            except Exception as e:
                print(f"Error leaving call: {e}")
                return

        current = check[0]
        file_path = current.get("file_path")
        title = current.get("title")
        dur = current.get("dur")
        user_id = current.get("user_id")
        video = current.get("vid")
        videoid = current.get("videoid")
        link = current.get("link")
        current["played"] = 0

        audio_stream_quality = MediumQualityAudio()
        video_stream_quality = MediumQualityVideo()

        app = appp.get(bot_username)
        if not app:
            print(f"App not found for {bot_username}")
            return

        if link and not file_path:
            try:
                file_path = await download(bot_username, link, video)
            except Exception as e:
                print(f"Error downloading: {e}")
                await app.send_message(chat_id, "**حدث خطأ اثناء تشغيل التالي .⚡**")
                return

        stream = AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality) if video else AudioPiped(file_path, audio_parameters=audio_stream_quality)

        try:
            await client.change_stream(chat_id, stream)
        except Exception as e:
            print(f"Error changing stream: {e}")
            await app.send_message(chat_id, "**حدث خطأ اثناء تشغيل التالي .⚡**")
            return

        try:
            userx = await app.get_users(user_id)
        except Exception as e:
            print(f"Error getting user: {e}")
            userx = None

        if videoid and userx:
            try:
                if userx.photo:
                    photo_id = userx.photo.big_file_id
                else:
                    owner_chat = await app.get_chat(OWNER[0])
                    photo_id = owner_chat.photo.big_file_id
                photo = await app.download_media(photo_id)
                img = await gen_thumb(videoid, photo)
            except Exception as e:
                print(f"Error generating thumb: {e}")
                img = PHOTO
        else:
            img = PHOTO

        requester = userx.mention if userx else "Unknown"
        gr = await get_group(bot_username)
        ch = await get_channel(bot_username)

        buttons = [
            [InlineKeyboardButton("END", callback_data="stop"),
             InlineKeyboardButton("RESUME", callback_data="resume"),
             InlineKeyboardButton("PAUSE", callback_data="pause")],
            [InlineKeyboardButton("𝗖𝗵𝗮𝗻𝗻𝗲𝗹 🖱️", url=ch),
             InlineKeyboardButton("𝗚𝗿𝗼𝘂𝗽 🖱️", url=gr)],
            [InlineKeyboardButton(OWNER_NAME, url=f"https://t.me/{OWNER[0]}")],
            [InlineKeyboardButton("اضف البوت الي مجموعتك او قناتك ⚡", url=f"https://t.me/{bot_username}?startgroup=True")]
        ]

        await app.send_photo(
            chat_id,
            photo=img,
            caption=f"**Starting Streaming **\n\n**Song Name** : {title}\n**Duration Time** {dur}\n**Request By** : {requester}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if img and os.path.exists(img) and img != PHOTO:
                os.remove(img)
        except Exception as e:
            print(f"Error removing files: {e}")

    except Exception as e:
        print(f"Error in change_stream: {e}")


# رسالة انضمام المساعد للخاص
async def helper(bot_username):
    user = await get_userbot(bot_username)
    gr = await get_group(bot_username)

    @user.on_message(filters.private)
    async def helperuser(client, update):
        if bot_username not in ass:
            ass[bot_username] = []
        if update.chat.id not in ass[bot_username]:
            await user.send_message(
                update.chat.id,
                f"**انا الحساب الخاص بتشغيل الاغاني ⚡**\n\n**⚡ {gr} : انضم هنا**"
            )
            ass[bot_username].append(update.chat.id)


# Call handler
async def Call(bot_username):
    call_client = await get_call(bot_username)

    @call_client.on_kicked()
    @call_client.on_closed_voice_chat()
    @call_client.on_left()
    async def stream_services_handler(client, chat_id: int):
        return await remove_active(bot_username, chat_id)

    @call_client.on_stream_end()
    async def stream_end_handler1(client, update):
        if isinstance(update, StreamAudioEnded):
            await change_stream(bot_username, client, update.chat_id)


# التأكد من اشتراك المستخدم في القناة
async def joinch(message):
    try:
        ii = await must_join(message._client.me.username)
        if ii == "معطل":
            return False

        cch = await get_channel(message._client.me.username)
        ch = cch.replace("https://t.me/", "")

        try:
            await message._client.get_chat_member(ch, message.from_user.id)
            return False
        except UserNotParticipant:
            try:
                await message.reply(
                    f"🚦 يجب ان تشترك في القناة\n\nقنـاة الـبـوت : « {cch} »",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("اضـغط هنا للأشتـراك القنـاة 🚦", url=cch)]]
                    )
                )
                return True
            except Exception as e:
                print(f"Error sending join message: {e}")
                return False
        except Exception as e:
            print(f"Error checking membership: {e}")
            return False
    except Exception as e:
        print(f"Error in joinch: {e}")
        return False


# Explicitly export symbols so Maker/KERO.py and other modules can import them
__all__ = [
    'Call',
    'activecall',
    'helper',
    'active',
    'botss',
    'is_served_chat',
    'add_served_chat',
    'is_served_user',
    'add_served_user',
    'get_served_chats',
    'get_served_users',
    'del_served_chat',
    'del_served_user',
    'joinch',
    'API_ID',
    'API_HASH',
    'MONGO_DB_URL',
    'user',
    'db',
    'add',
    'download',
    'gen_thumb',
    'is_served_call',
    'remove_active',
    'add_active_chat',
    'add_active_video_chat',
    'add_served_call',
    'remove_active_chat',
    'remove_active_video_chat',
    'get_active_chats',
    'get_active_video_chats',
    'is_active_chat',
    'is_active_video_chat',
    'change_stream',
]