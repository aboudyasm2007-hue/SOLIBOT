import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)

# الإعدادات
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
DEVELOPER_ID = 7308564874
BOT_USERNAME = "SOLI_7_bot"

logging.basicConfig(level=logging.INFO)

# تخزين البيانات
games = {} # لتخزين حالات الألعاب

# ================= أوامر البوت =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # إذا كان الدخول عبر رابط صارحني
    if context.args:
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
    
    elif uid == DEVELOPER_ID and update.message.reply_to_message:
        original_sender = context.bot_data.get(update.message.reply_to_message.message_id)
        if original_sender:
            await context.bot.send_message(chat_id=original_sender, text=f"💬 رد من صاحب الرابط:\n\n{text}")
            await update.message.reply_text("✅ وصل ردك للمجهول.")

# ================= لعبة حجرة ورقة مقص (لاعب ضد لاعب) =================

async def rps_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("تحدي! 🎮", callback_data="rps_join")]]
    await update.message.reply_text(f"🕹 **تحدي حجرة ورقة مقص!**\nاللاعب: {update.effective_user.first_name} ينتظر خصماً..", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))

async def rps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    uid = query.from_user.id
    msg_id = query.message.message_id

    if query.data == "rps_join":
        if msg_id not in games:
            games[msg_id] = {'p1': None, 'p2': None, 'choices': {}}
        
        keyboard = [
            [InlineKeyboardButton("💎 حجرة", callback_data="p_rock"),
             InlineKeyboardButton("📄 ورقة", callback_data="p_paper"),
             InlineKeyboardButton("✂️ مقص", callback_data="p_scissors")]
        ]
        await query.edit_message_text("اختاروا أسلحتكم! (لن يظهر اختيارك للخصم) 🔥", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("p_"):
        choice = query.data.split("_")[1]
        if msg_id not in games: return
        
        games[msg_id]['choices'][uid] = choice
        
        if len(games[msg_id]['choices']) == 1:
            await query.answer("تم تسجيل اختيارك! بانتظار الخصم...", show_alert=True)
        elif len(games[msg_id]['choices']) == 2:
            players = list(games[msg_id]['choices'].keys())
            c1, c2 = games[msg_id]['choices'][players[0]], games[msg_id]['choices'][players[1]]
            # تحديد الفائز (منطق مبسط)
            res = "انتهت اللعبة! تفقدوا الاختيارات."
            await query.edit_message_text(f"🏁 النتيجة:\nاللاعب 1: {c1}\nاللاعب 2: {c2}")
            del games[msg_id]

# ================= لعبة XO (لاعب ضد لاعب) =================

async def xo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = ["⬜"] * 9
    keyboard = []
    for i in range(0, 9, 3):
        keyboard.append([InlineKeyboardButton(board[i], callback_data=f"xo_{i}"),
                         InlineKeyboardButton(board[i+1], callback_data=f"xo_{i+1}"),
                         InlineKeyboardButton(board[i+2], callback_data=f"xo_{i+2}")])
    await update.message.reply_text("🎮 تحدي XO: دور اللاعب X", reply_markup=InlineKeyboardMarkup(keyboard))

# ================= التشغيل النهائي =================

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("link", send_link))
app.add_handler(CommandHandler("rps", rps_start))
app.add_handler(CommandHandler("xo", xo_start))
app.add_handler(CallbackQueryHandler(rps_callback, pattern="^(rps_|p_|xo_)"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

print("🚀 SOLI BOT IS READY FOR ACTION!")
app.run_polling()
