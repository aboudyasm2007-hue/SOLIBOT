import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot"

logging.basicConfig(level=logging.INFO)

# منطق تحديد الفائز
def get_winner(p1_choice, p2_choice):
    if p1_choice == p2_choice: return None
    rules = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    return "p1" if rules[p1_choice] == p2_choice else "p2"

# --- نظام الألعاب (Inline Mode) ---
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # عند كتابة يوزر البوت، تظهر له الخيارات الثلاثة ليختار سلاحه السري
    results = [
        InlineQueryResultArticle(
            id="r", title="💎 حجرة",
            input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {update.effective_user.first_name}\nاللاعب الثاني، اختر سلاحك للهجوم 👇"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 حجرة", callback_data=f"res_rock_{update.effective_user.id}_rock"),
                 InlineKeyboardButton("📄 ورقة", callback_data=f"res_rock_{update.effective_user.id}_paper"),
                 InlineKeyboardButton("✂️ مقص", callback_data=f"res_rock_{update.effective_user.id}_scissors")]
            ])
        ),
        InlineQueryResultArticle(
            id="p", title="📄 ورقة",
            input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {update.effective_user.first_name}\nاللاعب الثاني، اختر سلاحك للهجوم 👇"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 حجرة", callback_data=f"res_paper_{update.effective_user.id}_rock"),
                 InlineKeyboardButton("📄 ورقة", callback_data=f"res_paper_{update.effective_user.id}_paper"),
                 InlineKeyboardButton("✂️ مقص", callback_data=f"res_paper_{update.effective_user.id}_scissors")]
            ])
        ),
        InlineQueryResultArticle(
            id="s", title="✂️ مقص",
            input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {update.effective_user.first_name}\nاللاعب الثاني، اختر سلاحك للهجوم 👇"),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💎 حجرة", callback_data=f"res_scissors_{update.effective_user.id}_rock"),
                 InlineKeyboardButton("📄 ورقة", callback_data=f"res_scissors_{update.effective_user.id}_paper"),
                 InlineKeyboardButton("✂️ مقص", callback_data=f"res_scissors_{update.effective_user.id}_scissors")]
            ])
        )
    ]
    await update.inline_query.answer(results, cache_time=1)

# --- معالجة النتيجة مباشرة ---
async def handle_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_") # res, p1_choice, p1_id, p2_choice
    
    p1_choice = data[1]
    p1_id = int(data[2])
    p2_id = query.from_user.id
    p2_name = query.from_user.first_name
    p2_choice = data[3]

    if p2_id == p1_id:
        await query.answer("❌ لا يمكنك تحدي نفسك!", show_alert=True)
        return

    # الحصول على اسم اللاعب الأول
    try:
        p1_chat = await context.bot.get_chat(p1_id)
        p1_name = p1_chat.first_name
    except:
        p1_name = "اللاعب الأول"

    winner = get_winner(p1_choice, p2_choice)
    names = {"rock": "حجرة 💎", "paper": "ورقة 📄", "scissors": "مقص ✂️"}
    
    final_text = (
        f"🏁 **انتهت اللعبة!**\n\n"
        f"👤 {p1_name}: {names[p1_choice]}\n"
        f"👤 {p2_name}: {names[p2_choice]}\n\n"
    )
    
    if winner == "p1":
        final_text += f"🏆 الفائز: {p1_name}\n💀 الخاسر: {p2_name}"
    elif winner == "p2":
        final_text += f"🏆 الفائز: {p2_name}\n💀 الخاسر: {p1_name}"
    else:
        final_text += "🤝 النتيجة: تعادل!"
        
    await query.edit_message_text(final_text, parse_mode='Markdown')

# --- التشغيل ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(CallbackQueryHandler(handle_result, pattern="^res_"))
app.run_polling()
