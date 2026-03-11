import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# الإعدادات الأساسية
TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
DEVELOPER_ID = 7308564874
BOT_USERNAME = "SOLI_7_bot"

logging.basicConfig(level=logging.INFO)

# تخزين بيانات الألعاب والمحادثات
games = {}

# ================= الأوامر الأساسية =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        try:
            target = int(context.args[0])
            context.user_data['talking_to'] = target
            await update.message.reply_text("💌 بدأت الآن محادثة مجهولة.\nاكتب رسالتك وسأوصلها لصاحب الرابط!")
            return
        except: pass
    
    about = "🤖 **مرحباً بك في بوت SOLI**\n\nبواسطة هذا البوت يمكنك:\n1️⃣ استقبال رسائل مجهولة والرد عليها.\n2️⃣ لعب XO وحجرة ورقة مقص مع أصدقائك.\n\n📌 للحصول على رابطك: /link"
    await update.message.reply_text(about, parse_mode='Markdown')

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"🔗 **رابط صارحني الخاص بك:**\n\n{link}", parse_mode='Markdown')

# ================= نظام المحادثة المجهولة =================

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text

    if 'talking_to' in context.user_data:
        target = context.user_data['talking_to']
        sent = await context.bot.send_message(chat_id=target, text=f"💌 رسالة مجهولة:\n\n{text}\n\n---\nرد على الرسالة للاستمرار.")
        context.bot_data[sent.message_id] = uid
        await update.message.reply_text("✅ تم الإرسال.")
    
    elif uid == DEVELOPER_ID and update.message.reply_to_message:
        original_sender = context.bot_data.get(update.message.reply_to_message.message_id)
        if original_sender:
            await context.bot.send_message(chat_id=original_sender, text=f"💬 رد من صاحب الرابط:\n\n{text}")
            await update.message.reply_text("✅ تم إرسال ردك.")

# ================= لعبة حجرة ورقة مقص (RPS) =================

async def rps_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("انضمام للعبة 🎮", callback_data="rps_join")]]
    await update.message.reply_text(f"🎮 **تحدي حجرة ورقة مقص!**\nمن يتحدى {update.effective_user.first_name}؟", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))

async def rps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    
    if query.data == "rps_join":
        keyboard = [
            [InlineKeyboardButton("💎 حجرة", callback_data="rps_rock"),
             InlineKeyboardButton("📄 ورقة", callback_data="rps_paper"),
             InlineKeyboardButton("✂️ مقص", callback_data="rps_scissors")]
        ]
        await query.edit_message_text("اختر سلاحك الآن! 🔥", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data.startswith("rps_"):
        choice = query.data.split("_")[1]
        bot_choice = random.choice(["rock", "paper", "scissors"])
        # (تبسيط النتيجة هنا للسرعة)
        res = "تعادل! 🤝" if choice == bot_choice else "لقد لعبتُ جيداً! 😎"
        await query.edit_message_text(f"أنت اخترت: {choice}\nأنا اخترت: {bot_choice}\n\nالنتيجة: {res}")

# ================= لعبة XO =================

async def xo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = [" "]*9
    games[update.message.message_id] = {"board": board, "turn": "X"}
    keyboard = []
    for i in range(0, 9, 3):
        keyboard.append([InlineKeyboardButton("⬜", callback_data=f"xo_{i}"),
                         InlineKeyboardButton("⬜", callback_data=f"xo_{i+1}"),
                         InlineKeyboardButton("⬜", callback_data=f"xo_{i+2}")])
    await update.message.reply_text("🎮 لعبة XO الجديدة:\nدور اللاعب X", reply_markup=InlineKeyboardMarkup(keyboard))

# (يمكن إضافة معالج Callback لـ XO هنا بنفس الطريقة)

# ================= التشغيل =================

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("link", send_link))
app.add_handler(CommandHandler("rps", rps_command))
app.add_handler(CommandHandler("xo", xo_command))
app.add_handler(CallbackQueryHandler(rps_callback, pattern="^rps_"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

print("🚀 SOLI BOT IS LIVE WITH GAMES & CHAT")
app.run_polling()
