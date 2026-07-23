{\rtf1\ansi\ansicpg1252\cocoartf2639
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import os\
import requests\
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup\
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes\
\
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")\
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")\
\
async def ask_deepseek(user_message):\
    try:\
        response = requests.post(\
            url="https://api.deepseek.com/v1/chat/completions",\
            headers=\{\
                "Authorization": f"Bearer \{DEEPSEEK_API_KEY\}",\
                "Content-Type": "application/json",\
            \},\
            json=\{\
                "model": "deepseek-chat",\
                "messages": [\
                    \{"role": "system", "content": "\uc0\u1058 \u1099  \'97 \u1082 \u1086 \u1085 \u1089 \u1091 \u1083 \u1100 \u1090 \u1072 \u1085 \u1090  \u1087 \u1086  \u1076 \u1080 \u1079 \u1072 \u1081 \u1085 \u1091  \u1080  \u1088 \u1077 \u1082 \u1083 \u1072 \u1084 \u1077 . \u1054 \u1090 \u1074 \u1077 \u1095 \u1072 \u1081  \u1085 \u1072  \u1088 \u1091 \u1089 \u1089 \u1082 \u1086 \u1084  \u1103 \u1079 \u1099 \u1082 \u1077 , \u1082 \u1088 \u1072 \u1090 \u1082 \u1086  \u1080  \u1087 \u1086  \u1076 \u1077 \u1083 \u1091 ."\},\
                    \{"role": "user", "content": user_message\}\
                ],\
                "max_tokens": 500,\
                "temperature": 0.7\
            \}\
        )\
        if response.status_code == 200:\
            return response.json()["choices"][0]["message"]["content"]\
        else:\
            return f"\uc0\u1054 \u1096 \u1080 \u1073 \u1082 \u1072  API: \{response.status_code\}"\
    except Exception as e:\
        return f"\uc0\u1054 \u1096 \u1080 \u1073 \u1082 \u1072 : \{str(e)\}"\
\
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    keyboard = [\
        [InlineKeyboardButton("
\f1 \uc0\u55356 \u57256 
\f0  \uc0\u1043 \u1088 \u1072 \u1092 \u1080 \u1095 \u1077 \u1089 \u1082 \u1080 \u1077  \u1088 \u1077 \u1096 \u1077 \u1085 \u1080 \u1103 ", callback_data="graphic")],\
        [InlineKeyboardButton("
\f1 \uc0\u55357 \u56522 
\f0  \uc0\u1042 \u1080 \u1079 \u1091 \u1072 \u1083 \u1100 \u1085 \u1099 \u1077  \u1089 \u1090 \u1088 \u1072 \u1090 \u1077 \u1075 \u1080 \u1080 ", callback_data="visual")],\
        [InlineKeyboardButton("
\f1 \uc0\u55357 \u56547 
\f0  \uc0\u1056 \u1077 \u1082 \u1083 \u1072 \u1084 \u1085 \u1099 \u1077  \u1089 \u1090 \u1088 \u1072 \u1090 \u1077 \u1075 \u1080 \u1080 ", callback_data="advert")],\
    ]\
    reply_markup = InlineKeyboardMarkup(keyboard)\
    await update.message.reply_text(\
        "\uc0\u1044 \u1086 \u1073 \u1088 \u1086 \u1075 \u1086  \u1076 \u1085 \u1103 ! \u1071  \u1073 \u1086 \u1090  A-\u1043 \u1088 \u1091 \u1087 \u1087  \u1044 \u1080 \u1079 \u1072 \u1081 \u1085 . \u1063 \u1077 \u1084  \u1084 \u1086 \u1075 \u1091  \u1087 \u1086 \u1084 \u1086 \u1095 \u1100 ? \u1052 \u1099  \u1086 \u1089 \u1091 \u1097 \u1077 \u1089 \u1090 \u1074 \u1083 \u1103 \u1077 \u1084 :",\
        reply_markup=reply_markup\
    )\
\
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    query = update.callback_query\
    await query.answer()\
    if query.data == "graphic":\
        await query.edit_message_text("
\f1 \uc0\u55356 \u57256 
\f0  **\uc0\u1043 \u1088 \u1072 \u1092 \u1080 \u1095 \u1077 \u1089 \u1082 \u1080 \u1077  \u1088 \u1077 \u1096 \u1077 \u1085 \u1080 \u1103 :** \u1056 \u1072 \u1079 \u1088 \u1072 \u1073 \u1086 \u1090 \u1082 \u1072  \u1092 \u1080 \u1088 \u1084 \u1077 \u1085 \u1085 \u1086 \u1075 \u1086  \u1089 \u1090 \u1080 \u1083 \u1103 , \u1083 \u1086 \u1075 \u1086 \u1090 \u1080 \u1087 \u1086 \u1074 , \u1091 \u1087 \u1072 \u1082 \u1086 \u1074 \u1082 \u1080  \u1080  \u1087 \u1086 \u1083 \u1080 \u1075 \u1088 \u1072 \u1092 \u1080 \u1080 .", reply_markup=query.message.reply_markup)\
    elif query.data == "visual":\
        await query.edit_message_text("
\f1 \uc0\u55357 \u56522 
\f0  **\uc0\u1042 \u1080 \u1079 \u1091 \u1072 \u1083 \u1100 \u1085 \u1099 \u1077  \u1089 \u1090 \u1088 \u1072 \u1090 \u1077 \u1075 \u1080 \u1080 :** \u1057 \u1086 \u1079 \u1076 \u1072 \u1105 \u1084  \u1094 \u1077 \u1083 \u1086 \u1089 \u1090 \u1085 \u1091 \u1102  \u1089 \u1080 \u1089 \u1090 \u1077 \u1084 \u1091  \u1074 \u1080 \u1079 \u1091 \u1072 \u1083 \u1100 \u1085 \u1086 \u1081  \u1082 \u1086 \u1084 \u1084 \u1091 \u1085 \u1080 \u1082 \u1072 \u1094 \u1080 \u1080  \u1076 \u1083 \u1103  \u1074 \u1072 \u1096 \u1077 \u1075 \u1086  \u1073 \u1088 \u1077 \u1085 \u1076 \u1072 .", reply_markup=query.message.reply_markup)\
    elif query.data == "advert":\
        await query.edit_message_text("
\f1 \uc0\u55357 \u56547 
\f0  **\uc0\u1056 \u1077 \u1082 \u1083 \u1072 \u1084 \u1085 \u1099 \u1077  \u1089 \u1090 \u1088 \u1072 \u1090 \u1077 \u1075 \u1080 \u1080 :** \u1056 \u1072 \u1079 \u1088 \u1072 \u1073 \u1072 \u1090 \u1099 \u1074 \u1072 \u1077 \u1084  \u1101 \u1092 \u1092 \u1077 \u1082 \u1090 \u1080 \u1074 \u1085 \u1099 \u1077  \u1088 \u1077 \u1082 \u1083 \u1072 \u1084 \u1085 \u1099 \u1077  \u1082 \u1072 \u1084 \u1087 \u1072 \u1085 \u1080 \u1080  \u1076 \u1083 \u1103  \u1087 \u1088 \u1080 \u1074 \u1083 \u1077 \u1095 \u1077 \u1085 \u1080 \u1103  \u1074 \u1072 \u1096 \u1077 \u1081  \u1072 \u1091 \u1076 \u1080 \u1090 \u1086 \u1088 \u1080 \u1080 .", reply_markup=query.message.reply_markup)\
\
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):\
    user_message = update.message.text\
    if not user_message:\
        return\
    if user_message.lower() in ["\uc0\u1087 \u1088 \u1080 \u1074 \u1077 \u1090 ", "\u1079 \u1076 \u1088 \u1072 \u1074 \u1089 \u1090 \u1074 \u1091 \u1081 \u1090 \u1077 ", "\u1076 \u1086 \u1073 \u1088 \u1099 \u1081  \u1076 \u1077 \u1085 \u1100 "]:\
        await start(update, context)\
        return\
    reply = await ask_deepseek(user_message)\
    await update.message.reply_text(reply)\
\
def main():\
    app = Application.builder().token(TELEGRAM_TOKEN).build()\
    app.add_handler(CommandHandler("start", start))\
    app.add_handler(CallbackQueryHandler(button_handler))\
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))\
    app.run_polling()\
\
if __name__ == "__main__":\
    main()}