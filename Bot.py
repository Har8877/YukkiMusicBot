import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8725705616:AAFOeBQ7tqeFgqKY2qc9Bj6BQDkpaa0ieKA"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):

    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "🌍 Բացել World Clock",
            web_app={"url": "https://YOURDOMAIN.com"}
        )
    )

    bot.send_message(
        message.chat.id,
        "Բարի գալուստ World Clock Mini App ⏰",
        reply_markup=keyboard
    )

bot.infinity_polling()
