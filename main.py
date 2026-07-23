import os
import re
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, ConversationHandler

# --- ТОКЕНЫ И НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8833699342:AAGud8WsyHej9LtI5d6xkDRo3xoLSm2hqPg"
GROQ_API_KEY = "xai-btgIdlfmlf3kd1qgJsmBUIRuZMNgy4WvxRsK7fcoEWwN6PslkY3jBdOl780dqNWdijWBjkDaQv1fzTdD"
OPENROUTER_API_KEY = "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"
OWNER_CHAT_ID = 63938809

# --- СОСТОЯНИЯ ДЛЯ ОПРОСОВ ---
BOOKLET_FORMAT, BOOKLET_COLOR, BOOKLET_PAPER, BOOKLET_PRINT = range(4)
CATALOG_FORMAT, CATALOG_COLOR, CATALOG_PAGES, CATALOG_COVER, CATALOG_BLOCK, CATALOG_PRINT = range(6)

# --- ФУНКЦИЯ ПОИСКА В WIKIPEDIA (АСИНХРОННАЯ) ---
async def search_wikipedia(query):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = "https://ru.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "utf8": 1,
                "srlimit": 1
            }
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["query"]["search"]:
                    title = data["query"]["search"][0]["title"]
                    params = {
                        "action": "query",
                        "prop": "extracts",
                        "exintro": True,
                        "explaintext": True,
                        "titles": title,
                        "format": "json",
                        "utf8": 1
                    }
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        pages = data["query"]["pages"]
                        for page_id, page in pages.items():
                            if "extract" in page:
                                extract = page["extract"]
                                if len(extract) > 500:
                                    extract = extract[:500] + "..."
                                return f"📖 **{title}**\n\n{extract}"
            return None
    except Exception as e:
        return None

# --- ФУНКЦИЯ ЗАПРОСА К GROQ (АСИНХРОННАЯ) ---
async def ask_groq(user_message):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.3-70b-versatile",
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
                return await ask_openrouter_fallback(user_message)
    except Exception as e:
        return await ask_openrouter_fallback(user_message)

# --- ЗАПАСНАЯ ФУНКЦИЯ (OPENROUTER) ---
async def ask_openrouter_fallback(user_message):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://t.me/a_group_1",
                    "X-Title": "A_Group",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "meta-llama/llama-3.3-70b-instruct:free",
                    "messages": [
                        {"role": "system", "content": "Ты — консультант по дизайну и рекламе. Отвечай на русском языке, кратко и по делу. Если не знаешь — скажи честно."},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                }
            )
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return "Извините, я не смог найти точный ответ. Попробуйте переформулировать вопрос."
    except Exception as e:
        return "Извините, временная ошибка. Пожалуйста, попробуйте позже."

# --- ОСНОВНАЯ ФУНКЦИЯ ЗАПРОСА ---
async def ask_ai(user_message):
    wiki_result = await search_wikipedia(user_message)
    if wiki_result:
        return wiki_result
    return await ask_groq(user_message)

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

# --- ОБРАБОТЧИК СООБЩЕНИЙ (С ГИБКИМ ПОИСКОМ) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message:
        return
    
    text_lower = user_message.lower()
    
    # --- ПРИВЕТСТВИЯ ---
    if re.search(r'\b(привет|здравствуйте|добрый день|доброго дня|доброе утро|добрый вечер)\b', text_lower):
        await start(update, context)
        return
    
    # --- ЗАКАЗ БУКЛЕТА ---
    if re.search(r'\b(буклет|заказать буклет|сделать буклет|дизайн буклета|буклеты|публикация)\b', text_lower):
        await start_booklet(update, context)
        return
    
    # --- ЗАКАЗ КАТАЛОГА ---
    if re.search(r'\b(каталог|заказать каталог|сделать каталог|сверстать каталог|делать каталог|сделать издание)\b', text_lower):
        await start_catalog(update, context)
        return
    
    # --- ОТВЕТЫ НА ВОПРОСЫ О КОМПАНИИ ---
    if re.search(r'\b(что за компания|расскажите о компании|кто вы|что вы за организация|кто такая а-групп)\b', text_lower):
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
    
    # --- ВОПРОСЫ О ЛОКАЦИИ ---
    if re.search(r'\b(где вы находитесь|ваша локация|где ваш офис|где вы|вы где)\b', text_lower):
        await update.message.reply_text("Мы находимся в Санкт-Петербурге. Вы можете оставить сообщение, и мы с вами обязательно свяжемся.")
        return
    
    # --- ВОПРОСЫ О КОНТАКТАХ ---
    if re.search(r'\b(как с вами связаться|контакты|как вам написать)\b', text_lower):
        await update.message.reply_text("Вы можете оставить сообщение, и мы с вами обязательно свяжемся. Мы работаем по всей России.")
        return
    
    # --- ВОПРОСЫ О ЦЕНАХ ---
    if re.search(r'\b(сколько стоят услуги|прайс|цены)\b', text_lower):
        await update.message.reply_text("Стоимость зависит от сложности проекта. Мы сделаем расчёт после того, как вы оставите заявку. Напишите нам, и мы свяжемся с вами для консультации.")
        return
    
    # --- ВСЁ ОСТАЛЬНОЕ — ЧЕРЕЗ AI ---
    reply = await ask_ai(user_message)
    await update.message.reply_text(reply, parse_mode="Markdown")

# --- ФУНКЦИИ ДЛЯ БУКЛЕТА (опрос в 4 шага) ---
async def start_booklet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("A4", callback_data="booklet_a4")],
        [InlineKeyboardButton("A5", callback_data="booklet_a5")],
        [InlineKeyboardButton("A3", callback_data="booklet_a3")],
        [InlineKeyboardButton("Другой", callback_data="booklet_other")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Какой формат вам нужен?", reply_markup=reply_markup)
    context.user_data['booklet_data'] = {}
    return BOOKLET_FORMAT

# --- ОСТАЛЬНЫЕ ФУНКЦИИ (буклет, каталог) остаются без изменений ---
# ... (они не меняются, я их не копирую, чтобы не делать сообщение слишком длинным)
# Если нужна полная версия — напишите, я пришлю отдельно.

def main():
    print("✅ Бот A_Group запущен (асинхронный, с гибким поиском)!")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(graphic|visual|advert)$"))
    
    # Добавьте обработчики для буклета и каталога (они уже были в коде)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
