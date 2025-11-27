from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    UserAlreadyParticipant,
    UserNotParticipant,
    FloodWait
)

from pytgcalls import PyTgCalls
try:
    from pytgcalls.exceptions import (
        AlreadyJoinedError,
        NoActiveGroupCall,
        TelegramServerError,
        NotInCallError,
    )
except Exception:
    # Compatibility fallback for different pytgcalls versions
    try:
        from pytgcalls import exceptions as _pytg_ex
        AlreadyJoinedError = getattr(_pytg_ex, "AlreadyJoinedError", Exception)
        NoActiveGroupCall = getattr(_pytg_ex, "NoActiveGroupCall", Exception)
        TelegramServerError = getattr(_pytg_ex, "TelegramServerError", Exception)
        NotInCallError = getattr(_pytg_ex, "NotInCallError", Exception)
    except Exception:
        AlreadyJoinedError = Exception
        NoActiveGroupCall = Exception
        TelegramServerError = Exception
        NotInCallError = Exception
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

from youtubesearchpython.__future__ import VideosSearch
from youtube_search import YoutubeSearch
import yt_dlp
import pytgcalls

from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient

import os
import aiohttp
import requests
import random
import asyncio
from datetime import datetime, timedelta
from typing import Union

from config import (
    API_ID,
    API_HASH,
    MONGO_DB_URL,
    VIDEO,
    OWNER,
    OWNER_NAME,
    LOGS,
    GROUP,
    CHANNEL,
    PHOTO
)

from bot import bot as man

from KERO.info import (
    db,
    add,
    is_served_call,
    add_active_video_chat,
    add_served_call,
    add_active_chat,
    gen_thumb,
    download,
    remove_active,
    joinch
)

from KERO.Data import (
    get_logger,
    get_userbot,
    get_call,
    get_logger_mode,
    get_group,
    get_channel
)

mongodb = _mongo_client_(MONGO_DB_URL)
pymongodb = MongoClient(MONGO_DB_URL)
Bots = pymongodb.Bots


async def join_assistant(client, chat_id, message_id, userbot, file_path):
    join = None
    try:
        try:
            user = userbot.me
            user_id = user.id
            get = await client.get_chat_member(chat_id, user_id)
        except ChatAdminRequired:
            await client.send_message(chat_id, "**قم بترقية البوت مشرف .⚡**", reply_to_message_id=message_id)
            return None
        
        if get.status == ChatMemberStatus.BANNED:
            await client.send_message(
                chat_id,
                f"**قم بإلغاء الحظر عن الحساب المساعد لتفعيل البوت**.\n\n"
                f"@{user.username} : **الحساب المساعد ⚡.**\n"
                f"**قم بتنظيف قائمة المستخدمين الذين تمت إزالتهم ⚡.**\n\n"
                f"**@AT_W2 | @AT_W3 : او تواصل مع المطور من هنا ⚡.**",
                reply_to_message_id=message_id
            )
            return None
        else:
            join = True
            
    except UserNotParticipant:
        chat = await client.get_chat(chat_id)
        if chat.username:
            try:
                await userbot.join_chat(chat.username)
                join = True
            except UserAlreadyParticipant:
                join = True
            except Exception:
                try:
                    invitelink = await client.export_chat_invite_link(chat_id)
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                    await asyncio.sleep(3)
                    await userbot.join_chat(invitelink)
                    join = True
                except ChatAdminRequired:
                    await client.send_message(
                        chat_id,
                        "**قم بإعطاء البوت صلاحية إضافة المستخدمين عبر الرابط .⚡**",
                        reply_to_message_id=message_id
                    )
                    return None
                except Exception as e:
                    print(f"Error joining via invite: {e}")
                    await client.send_message(
                        chat_id,
                        f"**حدث خطأ حاول مرة أخرى لاحقاً**\n**{GROUP} : او تواصل مع الدعم من هنا .⚡**",
                        reply_to_message_id=message_id
                    )
                    return None
        else:
            try:
                try:
                    invitelink = chat.invite_link
                    if invitelink is None:
                        invitelink = await client.export_chat_invite_link(chat_id)
                except Exception:
                    try:
                        invitelink = await client.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        await client.send_message(
                            chat_id,
                            "**قم بإعطاء البوت صلاحية إضافة مستخدمين عبر الرابط .⚡**",
                            reply_to_message_id=message_id
                        )
                        return None
                    except Exception as e:
                        print(f"Error exporting invite: {e}")
                        await client.send_message(
                            chat_id,
                            f"**حدث خطأ حاول مرة أخرى لاحقاً**\n**{GROUP} : او تواصل مع الدعم من هنا .⚡**",
                            reply_to_message_id=message_id
                        )
                        return None
                        
                m = await client.send_message(chat_id, "**انتظر قليلاً جاري تفعيل البوت .⚡**")
                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                await userbot.join_chat(invitelink)
                join = True
                await m.edit(f"**{user.mention} : انضم الحساب المساعد**\n**وتم تفعيل البوت يمكنك التشغيل الان .⚡**")
            except UserAlreadyParticipant:
                join = True
            except Exception as e:
                print(f"Error in join_assistant: {e}")
                await client.send_message(
                    chat_id,
                    f"**حدث خطأ حاول مرة أخرى لاحقاً**\n**{GROUP} : او تواصل مع الدعم من هنا .⚡**",
                    reply_to_message_id=message_id
                )
                return None
    except Exception as e:
        print(f"Error in join_assistant main: {e}")
        return None
        
    return join


async def join_call(
    client,
    message_id,
    chat_id,
    bot_username,
    file_path,
    link,
    vid: Union[bool, str] = None
):
    userbot = await get_userbot(bot_username)
    Done = None
    
    try:
        call = await get_call(bot_username)
    except Exception as e:
        print(f"Error getting call: {e}")
        return Done
    
    audio_stream_quality = MediumQualityAudio()
    video_stream_quality = MediumQualityVideo()
    stream = (
        AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality)
        if vid else AudioPiped(file_path, audio_parameters=audio_stream_quality)
    )
    
    try:
        await call.join_group_call(chat_id, stream)
        Done = True
    
    except NoActiveGroupCall:
        h = await join_assistant(client, chat_id, message_id, userbot, file_path)
        if h:
            try:
                await call.join_group_call(chat_id, stream)
                Done = True
            except Exception as e:
                print(f"Error joining after assistant: {e}")
                await client.send_message(chat_id, "**قم بتشغيل المكالمة أولاً .🚦**", reply_to_message_id=message_id)
    
    except AlreadyJoinedError:
        await client.send_message(chat_id, "**قم بإعادة تشغيل المكالمة ..🚦**", reply_to_message_id=message_id)
    
    except TelegramServerError:
        await client.send_message(chat_id, "**قم بإعادة تشغيل المكالمة ..🚦**", reply_to_message_id=message_id)
    
    except Exception as e:
        print(f"Error in join_call: {e}")
        return Done
    
    return Done


def seconds_to_min(seconds):
    if seconds is not None:
        seconds = int(seconds)
        d, h, m, s = (
            seconds // (3600 * 24),
            seconds // 3600 % 24,
            seconds % 3600 // 60,
            seconds % 3600 % 60,
        )
        if d > 0:
            return "{:02d}:{:02d}:{:02d}:{:02d}".format(d, h, m, s)
        elif h > 0:
            return "{:02d}:{:02d}:{:02d}".format(h, m, s)
        elif m > 0:
            return "{:02d}:{:02d}".format(m, s)
        elif s > 0:
            return "00:{:02d}".format(s)
    return "-"


async def logs(bot_username, client, message):
    try:
        if await get_logger_mode(bot_username) == "OFF":
            return

        logger = await get_logger(bot_username)
        log_channel = LOGS

        if message.chat.type == ChatType.CHANNEL:
            chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
            name = message.author_signature if message.author_signature else chat
            text = f"**Playing History**\n\n**Chat : {chat}**\n**Chat Id : {message.chat.id}**\n**User Name : {name}**\n\n**Played : {message.text}**"
        else:
            chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
            user_info = f"User Username : @{message.from_user.username}" if message.from_user.username else f"User Id : {message.from_user.id}"
            text = f"**Playing History**\n\n**Chat : {chat}**\n**Chat Id : {message.chat.id}**\n**User Name : {message.from_user.mention}**\n**{user_info}**\n\n**Played : {message.text}**"

        await client.send_message(logger, text=text, disable_web_page_preview=True)
        await man.send_message(log_channel, text=f"[ @{bot_username} ]\n{text}", disable_web_page_preview=True)

    except Exception as e:
        print(f"Error in logs function: {e}")


@Client.on_message(filters.command(["عشوائي", "تشغيل عشوائي"]))
async def random_play(client: Client, message):
    if await joinch(message):
        return
    try:
        chat_id = message.chat.id
        bot_username = client.me.username
        rep = await message.reply_text("**جاري اختيار تشغيل عشوائي ♻️**")
        
        try:
            call = await get_call(bot_username)
        except Exception as e:
            print(f"Error getting call: {e}")
            await remove_active(bot_username, chat_id)
            return await rep.edit("**حدث خطأ**")
            
        try:
            await call.get_call(chat_id)
        except pytgcalls.exceptions.GroupCallNotFound:
            await remove_active(bot_username, chat_id)

        message_id = message.id
        user = await get_userbot(bot_username)
        req = message.from_user.mention if message.from_user else message.chat.title
        raw_list = [msg async for msg in user.get_chat_history("ELNQYBMUSIC") if msg.audio]

        if not raw_list:
            return await rep.edit("لا توجد أغاني لتشغيلها.")

        x = random.choice(raw_list)
        file_path = await x.download()
        title = x.audio.title
        dur = x.audio.duration
        duration = seconds_to_min(dur)
        photo = PHOTO
        vid = True if x.video else None
        user_id = message.from_user.id if message.from_user else "ISIIQ"
        videoid = None
        link = None

        await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)

        if not await is_served_call(client, chat_id):
            await add_active_chat(chat_id)
            await add_served_call(client, chat_id)
            if vid:
                await add_active_video_chat(chat_id)
            c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
            if not c:
                await remove_active(bot_username, chat_id)
                return await rep.delete()

        await rep.delete()

        gr = await get_group(bot_username)
        ch = await get_channel(bot_username)
        buttons = [
            [InlineKeyboardButton("END", callback_data="stop"),
             InlineKeyboardButton("RESUME", callback_data="resume"),
             InlineKeyboardButton("PAUSE", callback_data="pause")],
            [InlineKeyboardButton("قنـاه السورس", url=ch),
             InlineKeyboardButton("جــروب الدعم", url=gr)],
            [InlineKeyboardButton(OWNER_NAME, url=f"https://t.me/{OWNER[0]}")],
            [InlineKeyboardButton("اضف البوت الي مجموعتك او قناتك ⚡", url=f"https://t.me/{bot_username}?startgroup=True")]
        ]

        await message.reply_photo(
            photo=photo,
            caption=f"**Started Stream Random**\n\n**Song Name : {title}**\n**Duration Time : {duration}**\n**Requests By : {req}**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await logs(bot_username, client, message)
        await asyncio.sleep(4)

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as es:
        print(f"Error in random stream: {es}")


@Client.on_message(filters.command(["/play", "play", "/vplay", "شغل", "تشغيل", "فيد", "فيديو"]))
async def play(client: Client, message):
    if await joinch(message):
        return

    KERO = message
    bot_username = client.me.username
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "ISIIQ"
    message_id = message.id
    gr = await get_group(bot_username)
    ch = await get_channel(bot_username)

    button = [
        [InlineKeyboardButton(text=".♪ 𝑬𝒏𝒅", callback_data="stop"),
         InlineKeyboardButton(text="𝑹𝒆𝒔𝒖𝒎𝒆", callback_data="resume"),
         InlineKeyboardButton(text="𝑷𝒂𝒖𝒔𝒆 ♪.", callback_data="pause")],
        [InlineKeyboardButton(text="قــناه الســورس", url=ch),
         InlineKeyboardButton(text="جــروب الـدعم", url=gr)],
        [InlineKeyboardButton(text=OWNER_NAME, url=f"https://t.me/{OWNER[0]}")],
        [InlineKeyboardButton(text="اضف البوت الي مجموعتك او قناتك ⚡",
                              url=f"https://t.me/{bot_username}?startgroup=True")]
    ]

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "**♪ لا يمكنك التشغيل هنا للأسف 💎 .\n♪ قم بإضافة البوت لمجموعتك للتشغيل 💎 .**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                "اضف البوت الي مجموعتك او قناتك ⚡",
                url=f"https://t.me/{bot_username}?startgroup=True")]])
        )
        
    if message.sender_chat and message.chat.type != ChatType.CHANNEL:
        return await message.reply_text("**♪ يمكنك التشغيل بحسابك الخاص فقط 💎 .**")

    rep = None
    if len(message.command) == 1 and not message.reply_to_message:
        rep = await message.reply_text("**♪ جاري التشغيل انتظر قليلاً 💎 .**")

    try:
        call = await get_call(bot_username)
    except Exception as e:
        print(f"Error getting call: {e}")
        await remove_active(bot_username, chat_id)
        return
        
    try:
        await call.get_call(chat_id)
    except pytgcalls.exceptions.GroupCallNotFound:
        await remove_active(bot_username, chat_id)

    # الحصول على الأغنية
    if not message.reply_to_message:
        if len(message.command) == 1:
            if message.chat.type == ChatType.CHANNEL:
                return await message.reply_text("**♪ قم بكتابة شيء لتشغيله 💎 .**")
            try:
                name = await client.ask(
                    chat_id,
                    text="**♪ ارسل اسم او رابط لتشغيله 💎 .**",
                    reply_to_message_id=message.id,
                    filters=filters.user(message.from_user.id),
                    timeout=200
                )
                name = name.text
                rep = await message.reply_text("**♪ جاري التشغيل انتظر قليلاً 💎 .**")
            except asyncio.TimeoutError:
                return
        else:
            name = message.text.split(None, 1)[1]
            if not rep:
                rep = await message.reply_text("**♪ جاري التشغيل انتظر قليلاً 💎 .**")

        try:
            results = VideosSearch(name, limit=1)
            result_data = (await results.next())["result"][0]
        except Exception as e:
            print(f"Search error: {e}")
            return await rep.edit("**♪ لم يتم العثور على نتائج 💎 .**")

        title = result_data["title"]
        duration = result_data["duration"]
        videoid = result_data["id"]
        yturl = result_data["link"]
        thumbnail = result_data["thumbnails"][0]["url"].split("?")[0]
        vid = True if ("v" in message.command[0] or "ف" in message.command[0]) else None

        await rep.edit("**♪ جاري التشغيل انتظر قليلاً ⚡ .**")
        link = yturl

        if await is_served_call(client, chat_id):
            file_path = None
            await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            chat_key = f"{bot_username}{chat_id}"
            position = len(db.get(chat_key, [])) - 1

            chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" \
                if message.chat.username else message.chat.title
            chatname = message.author_signature if message.author_signature else chatname
            requester = chatname if KERO.views else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

            try:
                if message.from_user and message.from_user.photo:
                    photo_id = message.from_user.photo.big_file_id
                    photo = await client.download_media(photo_id)
                elif message.chat.photo:
                    photo_id = message.chat.photo.big_file_id
                    photo = await client.download_media(photo_id)
                else:
                    ahmed = await client.get_chat("AT_W3")
                    photo_id = ahmed.photo.big_file_id
                    photo = await client.download_media(photo_id)
            except Exception as e:
                print(f"Error downloading photo: {e}")
                photo = PHOTO

            photo = await gen_thumb(videoid, photo)
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Add Track To Playlist : {position} 🥁 .\n\n♪ Song Name : {title[:18]} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)
        else:
            await add_active_chat(chat_id)
            await add_served_call(client, chat_id)
            if vid:
                await add_active_video_chat(chat_id)

            file_path = await download(bot_username, link, vid)
            await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
            if not c:
                await remove_active(bot_username, chat_id)
                return await rep.delete()

            chatname = f"[{message.chat.title}](https://t.me/{message.chat.username})" \
                if message.chat.username else message.chat.title
            chatname = message.author_signature if message.author_signature else chatname
            requester = chatname if KERO.views else f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

            try:
                if message.from_user and message.from_user.photo:
                    photo_id = message.from_user.photo.big_file_id
                    photo = await client.download_media(photo_id)
                elif message.chat.photo:
                    photo_id = message.chat.photo.big_file_id
                    photo = await client.download_media(photo_id)
                else:
                    ahmed = await client.get_chat("AT_W3")
                    photo_id = ahmed.photo.big_file_id
                    photo = await client.download_media(photo_id)
            except Exception as e:
                print(f"Error downloading photo: {e}")
                photo = PHOTO

            photo = await gen_thumb(videoid, photo)
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Starting Playing Now 🥁 .\n\n♪ Song Name : {title[:18]} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)

    else:
        # تشغيل الملفات المرفوعة
        if not message.reply_to_message.media:
            return
        rep = await message.reply_text("**♪ جاري تشغيل الملف انتظر قليلاً 🚦 .**")
        photo = PHOTO
        vid = True if (message.reply_to_message.video or message.reply_to_message.document) else None
        file_path = await message.reply_to_message.download()

        file_obj = (message.reply_to_message.audio or message.reply_to_message.voice or
                    message.reply_to_message.video or message.reply_to_message.document)
        title = file_obj.file_name
        duration = seconds_to_min(getattr(file_obj, "duration", 0))
        link = None
        videoid = None

        if await is_served_call(client, chat_id):
            await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            chat_key = f"{bot_username}{chat_id}"
            position = len(db.get(chat_key, [])) - 1
            requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Add Track To Playlist : {position} 🥁 .\n\n♪ Song Name : {title} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)
        else:
            await add_active_chat(chat_id)
            await add_served_call(client, chat_id)
            if vid:
                await add_active_video_chat(chat_id)
            await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
            c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)
            if not c:
                await remove_active(bot_username, chat_id)
                return await rep.delete()

            requester = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
            await message.reply_photo(
                photo=photo,
                caption=f"**♪ Starting Playing Now 🥁 .\n\n♪ Song Name : {title} 🎞️ .\n♪ Duration Time : {duration} ⌚ .\n♪ Request By : {requester} 👤 .**",
                reply_markup=InlineKeyboardMarkup(button)
            )
            await logs(bot_username, client, message)

    try:
        if rep:
            await rep.delete()
    except:
        pass
        
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if isinstance(photo, str) and photo != PHOTO and os.path.exists(photo):
            os.remove(photo)
    except Exception as e:
        print(f"Error removing files: {e}")