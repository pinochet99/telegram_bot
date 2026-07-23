import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes, ConversationHandler

# --- ТОКЕНЫ И НАСТРОЙКИ ---
TELEGRAM_TOKEN = "8833699342:AAGud8WsyHej9LtI5d6xkDRo3xoLSm2hqPg"
OPENROUTER_API_KEY = "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"
OWNER_CHAT_ID = 63938809  # Ваш Telegram ID

# --- СОСТОЯНИЯ ДЛЯ ОПРОСОВ ---
BOOKLET_FORMAT, BOOKLET_COLOR, BOOKLET_PAPER, BOOKLET_PRINT = range(4)
CATALOG_FORMAT, CATALOG_COLOR, CATALOG_PAGES, CATALOG_COVER, CATALOG_BLOCK, CATALOG_PRINT = range(6)

# --- ФУНКЦИЯ ПОИСКА В WIKIPEDIA (ЗАПАСНОЙ ВАРИАНТ) ---
async def search_wikipedia(query):
    try:
        url = "https://ru.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "utf8": 1,
            "srlimit": 1
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["query"]["search"]:
                title = data["query"]["search"][0]["title"]
                # Получаем краткое содержание
                params = {
                    "action": "query",
                    "prop": "extracts",
                    "exintro": True,
                    "explaintext": True,
                    "titles": title,
                    "format": "json",
                    "utf8": 1
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    pages = data["query"]["pages"]
                    for page_id, page in pages.items():
                        if "extract" in page:
                            extract = page["extract"]
                            if len(extract) > 500:
                                extract = extract[:500] + "..."
                            return f"📖 **{title}**\n\n{extract}"
            return "🤔 Не нашёл информации по вашему запросу в Wikipedia."
        return "⚠️ Ошибка при обращении к Wikipedia."
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

# --- ФУНКЦИЯ ЗАПРОСА К OPENROUTER (С ЗАПАСНЫМ ВАРИАНТОМ) ---
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
                "model": "deepseek/deepseek-chat:free",
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
            # Если OpenRouter вернул ошибку — используем Wikipedia
            return await search_wikipedia(user_message)
    except Exception as e:
        # Если ошибка соединения — используем Wikipedia
        return await search_wikipedia(user_message)

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
    
    # --- ПРИВЕТСТВИЯ ---
    if user_message.lower() in ["привет", "здравствуйте", "добрый день", "доброго дня", "доброе утро", "добрый вечер"]:
        await start(update, context)
        return
    
    # --- ЗАКАЗ БУКЛЕТА ---
    if user_message.lower() in ["буклет", "хочу заказать буклет", "заказать буклет", "нужен буклет", "сделать буклет", "дизайн буклета", "буклеты", "публикация"]:
        await start_booklet(update, context)
        return
    
    # --- ЗАКАЗ КАТАЛОГА ---
    if user_message.lower() in ["каталог", "хочу заказать каталог", "заказать каталог", "нужен каталог", "сделать каталог", "сверстать каталог", "делать каталог", "сделать издание"]:
        await start_catalog(update, context)
        return
    
    # --- ОТВЕТЫ НА ВОПРОСЫ О КОМПАНИИ ---
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
    
    # --- ВОПРОСЫ О ЛОКАЦИИ ---
    if user_message.lower() in ["где вы находитесь", "ваша локация", "где ваш офис", "где вы", "вы где"]:
        await update.message.reply_text("Мы находимся в Санкт-Петербурге. Вы можете оставить сообщение, и мы с вами обязательно свяжемся.")
        return
    
    # --- ВОПРОСЫ О КОНТАКТАХ ---
    if user_message.lower() in ["как с вами связаться", "контакты", "как вам написать"]:
        await update.message.reply_text("Вы можете оставить сообщение, и мы с вами обязательно свяжемся. Мы работаем по всей России.")
        return
    
    # --- ВОПРОСЫ О ЦЕНАХ ---
    if user_message.lower() in ["сколько стоят услуги", "прайс", "цены"]:
        await update.message.reply_text("Стоимость зависит от сложности проекта. Мы сделаем расчёт после того, как вы оставите заявку. Напишите нам, и мы свяжемся с вами для консультации.")
        return
    
    # --- ВСЁ ОСТАЛЬНОЕ — ЧЕРЕЗ OPENROUTER, ПРИ ОШИБКЕ — WIKIPEDIA ---
    reply = await ask_openrouter(user_message)
    await update.message.reply_text(reply, parse_mode="Markdown")

# --- ФУНКЦИИ ДЛЯ БУКЛЕТА ---
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

async def booklet_format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    format_map = {
        "booklet_a4": "A4",
        "booklet_a5": "A5",
        "booklet_a3": "A3",
        "booklet_other": "Другой"
    }
    context.user_data['booklet_data']['format'] = format_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("CMYK (полноцвет)", callback_data="booklet_cmyk")],
        [InlineKeyboardButton("Чёрно-белый", callback_data="booklet_bw")],
        [InlineKeyboardButton("Смешанный", callback_data="booklet_mixed")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какая цветность?", reply_markup=reply_markup)
    return BOOKLET_COLOR

async def booklet_color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    color_map = {
        "booklet_cmyk": "CMYK (полноцвет)",
        "booklet_bw": "Чёрно-белый",
        "booklet_mixed": "Смешанный"
    }
    context.user_data['booklet_data']['color'] = color_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("Глянец", callback_data="booklet_glossy")],
        [InlineKeyboardButton("Матовая", callback_data="booklet_matte")],
        [InlineKeyboardButton("Дизайнерская", callback_data="booklet_design")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какой тип бумаги?", reply_markup=reply_markup)
    return BOOKLET_PAPER

async def booklet_paper_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    paper_map = {
        "booklet_glossy": "Глянец",
        "booklet_matte": "Матовая",
        "booklet_design": "Дизайнерская"
    }
    context.user_data['booklet_data']['paper'] = paper_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("до 100", callback_data="booklet_100")],
        [InlineKeyboardButton("100-500", callback_data="booklet_500")],
        [InlineKeyboardButton("500-1000", callback_data="booklet_1000")],
        [InlineKeyboardButton("более 1000", callback_data="booklet_1000_plus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какой тираж?", reply_markup=reply_markup)
    return BOOKLET_PRINT

async def booklet_print_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    print_map = {
        "booklet_100": "до 100",
        "booklet_500": "100-500",
        "booklet_1000": "500-1000",
        "booklet_1000_plus": "более 1000"
    }
    context.user_data['booklet_data']['print'] = print_map[query.data]
    
    data = context.user_data['booklet_data']
    username = update.effective_user.username or update.effective_user.first_name
    
    # Уведомление клиенту
    text = f"Принято! Ваш запрос: буклет {data['format']}, {data['color']}, {data['paper']}, тираж {data['print']}. Наши менеджеры обязательно свяжутся с вами для уточнения стоимости и сроков. Благодарим Вас!"
    await query.message.reply_text(text)
    
    # Уведомление владельцу
    owner_text = f"Новый заказ — буклет\nКлиент: {username} (ID: {update.effective_user.id})\nФормат: {data['format']}\nЦветность: {data['color']}\nБумага: {data['paper']}\nТираж: {data['print']}"
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=owner_text)
    
    context.user_data.clear()
    return -1

# --- ФУНКЦИИ ДЛЯ КАТАЛОГА ---
async def start_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("A4", callback_data="catalog_a4")],
        [InlineKeyboardButton("A5", callback_data="catalog_a5")],
        [InlineKeyboardButton("A3", callback_data="catalog_a3")],
        [InlineKeyboardButton("Другой", callback_data="catalog_other")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Какой формат вам нужен?", reply_markup=reply_markup)
    context.user_data['catalog_data'] = {}
    return CATALOG_FORMAT

async def catalog_format_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    format_map = {
        "catalog_a4": "A4",
        "catalog_a5": "A5",
        "catalog_a3": "A3",
        "catalog_other": "Другой"
    }
    context.user_data['catalog_data']['format'] = format_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("CMYK (полноцвет)", callback_data="catalog_cmyk")],
        [InlineKeyboardButton("Чёрно-белый", callback_data="catalog_bw")],
        [InlineKeyboardButton("Смешанный", callback_data="catalog_mixed")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какая цветность?", reply_markup=reply_markup)
    return CATALOG_COLOR

async def catalog_color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    color_map = {
        "catalog_cmyk": "CMYK (полноцвет)",
        "catalog_bw": "Чёрно-белый",
        "catalog_mixed": "Смешанный"
    }
    context.user_data['catalog_data']['color'] = color_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("до 8", callback_data="catalog_8")],
        [InlineKeyboardButton("8-16", callback_data="catalog_16")],
        [InlineKeyboardButton("16-32", callback_data="catalog_32")],
        [InlineKeyboardButton("более 32", callback_data="catalog_32_plus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Сколько полос (страниц) в каталоге?", reply_markup=reply_markup)
    return CATALOG_PAGES

async def catalog_pages_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    pages_map = {
        "catalog_8": "до 8",
        "catalog_16": "8-16",
        "catalog_32": "16-32",
        "catalog_32_plus": "более 32"
    }
    context.user_data['catalog_data']['pages'] = pages_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("Глянец", callback_data="catalog_cover_glossy")],
        [InlineKeyboardButton("Матовая", callback_data="catalog_cover_matte")],
        [InlineKeyboardButton("Дизайнерская", callback_data="catalog_cover_design")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какой тип бумаги для обложки?", reply_markup=reply_markup)
    return CATALOG_COVER

async def catalog_cover_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    cover_map = {
        "catalog_cover_glossy": "Глянец",
        "catalog_cover_matte": "Матовая",
        "catalog_cover_design": "Дизайнерская"
    }
    context.user_data['catalog_data']['cover'] = cover_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("Глянец", callback_data="catalog_block_glossy")],
        [InlineKeyboardButton("Матовая", callback_data="catalog_block_matte")],
        [InlineKeyboardButton("Дизайнерская", callback_data="catalog_block_design")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какой тип бумаги для внутреннего блока?", reply_markup=reply_markup)
    return CATALOG_BLOCK

async def catalog_block_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    block_map = {
        "catalog_block_glossy": "Глянец",
        "catalog_block_matte": "Матовая",
        "catalog_block_design": "Дизайнерская"
    }
    context.user_data['catalog_data']['block'] = block_map[query.data]
    
    keyboard = [
        [InlineKeyboardButton("до 100", callback_data="catalog_100")],
        [InlineKeyboardButton("100-500", callback_data="catalog_500")],
        [InlineKeyboardButton("500-1000", callback_data="catalog_1000")],
        [InlineKeyboardButton("более 1000", callback_data="catalog_1000_plus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Какой тираж?", reply_markup=reply_markup)
    return CATALOG_PRINT

async def catalog_print_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.delete()
    print_map = {
        "catalog_100": "до 100",
        "catalog_500": "100-500",
        "catalog_1000": "500-1000",
        "catalog_1000_plus": "более 1000"
    }
    context.user_data['catalog_data']['print'] = print_map[query.data]
    
    data = context.user_data['catalog_data']
    username = update.effective_user.username or update.effective_user.first_name
    
    # Уведомление клиенту
    text = f"Принято! Ваш запрос: каталог формата {data['format']}, {data['color']}, {data['pages']} полос, обложка: {data['cover']}, блок: {data['block']}, тираж {data['print']}. Наши менеджеры обязательно свяжутся с вами для уточнения стоимости и сроков. Благодарим Вас!"
    await query.message.reply_text(text)
    
    # Уведомление владельцу
    owner_text = f"Новый заказ — каталог\nКлиент: {username} (ID: {update.effective_user.id})\nФормат: {data['format']}\nЦветность: {data['color']}\nПолос: {data['pages']}\nОбложка: {data['cover']}\nБлок: {data['block']}\nТираж: {data['print']}"
    await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=owner_text)
    
    context.user_data.clear()
    return -1

# --- ЗАПУСК БОТА ---
def main():
    print("✅ Бот A_Group запущен!")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^(graphic|visual|advert)$"))
    
    booklet_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(буклет|хочу заказать буклет|заказать буклет|нужен буклет|сделать буклет)$"), start_booklet)],
        states={
            BOOKLET_FORMAT: [CallbackQueryHandler(booklet_format_handler, pattern="^booklet_")],
            BOOKLET_COLOR: [CallbackQueryHandler(booklet_color_handler, pattern="^booklet_")],
            BOOKLET_PAPER: [CallbackQueryHandler(booklet_paper_handler, pattern="^booklet_")],
            BOOKLET_PRINT: [CallbackQueryHandler(booklet_print_handler, pattern="^booklet_")],
        },
        fallbacks=[]
    )
    app.add_handler(booklet_handler)
    
    catalog_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(каталог|хочу заказать каталог|заказать каталог|нужен каталог|сделать каталог)$"), start_catalog)],
        states={
            CATALOG_FORMAT: [CallbackQueryHandler(catalog_format_handler, pattern="^catalog_")],
            CATALOG_COLOR: [CallbackQueryHandler(catalog_color_handler, pattern="^catalog_")],
            CATALOG_PAGES: [CallbackQueryHandler(catalog_pages_handler, pattern="^catalog_")],
            CATALOG_COVER: [CallbackQueryHandler(catalog_cover_handler, pattern="^catalog_cover_")],
            CATALOG_BLOCK: [CallbackQueryHandler(catalog_block_handler, pattern="^catalog_block_")],
            CATALOG_PRINT: [CallbackQueryHandler(catalog_print_handler, pattern="^catalog_")],
        },
        fallbacks=[]
    )
    app.add_handler(catalog_handler)
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    main()
