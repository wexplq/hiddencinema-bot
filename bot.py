import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === НАСТРОЙКИ ===
TOKEN = "7893220655:AAEPrLm4PQ0qfGA3Y7ghV4IIeT-aa7HPnRQ"
CHANNEL_USERNAME = "@HiddenCinemaHub"
CHANNEL_LINK = "https://t.me/HiddenCinemaHub"
PAYPAL_LINK = "https://paypal.me/wexmlq"

# === GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1OSjayMHBie-QcxLfoytbiHjEMDzfwZJ1DU18vtELsKA/edit#gid=0").sheet1

bot = telebot.TeleBot(TOKEN)
user_codes = {}  # Сохраняем введённые коды по user_id

# === Главное меню ===
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🎬 Find a film")
    markup.row("📣 Telegram Channel", "❓ Help")
    markup.row("🎁 Support", "🕘 Watch History")
    return markup

# === Клавиатура с цифрами ===
def code_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("1", "2", "3")
    markup.row("4", "5", "6")
    markup.row("7", "8", "9")
    markup.row("0", "✅", "❌")
    markup.row("⬅️ Back to Home")
    return markup

# === Старт ===
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "You're subscribed ✅\nSend me the movie code:",
        reply_markup=main_menu()
    )

# === Обработка сообщений ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if text == "⬅️ Back to Home":
        bot.send_message(chat_id, "Back to Home Menu:", reply_markup=main_menu())

    elif text == "🎬 Find a film":
        user_codes[chat_id] = ""
        bot.send_message(chat_id, "Enter the code:", reply_markup=code_keyboard())

    elif text == "❓ Help":
            help_text = (
    "*📽️ How to use the bot:*\n\n"
    "🔘 Press *🎬 Find a film*.\n"
    "🔘 Enter the short code for the film (e.g., 812, 90125, etc).\n"
    "🔘 You'll receive the title and info immediately.\n"
    "🔔 Make sure you're subscribed to our channel: @HiddenCinemaHub 👈"
)
		

        bot.send_message(chat_id, help_text, parse_mode="Markdown", reply_markup=main_menu())

    elif text == "📣 Telegram Channel":
        bot.send_message(chat_id, f"Here’s the link to our channel: {CHANNEL_LINK}", reply_markup=main_menu())

    elif text == "🎁 Support":
        bot.send_message(chat_id, f"Support the project on PayPal: {PAYPAL_LINK}", reply_markup=main_menu())

    elif text == "🕘 Watch History":
        bot.send_message(chat_id, "Feature coming soon 👀", reply_markup=main_menu())

    elif text == "❌":
        user_codes[chat_id] = ""
        bot.send_message(chat_id, "Code cleared. Enter again:", reply_markup=code_keyboard())

    elif text == "✅":
        code = user_codes.get(chat_id, "")
        if not code:
            bot.send_message(chat_id, "You haven't entered a code yet.", reply_markup=code_keyboard())
            return
        try:
            cell = sheet.find(code)
            row = sheet.row_values(cell.row)
            title = row[1] if len(row) > 1 else "Title not found"
            info = row[2] if len(row) > 2 else "No description"
            bot.send_message(chat_id, f"🎬 *{title}*\n{info}", parse_mode="Markdown", reply_markup=main_menu())
            user_codes[chat_id] = ""
        except:
            bot.send_message(chat_id, "❌ Film not found. Try again.", reply_markup=code_keyboard())
            user_codes[chat_id] = ""

    elif text.isdigit():
        user_codes[chat_id] = user_codes.get(chat_id, "") + text
        bot.send_message(chat_id, f"Current code: `{user_codes[chat_id]}`", parse_mode="Markdown", reply_markup=code_keyboard())

    else:
        bot.send_message(chat_id, "Please use the menu buttons.", reply_markup=main_menu())

bot.polling(none_stop=True)

