import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
CallbackQueryHandler,
MessageHandler,
ContextTypes,
filters
)

TOKEN = "8653719430:AAGJr7c4kIpMge3Qj_m4b0ufwBSYCRQQb_g"
DEVELOPER_ID = 7308564874

logging.basicConfig(level=logging.INFO)

anon_waiting = {}
rps_games = {}
xo_games = {}

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if context.args:
        try:
            target = int(context.args[0])
            anon_waiting[user.id] = target
            await update.message.reply_text("💌 اكتب رسالتك الآن")
        except:
            pass
    else:
        link = f"https://t.me/{context.bot.username}?start={user.id}"

        await update.message.reply_text(
            f"""🤖 مرحبا بك في بوت SOLI

💌 رابط صارحني الخاص بك:

{link}

ارسل الرابط لأصدقائك ليصارحوك."""
        )

# ================= استقبال الرسائل =================

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.effective_user.id

    if uid in anon_waiting:

        target = anon_waiting[uid]

        await context.bot.send_message(
            chat_id=target,
            text=f"💌 رسالة مجهولة:\n\n{update.message.text}"
        )

        await update.message.reply_text("✅ تم إرسال الرسالة")

        del anon_waiting[uid]

# ================= RPS =================

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat

    if chat.id in rps_games:
        return

    user = update.effective_user

    kb = [[InlineKeyboardButton("🎮 انضمام", callback_data="rps_join")]]

    await context.bot.send_message(
        chat.id,
        f"🎮 لعبة حجر ورقة مقص\n\n{user.first_name} بدأ التحدي",
        reply_markup=InlineKeyboardMarkup(kb)
    )

    rps_games[chat.id] = {
        "p1": user.id,
        "p2": None,
        "c1": None,
        "c2": None
    }

# ================= RPS BUTTONS =================

async def rps_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    chat = query.message.chat.id

    game = rps_games.get(chat)

    if not game:
        return

    uid = query.from_user.id

    if query.data == "rps_join":

        if uid == game["p1"]:
            return

        game["p2"] = uid

        kb = [[
            InlineKeyboardButton("✊", callback_data="rps_rock"),
            InlineKeyboardButton("✋", callback_data="rps_paper"),
            InlineKeyboardButton("✌️", callback_data="rps_scissors")
        ]]

        await query.edit_message_text(
            "اختر سلاحك 🎮",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data.startswith("rps_"):

        choice = query.data.split("_")[1]

        if uid == game["p1"]:
            game["c1"] = choice

        elif uid == game["p2"]:
            game["c2"] = choice

        if game["c1"] and game["c2"]:

            c1 = game["c1"]
            c2 = game["c2"]

            if c1 == c2:
                result = "🤝 تعادل"

            elif (c1 == "rock" and c2 == "scissors") or \
                 (c1 == "paper" and c2 == "rock") or \
                 (c1 == "scissors" and c2 == "paper"):

                result = "🎉 اللاعب الأول فاز"

            else:
                result = "🎉 اللاعب الثاني فاز"

            await query.edit_message_text(result)

            del rps_games[chat]

# ================= XO =================

async def xo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat

    if chat.id in xo_games:
        return

    kb = [[InlineKeyboardButton("🎮 انضمام XO", callback_data="xo_join")]]

    await context.bot.send_message(
        chat.id,
        "❌⭕ لعبة XO",
        reply_markup=InlineKeyboardMarkup(kb)
    )

    xo_games[chat.id] = {
        "p1": update.effective_user.id,
        "p2": None
    }

# ================= MAIN =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("rps", rps))
app.add_handler(CommandHandler("xo", xo))

app.add_handler(CallbackQueryHandler(rps_buttons, pattern="rps"))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text))

print("🔥 SOLI BOT RUNNING")

app.run_polling()