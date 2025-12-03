from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Привет! Я - ваш трекер привычек. Я помогаю развивать хорошие привычки и бороть плохие. Выберите нужную (или не нужную) вам привычку и считайте, что она уже в вас есть (или что ее уже нет: тут по ситуации)", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text()

async def echo (update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text()

app = ApplicationBuilder().token("8535688484:AAGmPuUIqnEllSx6B3abKx1Rqwy__VQLSHM").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

app.run_polling()