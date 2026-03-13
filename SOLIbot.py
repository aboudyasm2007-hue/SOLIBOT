import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot"

logging.basicConfig(level=logging.INFO)

# --- نظام الألعاب (Inline) ---
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id="xo",
            title="لعبة XO 🎮",
            description="اضغط هنا لإرسال تحدي XO",
            input_message_content=InputTextMessageContent(f"🕹 تحدي XO جديد من {update.effective_user.first_name}\nمن يقبل التحدي؟"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ابدأ اللعب ! 🎮", callback_data="xo_init")]])
        ),
        InlineQueryResultArticle(
            id="rps",
            title="حجرة ورقة مقص ✂️",
            description="اضغط هنا لإرسال تحدي حجرة ورقة مقص",
            input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {update.effective_user.first_name}"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("انضمام للتحدي ⚔️", callback_data="rps_init")]])
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

# --- تشغيل البوت ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(InlineQueryHandler(inline_query))
    # أضف هنا باقي أوامر الـ start والـ link السابقة
    app.run_polling()
