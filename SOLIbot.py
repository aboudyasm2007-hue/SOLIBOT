import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# التوكن ومعرف المطور الخاص بك
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
DEVELOPER_ID = 7308564874

logging.basicConfig(level=logging.INFO)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # إذا ضغط المستخدم على رابط (فيه آيدي المطور)
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 بدأت الآن محادثة مجهولة مع صاحب الرابط.\nاكتب رسالتك وسأوصلها له، ويمكنه الرد عليك أيضاً!")
        except:
            pass
    else:
        # إذا فتح المطور أو أي شخص البوت بدون رابط
        link = f"https://t.me/{context.bot.username}?start={user.id}"
        await update.message.reply_text(f"🤖 مرحبا بك في بوت SOLI\n\nرابطك لتلقي الرسائل المجهولة هو:\n{link}")

# ================= نظام المحادثة المستمر =================
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # 1. إذا كان المرسل هو "شخص مجهول" يرسل للمطور
    if 'talking_to' in context.user_data:
        target = context.user_data['talking_to']
        
        # نرسل الرسالة للمطور ونخزن آيدي الشخص المجهول عنده للرد عليه
        sent_msg = await context.bot.send_message(
            chat_id=target,
            text=f"💌 رسالة مجهولة جديدة:\n\n{text}\n\n---\nقم بالرد (Reply) على هذه الرسالة لتستمر المحادثة."
        )
        
        # ربط رسالة المطور بآيدي الشخص المجهول في ذاكرة البوت
        context.bot_data[sent_msg.message_id] = uid
        await update.message.reply_text("✅ تم إرسال رسالتك.")

    # 2. إذا كان "المطور" يرد على رسالة وصلت إليه
    elif uid == DEVELOPER_ID and update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
        
        # البحث عن صاحب الرسالة الأصلية من ذاكرة البوت
        original_sender_id = context.bot_data.get(reply_to_id)
        
        if original_sender_id:
            await context.bot.send_message(
                chat_id=original_sender_id,
                text=f"💬 رد من صاحب الرابط:\n\n{text}"
            )
            await update.message.reply_text("✅ وصل ردك للمجهول.")
        else:
            await update.message.reply_text("❌ عذراً، انتهت صلاحية الرد على هذه الرسالة أو لا يمكن العثور على المرسل.")

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

print("🔥 SOLI CHAT BOT IS RUNNING")
app.run_polling()
