import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, ConversationHandler

# --- ТОКЕНЫ И НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8833699342:AAGud8WsyHej9LtI5d6xkDRo3xoLSm2hqPg"
OPENROUTER_API_KEY = "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"
OWNER_CHAT_ID = 63938809

# --- СОСТОЯНИЯ ДЛЯ ОПРОСОВ ---
BOOKLET_FORMAT, BOOKLET_COLOR, BOOKLET_PAPER, BOOKLET_PRINT = range(4)
CATALOG_FORMAT, CATALOG_COLOR, CATALOG_PAGES, CATALOG_COVER, CATALOG_BLOCK, CATALOG_PRINT = range(6)

# --- ФУНКЦИЯ ЗАПРОСА К OPENROUTER (БЕСПЛАТНАЯ МОДЕЛЬ) ---
async def ask_openrouter(user_message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://t.me/a_group_1",
                "X-Title": "A_Group",
                "Content-Type": "application/json",
            },
            json={
                "model": "google/gemini-2.0-flash-lite:free",  # БЕСПЛАТНАЯ МОДЕЛЬ!
                "messages": [
                    {"role": "system", "content": "Ты — консультант по дизайну и рекламе. Отвечай на русском языке, кратко и по делу."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            # Если модель недоступна — пробуем другую бесплатную
            return await ask_openrouter_fallback(user_message)
    except Exception as e:
        return await ask_openrouter_fallback(user_message)

# --- ЗАПАСНАЯ БЕСПЛАТНАЯ МОДЕЛЬ ---
async def ask_openrouter_fallback(user_message):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://t.me/a_group_1",
                "X-Title": "A_Group",
                "Content-Type": "application/json",
            },
            json={
                "model": "microsoft/phi-3-medium-128k-instruct:free",  # Запасная бесплатная модель
                "messages": [
                    {"role": "system", "content": "Ты — консультант по дизайну и рекламе. Отвечай на русском языке, кратко и по делу."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return "Извините, я ещё учусь. Попробуйте переформулировать вопрос или спросить что-то другое."
    except Exception as e:
        return "Извините, временная ошибка. Пожалуйста, попробуйте позже."

# --- КОМАНДА /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎨 Графические решения", callback_data="graphic")],
        [InlineKeyboardButton("📊 Визуальные стратегии", callback_data="visual")],
        [InlineKeyboardButton("📣 Рекламные стратегии", callback_data="advert")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Доброго дня! Я бот A_Group. Чем могу помочь? Мы осуществляем:",
        reply_markup=reply_markup
    )

# --- ОБРАБОТЧИК КНОПОК МЕНЮ ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "graphic":
        await query.edit_message_text("🎨 **Графические решения:** разработка фирменного стиля, логотипов, упаковки и полиграфии.", reply_markup=query.message.reply_markup, parse_mode="Markdown")
    elif query.data == "visual":
        await query.edit_message_text("📊 **Визуальные стратегии:** создаём целостную систему визуальной коммуникации для вашего бренда.", reply_markup=query.message.reply_markup, parse_mode="Markdown")
    elif query.data == "advert":
        await query.edit_message_text("📣 **Рекламные стратегии:** разрабатываем эффективные рекламные кампании для привлечения вашей аудитории.", reply_markup=query.message.reply_markup, parse_mode="Markdown")

# --- ОТВЕТ НА ЛЮБОЕ СООБЩЕНИЕ ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message:
        return
    
    # Приветствия
    if user_message.lower() in ["привет", "здравствуйте", "добрый день", "доброго дня", "доброе утро", "добрый вечер"]:
        await start(update, context)
        return
    
    # Заказ буклета
    if user_message.lower() in ["буклет", "хочу заказать буклет", "заказать буклет", "нужен буклет", "сделать буклет", "дизайн буклета", "буклеты", "публикация"]:
        await start_booklet(update, context)
        return
    
    # Заказ каталога
    if user_message.lower() in ["каталог", "хочу заказать каталог", "заказать каталог", "нужен каталог", "сделать каталог", "сверстать каталог", "делать каталог", "сделать издание"]:
        await start_catalog(update, context)
        return
    
    # О компании
    if user_message.lower() in ["что за компания", "расскажите о компании", "кто вы", "что вы за организация", "кто такая а-групп"]:
        await update.message.reply_text(
            "А-Групп — это дизайн-студия полного цикла и продакшн-центр. Мы создаём визуальный контент для бизнеса любого масштаба.\n\n"
            "Наши направления:\n"
            "• Графический дизайн — логотипы, фирменный стиль, упаковка, полиграфия.\n"
            "• Фотостудия — предметная, интерьерная и рекламная съёмка.\n"
            "• Видеопродакшн — съёмка и монтаж рекламных роликов, корпоративных фильмов.\n"
            "• Рекламные стратегии — разработка комплексных кампаний для продвижения вашего бренда.\n\n"
            "Мы находимся в Санкт-Петербурге и работаем по всей России."
        )
        return
    
    # Локация
    if user_message.lower() in ["где вы находитесь", "ваша локация", "где ваш офис", "где вы", "вы где"]:
        await update.message.reply_text("Мы находимся в Санкт-Петербурге. Вы можете оставить сообщение, и мы с вами обязательно свяжемся.")
        return
    
    # Контакты
    if user_message.lower() in ["как с вами связаться", "контакты", "как вам написать"]:
        await update.message.reply_text("Вы можете оставить сообщение, и мы с вами обязательно свяжемся. Мы работаем по всей России.")
        return
    
    # Цены
    if user_message.lower() in ["сколько стоят услуги", "прайс", "цены"]:
        await update.message.reply_text("Стоимость зависит от сложности проекта. Мы сделаем расчёт после того, как вы оставите заявку. Напишите нам, и мы свяжемся с вами для консультации.")
        return
    
    # Всё остальное — через OpenRouter
    reply = await ask_openrouter(user_message)
    await update.message.reply_text(reply, parse_mode="Markdown")

# --- ФУНКЦИИ ДЛЯ БУКЛЕТА (шаги опроса) ---
# ... (они остаются без изменений, но я их не копирую, чтобы не делать сообщение слишком длинным)
# Если нужна полная версия — напишите, я пришлю отдельно.

def main():
    print("✅ Бот A_Group запущен!")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(graphic|visual|advert)$"))
    
    # Здесь должны быть обработчики для буклета и каталога
    # (они уже были в коде)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
