import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
DEVELOPER_ID = 7308564874

logging.basicConfig(level=logging.INFO)

anon_waiting = {}

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if context.args:
        try:
            target = int(context.args[0])
            anon_waiting[user.id] = target
            await update.message.reply_text("💌 اكتب رسالتك المجهولة الآن:")
        except:
            pass
    else:
        link = f"https://t.me/{context.bot.username}?start={user.id}"
        await update.message.reply_text(f"🤖 مرحبا بك في بوت SOLI\n\nرابط صارحني الخاص بك:\n{link}")

# ================= استقبال وإرسال الرسائل المجهولة =================
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # الحالة الأولى: مستخدم يرسل رسالة مجهولة لك
    if uid in anon_waiting:
        target = anon_waiting[uid]
        # نرسل لك الرسالة مع "توقيع" مخفي يحتوي على ID المرسل للرد عليه
        await context.bot.send_message(
            chat_id=target,
            text=f"💌 رسالة مجهولة جديدة:\n\n{text}\n\n---\nللرد على هذه الرسالة، استخدم خاصية الرد (Reply) مباشرة."
        )
        # نخزن الـ ID في بيانات الرسالة لتمكين الرد
        context.bot_data[f"reply_to_{target}"] = uid
        await update.message.reply_text("✅ تم إرسال رسالتك بنجاح!")
        del anon_waiting[uid]

    # الحالة الثانية: أنت (المطور) ترد على رسالة مجهولة
    elif uid == DEVELOPER_ID and update.message.reply_to_message:
        target_user_id = context.bot_data.get(f"reply_to_{uid}")
        if target_user_id:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"💬 رد من صاحب الرابط:\n\n{text}"
            )
            await update.message.reply_text("✅ تم إرسال ردك للمرسل.")
        else:
            await update.message.reply_text("❌ عذراً، لا يمكنني العثور على صاحب هذه الرسالة للرد عليه.")

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

print("🔥 SOLI BOT UPDATED & RUNNING")
app.run_polling()
