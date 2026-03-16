import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

# الإعدادات - تم تعديل اليوزر ليكون دقيقاً جداً
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot"  # تأكد أن هذا اليوزر هو نفسه في BotFather

logging.basicConfig(level=logging.INFO)
bot_data_store = {}

# --- 1. إصلاح رابط صارحني ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 اكتب رسالتك المجهولة الآن، وسيتمكن صاحب الرابط من الرد عليك!")
            return
        except: pass
    await update.message.reply_text("🤖 أهلاً بك في بوت SOLI.\nاستخدم /link للحصول على رابطك الخاص.")

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # هذا السطر يضمن ظهور الرابط بالشرطات بشكل صحيح
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 **رابط صارحني الخاص بك:**\n\n`{link}`", parse_mode='Markdown')

# --- 2. نظام الألعاب (إضافة XO و RPS للقائمة) ---
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    uid = update.effective_user.id
    
    results = [
        # خيار لعبة XO
        InlineQueryResultArticle(
            id="xo_game", title="🎮 لعبة XO",
            description="إرسال تحدي XO مباشر",
            input_message_content=InputTextMessageContent(f"🕹 تحدي XO من {user_name}\nمن يتحدى؟ اضغط على مربع للبدء!"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬜", callback_data=f"x_0_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_1_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_2_{uid}")],
                [InlineKeyboardButton("⬜", callback_data=f"x_3_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_4_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_5_{uid}")],
                [InlineKeyboardButton("⬜", callback_data=f"x_6_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_7_{uid}"), InlineKeyboardButton("⬜", callback_data=f"x_8_{uid}")]
            ])
        ),
        # خيار حجرة ورقة مقص
        InlineQueryResultArticle(
            id="rps_direct", title="💎 حجرة ورقة مقص",
            description="إرسال تحدي مباشر بـ 3 أزرار",
            input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {user_name}\nالخصم، اختر سلاحك فوراً 👇"),
            reply_markup=InlineKeyboardMarkup([[ 
                InlineKeyboardButton("💎 حجرة", callback_data=f"res_rock_{uid}_rock"),
                InlineKeyboardButton("📄 ورقة", callback_data=f"res_rock_{uid}_paper"),
                InlineKeyboardButton("✂️ مقص", callback_data=f"res_rock_{uid}_scissors")
            ]])
        )
    ]
    await update.inline_query.answer(results, cache_time=1)

# --- 3. معالجة الرسائل والردود ---
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'talking_to' in context.user_data:
        target = context.user_data['talking_to']
        sent = await context.bot.send_message(chat_id=target, text=f"💌 رسالة مجهولة:\n\n{update.message.text}\n\n(استخدم Reply للرد)")
        bot_data_store[sent.message_id] = update.effective_user.id
        await update.message.reply_text("✅ أرسلت!")
    elif update.message.reply_to_message:
        original = bot_data_store.get(update.message.reply_to_message.message_id)
        if original:
            await context.bot.send_message(chat_id=original, text=f"💬 رد صاحب الرابط:\n\n{update.message.text}")
            await update.message.reply_text("✅ وصل ردك.")

# --- 4. تشغيل البوت ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("link", send_link))
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
app.add_handler(CallbackQueryHandler(lambda u, c: None)) # لتجنب أخطاء الأزرار مؤقتاً

app.run_polling()
