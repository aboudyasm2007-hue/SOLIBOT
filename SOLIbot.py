import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters
)

# الإعدادات
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
DEVELOPER_ID = 7308564874
BOT_USERNAME = "SOLI_7_bot" # تم التثبيت لحل مشكلة الرابط

logging.basicConfig(level=logging.INFO)
games = {}

# ================= أوامر البوت =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args: # الدخول عبر رابط صارحني
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 اكتب رسالتك المجهولة الآن، وسيتمكن صاحب الرابط من الرد عليك!")
            return
        except: pass
    
    await update.message.reply_text(
        "🤖 **أهلاً بك في بوت SOLI المطور**\n\n"
        "🎮 ألعاب (XO - حجرة ورقة مقص) ضد لاعبين حقيقيين.\n"
        "💌 رسائل مجهولة مع نظام رد مستمر.\n\n"
        "🔗 للحصول على رابطك الخاص: /link", parse_mode='Markdown'
    )

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # استخدام اليوزر المثبت لضمان عدم ظهور خطأ "لم يتم العثور على اسم المستخدم"
    link = f"https://t.me/{BOT_USERNAME}?start={update.effective_user.id}"
    await update.message.reply_text(f"🔗 **رابط صارحني الخاص بك:**\n\n{link}", parse_mode='Markdown')

# ================= نظام صارحني (محادثة مستمرة) =================

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if 'talking_to' in context.user_data:
        target = context.user_data['talking_to']
        sent = await context.bot.send_message(chat_id=target, text=f"💌 رسالة مجهولة:\n\n{text}\n\n---\nاستخدم (Reply) للرد.")
        context.bot_data[sent.message_id] = uid
        await update.message.reply_text("✅ تم إرسال رسالتك.")
    
    elif update.message.reply_to_message:
        original_sender = context.bot_data.get(update.message.reply_to_message.message_id)
        if original_sender:
            await context.bot.send_message(chat_id=original_sender, text=f"💬 رد من صاحب الرابط:\n\n{text}")
            await update.message.reply_text("✅ وصل ردك للمجهول.")

# ================= نظام الألعاب (Inline Mode) مثل الصور =================

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id="xo_game",
            title="لعبة XO 🎮",
            input_message_content=InputTextMessageContent(f"🕹 تحدي XO من {update.effective_user.first_name}\nانقر على الزر أدناه للبدء 👇"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ابدأ اللعب ! 🎮", callback_data="xo_init")]])
        ),
        InlineQueryResultArticle(
            id="rps_game",
            title="حجرة ورقة مقص ✂️",
            input_message_content=InputTextMessageContent(f"💎 تحدي حجرة ورقة مقص من {update.effective_user.first_name}"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("انضمام للتحدي ⚔️", callback_data="rps_init")]])
        )
    ]
    await update.inline_query.answer(results)

# ================= معالجة الأزرار (Callback) =================

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    # هنا يتم وضع منطق اللعبة (XO و RPS) لتبديل الأزرار عند الضغط عليها
    if query.data == "xo_init":
        board = ["⬜"] * 9
        keyboard = []
        for i in range(0, 9, 3):
            keyboard.append([InlineKeyboardButton(board[i], callback_data=f"xo_{i}"),
                             InlineKeyboardButton(board[i+1], callback_data=f"xo_{i+1}"),
                             InlineKeyboardButton(board[i+2], callback_data=f"xo_{i+2}")])
        await query.edit_message_text("🎮 لعبة XO: دور اللاعب الأول (X)", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= التشغيل النهائي =================

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("link", send_link))
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(CallbackQueryHandler(handle_callbacks))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

app.run_polling()
