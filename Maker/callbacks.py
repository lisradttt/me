import traceback
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from Maker.generate import generate_session, ask_ques, buttons_ques

# رسالة الخطأ
ERROR_MESSAGE = """
⚠️ **حدث خطأ أثناء توليد الجلسة**

**الخطأ:** `{}`

📞 **للتواصل:** @ISIIQ
"""


@Client.on_callback_query(filters.regex(pattern=r"^(generate|pyrogram|pyrogram_bot|telethon_bot|telethon)$"))
async def _callbacks(bot: Client, callback_query: CallbackQuery):
    """
    معالج callback queries لتوليد جلسات Pyrogram و Telethon
    """
    query = callback_query.matches[0].group(1)
    
    try:
        # خيار عرض قائمة اختيار نوع الجلسة
        if query == "generate":
            await callback_query.answer()
            await callback_query.message.reply(
                ask_ques, 
                reply_markup=InlineKeyboardMarkup(buttons_ques)
            )
            return
        
        # إعدادات توليد الجلسة لكل نوع
        session_config = {
            "pyrogram": {
                "telethon": False, 
                "is_bot": False
            },
            "pyrogram_bot": {
                "telethon": False, 
                "is_bot": True
            },
            "telethon": {
                "telethon": True, 
                "is_bot": False
            },
            "telethon_bot": {
                "telethon": True, 
                "is_bot": True
            }
        }
        
        # معالجة خيارات توليد الجلسة
        if query in session_config:
            # رسالة تنبيه خاصة لـ pyrogram_bot
            if query == "pyrogram_bot":
                await callback_query.answer(
                    "» ᴛʜᴇ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴡɪʟʟ ʙᴇ ᴏғ ᴩʏʀᴏɢʀᴀᴍ ᴠ2.", 
                    show_alert=True
                )
            else:
                await callback_query.answer()
            
            # توليد الجلسة بالإعدادات المناسبة
            await generate_session(
                bot, 
                callback_query.message, 
                **session_config[query]
            )
    
    except Exception as e:
        # طباعة الخطأ الكامل في الكونسول
        print("=" * 50)
        print("خطأ في معالج الـ callback:")
        print(traceback.format_exc())
        print("=" * 50)
        
        # إرسال رسالة خطأ للمستخدم
        error_text = str(e) if str(e) else "خطأ غير معروف"
        try:
            await callback_query.message.reply(
                ERROR_MESSAGE.format(error_text)
            )
        except Exception as reply_error:
            print(f"فشل في إرسال رسالة الخطأ: {reply_error}")
            # محاولة الرد على الـ callback query نفسه
            await callback_query.answer(
                "حدث خطأ! الرجاء المحاولة مرة أخرى", 
                show_alert=True
            )