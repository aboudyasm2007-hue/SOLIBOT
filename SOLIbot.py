import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, ContextTypes, filters

# --- الإعدادات الأساسية ---
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
BOT_USERNAME = "SOLI_7_bot"
DEVELOPER_TAG = "@M_V_EV"

logging.basicConfig(level=logging.INFO)

# تخزين مؤقت للبيانات
if 'msg_map' not in globals(): msg_map = {}
if 'xo_games' not in globals(): xo_games = {}

# --- 1. نظام صارحني (مطور) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # رسالة البداية مع وسم المطور
    welcome_text = (
        f"🤖 أهلاً بك في بوت SOLI\n"
        f"👨‍💻 المطور: {DEVELOPER_TAG}\n\n"
        f"استخدم /link للحصول على رابطك الخاص."
    )
    
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 أرسل رسالتك المجهولة الآن..")
            return
        except: pass
    
    await update.message.reply_text(welcome_text)

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 **رابط صارحني الخاص بك:**\n\n`{link}`", parse_mode='Markdown')

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    now = datetime.now(pytz.timezone('Africa/Cairo')).strftime('%Y/%m/%d %I:%M %p')

    if 'talking_to' in context.user_data:
        target_id = context.user_data['talking_to']
        sent_msg = await context.bot.send_message(chat_id=target_id, text=f"{now}\n{text}")
        msg_map[sent_msg.message_id] = user_id
        await update.message.reply_text("✅ تم الإرسال.")

    elif update.message.reply_to_message:
        original_sender = msg_map.get(update.message.reply_to_message.message_id)
        if original_sender:
            await context.bot.send_message(chat_id=original_sender, text=f"💬 رد صاحب الرابط:\n\n{text}", reply_to_message_id=None)
            await update.message.reply_text("✅ تم إرسال ردك.")

# --- 2. نظام الألعاب (Inline Mode) ---

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    uid = update.effective_user.id
    
    # لوحة XO فارغة للبداية
    def get_xo_kb():
        return [[InlineKeyboardButton("⬜", callback_data=f"xo_{i}_{uid}_X") for i in range(j, j+3)] for j in range(0, 9, 3)]

    results = [
        InlineQueryResultArticle(
            id="xo", title="🎮 لعبة XO",
            input_message_content=InputTextMessageContent(f"🕹 تحدي XO من {user_name}\nاللاعب الثاني، ابدأ حركتك الأولى (X) 👇"),
            reply_markup=InlineKeyboardMarkup(get_xo_kb())
        ),
        InlineQueryResultArticle(
            id="rps", title="💎 حجرة ورقة مقص",
            input_message_content=InputTextMessageContent(f"⚔️ تحدي حجرة ورقة مقص من {user_name}\nالخصم، اختر سلاحك للهجوم 👇"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💎 حجرة", callback_data=f"res_rock_{uid}_rock"),
                InlineKeyboardButton("📄 ورقة", callback_data=f"res_rock_{uid}_paper"),
                InlineKeyboardButton("✂️ مقص", callback_data=f"res_rock_{uid}_scissors")
            ]])
        )
    ]
    await update.inline_query.answer(results, cache_time=0)

# --- 3. معالجة حركات الألعاب ---

async def game_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")
    user = query.from_user

    # حجرة ورقة مقص
    if data[0] == "res":
        p1_choice, p1_id, p2_choice = data[1], int(data[2]), data[3]
        if user.id == p1_id:
            await query.answer("❌ لا يمكنك تحدي نفسك!", show_alert=True)
            return
        
        m = {"rock": "حجرة 💎", "paper": "ورقة 📄", "scissors": "مقص ✂️"}
        p1_name = "اللاعب الأول"
        try: p1_name = (await context.bot.get_chat(p1_id)).first_name
        except: pass

        winner = "draw" if p1_choice == p2_choice else ("p1" if (p1_choice == "rock" and p2_choice == "scissors") or (p1_choice == "paper" and p2_choice == "rock") or (p1_choice == "scissors" and p2_choice == "paper") else "p2")
        
        res = f"🏁 انتهت اللعبة!\n👤 {p1_name}: {m[p1_choice]}\n👤 {user.first_name}: {m[p2_choice]}\n\n"
        res += "🤝 تعادل!" if winner == "draw" else f"🏆 الفائز: {p1_name if winner == 'p1' else user.first_name}"
        await query.edit_message_text(res)

    # XO (منطق التبديل)
    elif data[0] == "xo":
        index, creator_id, current_turn = int(data[1]), int(data[2]), data[3]
        if user.id == creator_id and current_turn == "X": # منع منشئ اللعبة من اللعب أولاً إذا كان هو من أرسل التحدي
             await query.answer("انتظر اللاعب الثاني ليبدأ!", show_alert=True)
             return
        
        kb = query.message.reply_markup.inline_keyboard
        row, col = divmod(index, 3)
        
        if kb[row][col].text != "⬜":
            await query.answer("المربع مشغول!", show_alert=True)
            return

        new_mark = "❌" if current_turn == "X" else "⭕"
        next_turn = "O" if current_turn == "X" else "X"
        kb[row][col] = InlineKeyboardButton(new_mark, callback_data=f"xo_{index}_{creator_id}_{next_turn}")
        
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(kb))

# --- تشغيل ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("link", send_link))
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(game_callbacks))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    app.run_polling()
