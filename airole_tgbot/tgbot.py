import telegram.ext
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton # 互動式按鈕
from google import genai
from google.genai import types

import codecs
import asyncio
import os
import airole_tgbot
import json

# 替換成你的 Bot Token
TOKEN = os.getenv("TG_BOT_TOKEN", None)

STATE = {
    1: "start",
    2: "train",
    3: "confirm",
}
# 替換成你的 API Key
g_client = genai.Client(api_key=os.getenv("API_KEY"))



class Basic:
    def __init__(self, client):
        self.client = client

        self.client.add_handler(CommandHandler('start', self.start))
        self.client.add_handler(CommandHandler('choose', self.choose))

        self.client.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sender = {
            "id": update.effective_user.id,
            "name": update.effective_user.username,
        }
        # Load character data from JSON
        f = codecs.open("resource/characters.json", "r", "utf-8")
        characters = json.load(f)

        character_list = "\n".join([f"- {c['name']}: {c['description']}" for c in characters['characters']])
        await  update.message.reply_text(f"Welcome! Choose a character to talk to:\n{character_list}\n\nUse /choose <character_name> to select a character.")

    async def choose(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sender = {
            "id": update.effective_user.id,
            "name": update.effective_user.username,
        }
        # Load character data from JSON
        f = codecs.open("resource/characters.json", "r", "utf-8")
        characters = json.load(f)

        character_name = " ".join(context.args).strip()
        for character in characters['characters']:
            if character["name"].lower() == character_name.lower():
                context.user_data['character'] = character
                # 使用 Gemini API 生成回應
                chat = g_client.chats.create(model="gemini-2.0-flash", history=[])
                # 構建提示
                chat.send_message(f"你現在扮演{character['name']}，一個{character['type']}。{character['description']}。個性:{character}。回答請加入 emojis 來修飾。")
                resp = chat.send_message(f"請自我介紹")
                context.user_data['chat'] = chat

                await update.message.reply_text(resp.text)
                return
        await update.message.reply_text(f"Character '{character_name}' not found.  Use /start to see the list of available characters.")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if 'chat' not in context.user_data:
            chat = context.user_data['chat']
            resp = chat.send_message(update.message.text)
            await update.message.reply_text(resp.text)
        else:
            await update.message.reply_text("Use /start to see the list of available characters.")


async def main():
    application = telegram.ext.Application.builder().token(TOKEN).build()

    Basic(application)

    await application.run_polling()

