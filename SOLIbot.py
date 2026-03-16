import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

# --- الإعدادات ---
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot"
DEVELOPER_TAG = "@M_V_EV"

logging.basicConfig(level=logging.INFO)
if 'msg_map' not in globals(): msg_map = {} 

# --- 1. نظام صارحني (بالرد المترابط والوقت) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = f"🤖 أهلاً بك في بوت SOLI\n👨‍💻 المطور: {DEVELOPER_TAG}\n\nأرسل /link للحصول على رابطك."
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 أرسل رسالتك المجهولة الآن..")
            return
        except: pass
    await update.message.reply_text(welcome)

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = f"https://t.me/{BOT_USERNAME}?start={update.effective_user.id}"
    await update.message.reply_text(f"🔗 **رابطك:** `{link}`", parse_mode='Markdown')

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.now(pytz.timezone('Africa/Cairo')).strftime('%Y/%m/%d %I:%M %p')

    if 'talking_to' in context.user_data:
        target_id = context.user_data['talking_to']
        sent = await context.bot.send_message(chat_id=target_id, text=f"📅 {now}\n\n{update.message.text}")
        msg_map[f"to_owner_{sent.message_id}"] = user_id
        await update.message.reply_text("✅ تم الإرسال.")

    elif update.message.reply_to_message:
        reply_id = update.message.reply_to_message.message_id
        original_sender = msg_map.get(f"to_owner_{reply_id}")
        if original_sender:
            # إرسال الرد كمقتبس (Reply) لضمان الترابط
            await context.bot.send_message(
                chat_id=original_sender,
                text=f"💬 رد صاحب الرابط:\n\n{update.message.text}"
            )
            await update.message.reply_text("✅ تم إيصال ردك.")

# --- 2. نظام القوائم (Inline Mode) ---

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.lower()
    uid = update.effective_user.id
    user_name = update.effective_user.first_name

    results = []

    # الحالة الأولى: القائمة الرئيسية (تظهر عند كتابة اليوزر فقط)
    if not query:
        results = [
            InlineQueryResultArticle(
                id="main_xo",
                title="🎮 لعبة XO",
                description="إرسال تحدي XO مباشر",
                input_message_content=InputTextMessageContent(f"🕹 تحدي XO من {user_name}\nمن يتحدى؟ اضغط للبدء!"),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬜", callback_data=f"xo_{i}_{uid}_X") for i in range(j, j+3)] for j in range(0, 9, 3)])
            ),
            InlineQueryResultArticle(
                id="main_rps",
                title="💎 حجرة ورقة مقص",
                description="انقر هنا لاختيار سلاحك (حجرة، ورقة، مقص)",
                input_message_content=InputTextMessageContent(f"قم بكتابة يوزر البوت متبوعاً بكلمة 'لعب' للاختيار:\n\n`@{BOT_USERNAME} لعب`"),
                parse_mode='Markdown'
            )
        ]

    # الحالة الثانية: القائمة الفرعية لحجرة ورقة مقص (تظهر عند كتابة يوزر البوت + كلمة لعب)
    elif query == "لعب":
        choices = [("حجرة 💎", "rock"), ("ورقة 📄", "paper"), ("مقص ✂️", "scissors")]
        for title, code in choices:
            results.append(
                InlineQueryResultArticle(
                    id=f"rps_{code}",
                    title=title,
                    input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {user_name}\nالخصم، اختر سلاحك للهجوم 👇"),
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("💎 حجرة", callback_data=f"res_{code}_{uid}_rock"),
                        InlineKeyboardButton("📄 ورقة", callback_data=f"res_{code}_{uid}_paper"),
                        InlineKeyboardButton("✂️ مقص", callback_data=f"res_{code}_{uid}_scissors")
                    ]])
                )
            )

    await update.inline_query.answer(results, cache_time=0)

# --- 3. معالجة الأزرار (XO و RPS) ---

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    
    if data[0] == "res": # منطق حجرة ورقة مقص
        p1_choice, p1_id, p2_choice = data[1], int(data[2]), data[3]
        if query.from_user.id == p1_id:
            await query.answer("❌ لا يمكنك تحدي نفسك!", show_alert=True)
            return
        
        m = {"rock": "حجرة 💎", "paper": "ورقة 📄", "scissors": "مقص ✂️"}
        rules = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        winner = "p1" if rules[p1_choice] == p2_choice else ("draw" if p1_choice == p2_choice else "p2")
        
        p1_chat = await context.bot.get_chat(p1_id)
        res_txt = f"🏁 النتيجة النهائية:\n👤 {p1_chat.first_name}: {m[p1_choice]}\n👤 {query.from_user.first_name}: {m[p2_choice]}\n\n"
        res_txt += "🤝 تعادل!" if winner == "draw" else f"🏆 الفائز: {p1_chat.first_name if winner == 'p1' else query.from_user.first_name}"
        await query.edit_message_text(res_txt)

    elif data[0] == "xo": # منطق XO (تبديل المربعات)
        index, creator_id, next_turn = int(data[1]), int(data[2]), data[3]
        kb = query.message.reply_markup.inline_keyboard
        row, col = divmod(index, 3)
        if kb[row][col].text != "⬜": return
        
        mark = "❌" if next_turn == "X" else "⭕"
        new_turn = "O" if next_turn == "X" else "X"
        kb[row][col] = InlineKeyboardButton(mark, callback_data=f"xo_{index}_{creator_id}_{new_turn}")
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(kb))

# --- التشغيل ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("link", send_link))
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
app.run_polling()
