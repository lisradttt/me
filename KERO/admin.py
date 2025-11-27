import asyncio
import os

from config import OWNER, OWNER_NAME, VIDEO, PHOTO

# ───────────────────────────────
# Pyrogram
# ───────────────────────────────
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

# ───────────────────────────────
# PyTgCalls (Voice Chat)
# ───────────────────────────────
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import (
    AudioPiped,
    AudioVideoPiped
)
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    MediumQualityAudio,
    MediumQualityVideo,
    LowQualityAudio,
    LowQualityVideo
)

# ───────────────────────────────
# الملفات الداخلية KERO
# ───────────────────────────────
from KERO.info import (
    remove_active,
    is_served_call,
    joinch,
    add,
    db,
    download,
    gen_thumb
)

from KERO.Data import (
    get_call,
    get_dev,
    get_group,
    get_channel
)


@Client.on_callback_query(
    filters.regex(pattern=r"^(pause|skip|stop|resume)$")
)
async def admin_risghts(client: Client, CallbackQuery):
  try:
    a = await client.get_chat_member(CallbackQuery.message.chat.id, CallbackQuery.from_user.id)
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if not a.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
     if not CallbackQuery.from_user.id == dev:
      if not CallbackQuery.from_user.username in OWNER:
        return await CallbackQuery.answer("يجب انت تكون ادمن للقيام بذلك  !", show_alert=True)
    command = CallbackQuery.matches[0].group(1)
    chat_id = CallbackQuery.message.chat.id
    if not await is_served_call(client, chat_id):
        return await CallbackQuery.answer("لا يوجد شئ قيد التشغيل الان .", show_alert=True)
    call = await get_call(bot_username)
    chat_id = CallbackQuery.message.chat.id
    if command == "pause":
        await call.pause_stream(chat_id)
        await CallbackQuery.answer("تم ايقاف التشغيل موقتا ☕🍀", show_alert=True)
        await CallbackQuery.message.reply_text(f"{CallbackQuery.from_user.mention} **تم ايقاف التشغيل بواسطه**")
    if command == "resume":
        await call.resume_stream(chat_id)
        await CallbackQuery.answer("تم استكمال التشغيل ☕🍀", show_alert=True)
        await CallbackQuery.message.reply_text(f"{CallbackQuery.from_user.mention} **تم إستكمال التشغيل بواسطه**")
    if command == "stop":
        try:
         await call.leave_group_call(chat_id)
        except Exception as e:
          print(f"Error leaving call: {e}")
        await remove_active(bot_username, chat_id)
        await CallbackQuery.answer("تم انهاء التشغيل بنجاح ⚡", show_alert=True)
        await CallbackQuery.message.reply_text(f"{CallbackQuery.from_user.mention} **تم انهاء التشغيل بواسطه**")
  except Exception as e:
     print(f"Error in callback handler: {e}")





@Client.on_message(filters.command(["/stop", "/end", "/skip", "/resume", "/pause", "/loop", "ايقاف مؤقت", "استكمال", "تخطي", "انهاء", "اسكت", "ايقاف", "تكرار", "كررها"], "") & ~filters.private)
async def admin_risght(client: Client, message):
  try:
    if await joinch(message):
            return
    bot_username = client.me.username
    dev = await get_dev(bot_username)
    if not message.chat.type == ChatType.CHANNEL:
     a = await client.get_chat_member(message.chat.id, message.from_user.id)
     if not a.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
      if not message.from_user.id == dev:
       if not message.from_user.username in OWNER:
        return await message.reply_text("**يجب انت تكون ادمن للقيام بذلك  !**")
    command = message.command[0]
    chat_id = message.chat.id
    if not await is_served_call(client, chat_id):
        return await message.reply_text("**لا يوجد شئ قيد التشغيل الان .**")
    call = await get_call(bot_username)
    chat_id = message.chat.id
    if command == "/pause" or command == "ايقاف مؤقت":
        await call.pause_stream(chat_id)
        await message.reply_text(f"**تم ايقاف التشغيل موقتاً .♻️**")
    elif command == "/resume" or command == "استكمال":
        await call.resume_stream(chat_id)
        await message.reply_text(f"**تم إستكمال التشغيل .🚀**")
    elif command == "/stop" or command == "/end" or command == "اسكت" or command == "انهاء" or command == "ايقاف":
        try:
         await call.leave_group_call(chat_id)
        except Exception as e:
         print(f"Error leaving call: {e}")
        await remove_active(bot_username, chat_id)
        await message.reply_text(f"**تم انهاء التشغيل .**")
    elif command == "تكرار" or command == "كررها" or command == "/loop":
            if len(message.command) < 2:
               return await message.reply_text("**قم بتحديد مرات التكرار مثل: تكرار 3**")
            
            try:
                text = message.command[1]
                
                # تحويل النص لرقم
                if text == "مره":
                    count = 1
                    display = "مره واحده"
                elif text == "مرتين":
                    count = 2
                    display = "مرتين"
                elif text.isdigit():
                    count = int(text)
                    if count < 1 or count > 10:
                        return await message.reply_text("**استخدم رقم من 1 إلى 10**")
                    display = f"{count} مره"
                else:
                    return await message.reply_text("**خطأ في الاستخدام، مثال: تكرار 3**")
                
                # جلب البيانات من قاعدة البيانات
                chat = f"{bot_username}{chat_id}"
                check = db.get(chat)
                if not check:
                    return await message.reply_text("**لا يوجد شيء في قائمة التشغيل**")
                
                file_path = check[0]["file_path"]
                title = check[0]["title"]
                duration = check[0]["dur"]
                user_id = check[0]["user_id"]
                chat_id = check[0]["chat_id"]
                vid = check[0]["vid"]
                link = check[0]["link"]
                videoid = check[0]["videoid"]
                
                # إضافة المقطع للتكرار
                for _ in range(count):
                    file_path_add = file_path if file_path else None
                    await add(chat_id, bot_username, file_path_add, link, title, duration, videoid, vid, user_id)
                
                await message.reply_text(f"**تم تفعيل التكرار {display}**")
                
            except Exception as e:
                print(f"Error in loop command: {e}")
                await message.reply_text("**حدث خطأ أثناء تفعيل التكرار**")
                
    elif command == "/skip" or command == "تخطي":
       chat = f"{bot_username}{chat_id}"
       check = db.get(chat)
       if not check or len(check) < 2:
         try:
           await call.leave_group_call(chat_id)
         except Exception as e:
           print(f"Error leaving call: {e}")
         await remove_active(bot_username, chat_id)
         return await message.reply_text("**تم ايقاف التشغيل لأن قائمة التشغيل فارغة .⚡**")
       
       popped = check.pop(0)
       file = check[0]["file_path"]
       title = check[0]["title"]
       dur = check[0]["dur"]
       video = check[0]["vid"]
       videoid = check[0]["videoid"]
       user_id = check[0]["user_id"]
       link = check[0]["link"]
       audio_stream_quality = MediumQualityAudio()
       video_stream_quality = MediumQualityVideo()
       if file:
         file_path = file
       else:     
         try:
            file_path = await download(bot_username, link, video)
         except Exception as e:
            print(f"Error downloading: {e}")
            return await client.send_message(chat_id, "**حدث خطأ اثناء تشغيل التالي .⚡**")
       stream = (AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality) if video else AudioPiped(file_path, audio_parameters=audio_stream_quality))
       try:
           await call.change_stream(chat_id, stream)
       except Exception as e:
            print(f"Error changing stream: {e}")
            return await client.send_message(chat_id, "**حدث خطأ اثناء تشغيل التالي .⚡**")
       userx = await client.get_users(user_id)
       if videoid:
         if userx.photo:
            photo_id = userx.photo.big_file_id
         else:
            ahmed = await client.get_chat("AT_W2")
            photo_id = ahmed.photo.big_file_id
         photo = await client.download_media(photo_id)
         img = await gen_thumb(videoid, photo)
       else:
         img = PHOTO
       requester = userx.mention       
       gr = await get_group(bot_username)
       ch = await get_channel(bot_username)
       button = [[InlineKeyboardButton(text="END", callback_data=f"stop"), InlineKeyboardButton(text="RESUME", callback_data=f"resume"), InlineKeyboardButton(text="PAUSE", callback_data=f"pause")], [InlineKeyboardButton(text="قـناه الســورس", url=f"{ch}"), InlineKeyboardButton(text="جــروب الـدعم", url=f"{gr}")], [InlineKeyboardButton(text=f"{OWNER_NAME}", url="https://t.me/M_9_T")], [InlineKeyboardButton(text="اضف البوت الي مجموعتك او قناتك ⚡", url=f"https://t.me/{bot_username}?startgroup=True")]]
       await message.reply_photo(photo=img, caption=f"**Skipped Streaming **\n\n**Song Name** : {title}\n**Duration Time** {dur}\n**Request By** : {requester}", reply_markup=InlineKeyboardMarkup(button))
       try:
           os.remove(file_path)
           os.remove(img)
       except Exception as e:
           print(f"Error removing files: {e}")
    else:
      await message.reply_text("**خطا في استخدام الأمر**")
  except Exception as e:
    print(f"Error in command handler: {e}")