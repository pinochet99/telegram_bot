import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

async def ask_deepseek(user_message):
    try:
        response = requests.post(
            url="https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "Ты — консультант по дизайну и рекламе. Отвечай на русском языке, кратко и по делу."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Ошибка API: {response.status_code}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 Графические решения", callback_data="graphic")],
        [InlineKeyboardButton("📊 Визуальные стратегии", callback_data="visual")],
        [InlineKeyboardButton("📣 Рекламные стратегии", callback_data="advert")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Доброго дня! Я бот A-Групп Дизайн. Чем могу помочь? Мы осуществляем:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "graphic":
        await query.edit_message_text("🎨 **Графические решения:** Разработка фирменного стиля, логотипов, упаковки и полиграфии.", reply_markup=query.message.reply_markup)
    elif query.data == "visual":
        await query.edit_message_text("📊 **Визуальные стратегии:** Создаём целостную систему визуальной коммуникации для вашего бренда.", reply_markup=query.message.reply_markup)
    elif query.data == "advert":
        await query.edit_message_text("📣 **Рекламные стратегии:** Разрабатываем эффективные рекламные кампании для привлечения вашей аудитории.", reply_markup=query.message.reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message:
        return
    if user_message.lower() in ["привет", "здравствуйте", "добрый день"]:
        await start(update, context)
        return
    reply = await ask_deepseek(user_message)
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
