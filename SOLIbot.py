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

# ================= START (نبذة عن البوت) =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إذا دخل المستخدم عبر رابط مجهول (يحتوي على آيدي)
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 بدأت الآن محادثة مجهولة.\nاكتب رسالتك وسأوصلها لصاحب الرابط، ويمكنه الرد عليك أيضاً!")
            return
        except:
            pass
    
    # رسالة نبذة عن البوت عند استخدام /start بدون رابط
    about_text = (
        "🤖 **مرحباً بك في بوت SOLI**\n\n"
        "هذا البوت يتيح لك استقبال رسائل مجهولة الهوية من أصدقائك ومتابعينك "
        "مع إمكانية الرد عليهم مباشرة ودخول محادثة مستمرة.\n\n"
        "📌 **للحصول على رابطك الخاص، أرسل الأمر:** /link"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

# ================= LINK (الحصول على الرابط) =================
async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    link = f"https://t.me/{context.bot.username}?start={user.id}"
    
    response_text = (
        f"🔗 **رابط صارحني الخاص بك هو:**\n\n"
        f"{link}\n\n"
        f"قم بنشر هذا الرابط في قناتك أو على حساباتك لتلقي الرسائل المجهولة."
    )
    await update.message.reply_text(response_text, parse_mode='Markdown')

# ================= نظام المحادثة المستمر =================
async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # 1. إذا كان المرسل هو "شخص مجهول" يرسل للمطور أو صاحب الرابط
    if 'talking_to' in context.user_data:
        target = context.user_data['talking_to']
        
        sent_msg = await context.bot.send_message(
            chat_id=target,
            text=f"💌 رسالة مجهولة جديدة:\n\n{text}\n\n---\nقم بالرد (Reply) على هذه الرسالة لتستمر المحادثة."
        )
        
        context.bot_data[sent_msg.message_id] = uid
        await update.message.reply_text("✅ تم إرسال رسالتك.")

    # 2. إذا كان "المطور" يرد على رسالة وصلت إليه
    elif uid == DEVELOPER_ID and update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
        original_sender_id = context.bot_data.get(reply_to_id)
        
        if original_sender_id:
            await context.bot.send_message(
                chat_id=original_sender_id,
                text=f"💬 رد من صاحب الرابط:\n\n{text}"
            )
            await update.message.reply_text("✅ وصل ردك للمجهول.")
        else:
            await update.message.reply_text("❌ عذراً، لا يمكنني العثور على المرسل للرد عليه.")

# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("link", send_link))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

print("🔥 SOLI BOT UPDATED WITH /LINK COMMAND")
app.run_polling()
