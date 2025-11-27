import os
import aiohttp
import aiofiles
import asyncio
from pyrogram import Client, filters, enums
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
from config import OWNER

# ---------------------------------------
# دوال مساعدة
# ---------------------------------------

def remove_if_exists(path):
    """
    تحذف الملف اذا موجود
    """
    if path and os.path.exists(path):
        os.remove(path)

async def download_file(url, filename):
    """
    تحميل الملفات (صورة أو غيرها) بطريقة async
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(filename, mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    return filename
    except Exception as e:
        print(f"❌ خطأ في تحميل الملف {filename}: {e}")
    return None

async def search_youtube(query, max_results=1):
    """
    البحث في يوتيوب عن الفيديوهات
    """
    try:
        results = YoutubeSearch(query, max_results=max_results).to_dict()
        return results if results else None
    except Exception as e:
        print(f"❌ خطأ في البحث عن {query}: {e}")
        return None

def parse_duration(duration_str):
    """
    تحويل مدة الفيديو من صيغة 00:00:00 إلى ثواني
    """
    try:
        parts = [int(x) for x in duration_str.split(":")]
        duration = sum(val * (60 ** idx) for idx, val in enumerate(reversed(parts)))
        return duration
    except Exception as e:
        print(f"❌ خطأ في تحويل المدة {duration_str}: {e}")
        return 0

# ---------------------------------------
# دالة البحث
# ---------------------------------------

@Client.on_message(filters.command(["بحث"], ""))
async def ytsearch(client, message):
    """
    البحث عن الفيديوهات وعرض النتائج
    """
    if len(message.command) == 1:
        await message.reply_text("🔎 اكتب شيئ للبحث")
        return

    query = message.text.split(None, 1)[1]
    m = await message.reply_text("⏳ جاري البحث...")
    
    try:
        results = await search_youtube(query, 6)
        if not results:
            await m.edit("❌ لم يتم العثور على نتائج")
            return

        text = ""
        for res in results:
            text += f"🎬 عنوان: {res['title']}\n"
            text += f"⏱ المدة: {res['duration']}\n"
            text += f"👀 المشاهدات: {res['views']}\n"
            text += f"📺 القناة: {res['channel']}\n"
            text += f"https://youtube.com{res['url_suffix']}\n\n"

        await m.edit(text, disable_web_page_preview=True)

    except Exception as e:
        await m.edit(f"❌ حدث خطأ أثناء البحث: {e}")

# ---------------------------------------
# دالة التحميل
# ---------------------------------------

@Client.on_message(filters.command(["/song", "/video", "نزل", "تنزيل", "حمل", "تحميل"], ""))
async def downloaded(client: Client, message):
    """
    تحميل فيديو أو أوديو من يوتيوب
    """
    query = None
    m = None

    # ---------------------------------------
    # تحديد نص البحث
    # ---------------------------------------
    if len(message.command) == 1:
        try:
            ask = await client.ask(
                message.chat.id,
                "🔎 ارسل الاسم الان",
                filters=filters.user(message.from_user.id) if message.chat.type != enums.ChatType.PRIVATE else None,
                reply_to_message_id=message.id,
                timeout=20
            )
            query = ask.text
            m = await ask.reply_text("⏳ جاري البحث...")
        except asyncio.TimeoutError:
            await message.reply_text("❌ انتهت المهلة")
            return
        except Exception as e:
            await message.reply_text(f"❌ خطأ: {e}")
            return
    else:
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("⏳ جاري البحث...")

    is_audio = message.command[0] in ["/song", "نزل", "تنزيل"]

    ydl_opts = {
        "format": "bestaudio" if is_audio else "best",
        "keepvideo": not is_audio,
        "quiet": True,
        "outtmpl": "%(title)s.%(ext)s",
    }

    # ---------------------------------------
    # البحث عن الفيديو
    # ---------------------------------------
    try:
        results = await search_youtube(query)
        if not results:
            await m.edit("❌ لم يتم العثور على نتيجة")
            return

        info = results[0]
        link = f"https://youtube.com{info['url_suffix']}"
        title = info["title"][:40]
        duration = parse_duration(info['duration'])

        # ---------------------------------------
        # تحميل الصورة المصغرة
        # ---------------------------------------
        thumb_name = f"{title}.jpg"
        thumb_file = await download_file(info["thumbnails"][0], thumb_name)
        if not thumb_file:
            thumb_name = None

        await m.edit("⚡ جاري التحميل...")

        # ---------------------------------------
        # التحميل باستخدام yt_dlp
        # ---------------------------------------
        try:
            with YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(link, download=True)
                file_name = ydl.prepare_filename(data)
        except Exception as e:
            await m.edit(f"❌ خطأ أثناء التحميل: {e}")
            remove_if_exists(thumb_name)
            return

        # ---------------------------------------
        # ارسال الملفات
        # ---------------------------------------
        try:
            if is_audio:
                await message.reply_audio(
                    file_name,
                    caption=f"• uploader @{OWNER[0]}",
                    performer=data.get("uploader"),
                    thumb=thumb_name,
                    title=title,
                    duration=duration,
                )
            else:
                await message.reply_video(
                    file_name,
                    caption=data.get("title"),
                    duration=int(data.get("duration", 0)),
                    thumb=thumb_name
                )
        except Exception as e:
            await m.edit(f"❌ خطأ أثناء ارسال الملف: {e}")

    except Exception as e:
        await m.edit(f"❌ حدث خطأ غير متوقع: {e}")

    finally:
        # ---------------------------------------
        # حذف الملفات المؤقتة
        # ---------------------------------------
        remove_if_exists(file_name if 'file_name' in locals() else "")
        remove_if_exists(thumb_name)
        try:
            if m:
                await m.delete()
        except:
            pass
