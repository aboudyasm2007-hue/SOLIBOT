import logging
from datetime import datetime
import pytz # تأكد من إضافة pytz في ملف requirements.txt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

# الإعدادات
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot"

logging.basicConfig(level=logging.INFO)

# قاموس لحفظ العلاقات بين الرسائل للرد المترابط
# نستخدم bot_data لضمان بقاء البيانات حتى لو توقف البوت مؤقتاً
if 'msg_map' not in globals():
    msg_map = {}

# --- 1. نظام صارحني المطور ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 أرسل رسالتك المجهولة الآن..")
            return
        except: pass
    await update.message.reply_text("🤖 أهلاً بك في بوت SOLI.\nأرسل /link للحصول على رابطك.")

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 **رابط صارحني الخاص بك:**\n\n`{link}`", parse_mode='Markdown')

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # الحصول على الوقت الحالي بتوقيت ليبيا/مصر (أو توقيتك المحلي)
    now = datetime.now(pytz.timezone('Africa/Cairo')).strftime('%Y/%m/%d %I:%M %p')

    # أ. إرسال رسالة مجهولة لصاحب الرابط
    if 'talking_to' in context.user_data:
        target_id = context.user_data['talking_to']
        formatted_msg = f"📅 {now}\n\n{text}"
        
        try:
            sent_msg = await context.bot.send_message(chat_id=target_id, text=formatted_msg)
            # ربط الرسالة المرسلة بهوية الراسل الأصلي
            msg_map[sent_msg.message_id] = user_id
            await update.message.reply_text("✅ تم إرسال رسالتك بنجاح.")
        except Exception as e:
            await update.message.reply_text("❌ حدث خطأ، ربما صاحب الرابط قام بحظر البوت.")

    # ب. الرد المترابط (Reply) من صاحب الرابط
    elif update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
        original_sender_id = msg_map.get(reply_to_id)
        
        if original_sender_id:
            try:
                # الرد يصل للمستخدم مجهول الهوية مربوطاً برسالته الأصلية
                await context.bot.send_message(
                    chat_id=original_sender_id,
                    text=f"💬 رد جديد من صاحب الرابط:\n\n{text}"
                )
                await update.message.reply_text("✅ تم إرسال ردك بنجاح.")
            except Exception as e:
                await update.message.reply_text("❌ تعذر إيصال الرد.")
        else:
            await update.message.reply_text("⚠️ لا يمكنني العثور على صاحب هذه الرسالة (قديمة جداً).")

# --- 2. نظام الألعاب (Inline) ---
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    results = [
        InlineQueryResultArticle(
            id="xo", title="🎮 لعبة XO",
            input_message_content=InputTextMessageContent(f"🕹 تحدي XO جديد!\nاضغط على المربعات للعب 👇"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬜", callback_data=f"x_0_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_1_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_2_{uid}")],
                [InlineKeyboardButton("⬜", callback_data=f"x_3_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_4_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_5_{uid}")],
                [InlineKeyboardButton("⬜", callback_data=f"x_6_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_7_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_8_{uid}")]
            ])
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

# --- التشغيل ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", send_link))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    app.run_polling()
