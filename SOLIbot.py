import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

# الإعدادات الأساسية
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot" # المعرف الثابت لحل مشكلة الرابط
DEVELOPER_ID = 7308564874

logging.basicConfig(level=logging.INFO)

# ================= 1. نظام صارحني (حل المشكلة) =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # الدخول عبر رابط صارحني الخاص بك
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 أرسل رسالتك المجهولة الآن، وسيستلمها صاحب الرابط فوراً!")
            return
        except: pass
    
    await update.message.reply_text("🤖 أهلاً بك في بوت SOLI.\nأرسل /link للحصول على رابطك الخاص.")

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إنشاء الرابط باستخدام اليوزر الثابت لضمان عدم حدوث خطأ (Username not found)
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 **رابط صارحني الخاص بك:**\n\n{link}", parse_mode='Markdown')

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    # توجيه الرسالة المجهولة
    if 'talking_to' in context.user_data:
        target = context.user_data['talking_to']
        sent = await context.bot.send_message(chat_id=target, text=f"💌 رسالة مجهولة جديدة:\n\n{text}\n\n---\nرد على هذه الرسالة للتواصل.")
        context.bot_data[sent.message_id] = uid # حفظ هوية المرسل للرد عليه
        await update.message.reply_text("✅ تم إرسال رسالتك بسرية.")
    
    # الرد من صاحب الرابط
    elif update.message.reply_to_message:
        original_sender = context.bot_data.get(update.message.reply_to_message.message_id)
        if original_sender:
            await context.bot.send_message(chat_id=original_sender, text=f"💬 رد من صاحب الرابط:\n\n{text}")
            await update.message.reply_text("✅ تم إرسال ردك.")

# ================= 2. نظام الألعاب (XO و RPS) =================

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    uid = update.effective_user.id
    
    results = [
        # خيار XO المضاف حديثاً
        InlineQueryResultArticle(
            id="xo", title="🎮 لعبة XO",
            input_message_content=InputTextMessageContent(f"🕹 تحدي XO من {user_name}\nاللاعب الثاني، اضغط للبدء 👇"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬜", callback_data=f"xo_0_{uid}"), InlineKeyboardButton("⬜", callback_data=f"xo_1_{uid}"), InlineKeyboardButton("⬜", callback_data=f"xo_2_{uid}")],
                [InlineKeyboardButton("⬜", callback_data=f"xo_3_{uid}"), InlineKeyboardButton("⬜", callback_data=f"xo_4_{uid}"), InlineKeyboardButton("⬜", callback_data=f"xo_5_{uid}")],
                [InlineKeyboardButton("⬜", callback_data=f"xo_6_{uid}"), InlineKeyboardButton("⬜", callback_data=f"xo_7_{uid}"), InlineKeyboardButton("⬜", callback_data=f"xo_8_{uid}")]
            ])
        ),
        # خيار حجرة ورقة مقص (حجرة)
        InlineQueryResultArticle(
            id="r", title="💎 حجرة",
            input_message_content=InputTextMessageContent(f"⚔️ {user_name} اختار سلاحه! اختر سلاحك للهجوم 👇"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💎 حجرة", callback_data=f"res_rock_{uid}_rock"),
                InlineKeyboardButton("📄 ورقة", callback_data=f"res_rock_{uid}_paper"),
                InlineKeyboardButton("✂️ مقص", callback_data=f"res_rock_{uid}_scissors")
            ]])
        )
    ]
    await update.inline_query.answer(results, cache_time=1)

# ================= 3. التشغيل =================

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", send_link))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    print("🚀 البوت يعمل الآن.. تم إصلاح الرابط وإضافة الألعاب.")
    app.run_polling()
