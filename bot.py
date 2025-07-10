import os
import telebot
from telebot.types import Message
from dotenv import load_dotenv
import gspread

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
SHEET_URL = os.getenv("SHEET_URL")

bot = telebot.TeleBot(TOKEN)

gc = gspread.service_account(filename="service_account.json")
sheet = gc.open_by_url(SHEET_URL).sheet1

@bot.message_handler(commands=["start"])
def start(message: Message):
    user_id = message.from_user.id
    chat_member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
    if chat_member.status in ["member", "creator", "administrator"]:
        bot.send_message(message.chat.id, "You're subscribed ✅\nSend me the movie code:")
    else:
        bot.send_message(message.chat.id, f"❗ Please subscribe to the channel first: https://t.me/{CHANNEL_USERNAME}")

@bot.message_handler(func=lambda message: True)
def get_movie_info(message: Message):
    code = message.text.strip()
    try:
        records = sheet.get_all_records()
        for row in records:
            if str(row["code"]) == code:
                title = row["title"]
                year = row["year"]
                type_ = row["type"]
                description = row["description"]
                bot.send_message(message.chat.id, f"*{title}* ({year})\nType: {type_}\n\n{description}", parse_mode="Markdown")
                return
        bot.send_message(message.chat.id, "❌ Movie not found.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

bot.infinity_polling()
