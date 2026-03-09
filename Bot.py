import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
import time
import threading 

TOKEN = "8725705616:AAFOeBQ7tqeFgqKY2qc9Bj6BQDkpaa0ieKA" 

bot = telebot.TeleBot(TOKEN) 

live_sessions = {} 

cities = [
("🇦🇲", "Yerevan", "Asia/Yerevan", "+4"),
("🇩🇪", "Berlin", "Europe/Berlin", "+1"),
("🇫🇷", "Paris", "Europe/Paris", "+1"),
("🇺🇸", "New York", "America/New_York", "-5")
]


def day_or_night(hour):
    if 6 <= hour < 18:
        return "🌞"
    return "🌙"


def get_clock(): 

    text = "🌍 <b>Live World Clock</b>\n\n" 

    for flag, city, zone, utc in cities: 

        tz = pytz.timezone(zone)
        now = datetime.now(tz) 

        time_str = now.strftime("%H:%M:%S")
        icon = day_or_night(now.hour) 

        text += f"{flag} <b>{city}</b>\n"
        text += f"{icon} 🕒 {time_str}\n"
        text += f"UTC {utc}\n\n" 

    return text


def live_clock(chat_id, message_id): 

    live_sessions[chat_id] = True 

    while live_sessions.get(chat_id): 

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("🔄 Restart", callback_data="clock"),
            InlineKeyboardButton("ℹ️ Info", callback_data="info")
        ) 

        try:
            bot.edit_message_text(
                get_clock(),
                chat_id,
                message_id,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        except:
            pass 

        time.sleep(2)


@bot.message_handler(commands=['start'])
def start(message): 

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🌍 Open World Clock", callback_data="clock")
    ) 

    text = """
👋 <b>Բարի գալուստ World Clock Bot</b> 

Այս բոտը ցույց է տալիս աշխարհի տարբեր քաղաքների ճշգրիտ ժամանակը 🌍
""" 

    bot.send_message(
        message.chat.id,
        text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback(call): 

    if call.data == "clock": 

        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton("🔄 Restart", callback_data="clock"),
            InlineKeyboardButton("ℹ️ Info", callback_data="info")
        ) 

        bot.edit_message_text(
            get_clock(),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        ) 

        threading.Thread(
            target=live_clock,
            args=(call.message.chat.id, call.message.message_id)
        ).start()


    elif call.data == "info": 

        live_sessions[call.message.chat.id] = False 

        keyboard = InlineKeyboardMarkup() 

        text = """
ℹ️ <b>World Clock Bot</b> 

Այս բոտը ցույց է տալիս տարբեր քաղաքների ժամանակը։ 

Քաղաքներ
🇦🇲 Yerevan
🇩🇪 Berlin
🇫🇷 Paris
🇺🇸 New York 

⏱ Live թարմացում
🌞🌙 Day / Night
UTC տարբերություն
""" 

        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML"
        ) 

        def back(): 

            time.sleep(8) 

            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton("🔄 Restart", callback_data="clock"),
                InlineKeyboardButton("ℹ️ Info", callback_data="info")
            ) 

            bot.edit_message_text(
                get_clock(),
                call.message.chat.id,
                call.message.message_id,
                parse_mode="HTML",
                reply_markup=keyboard
            ) 

            threading.Thread(
                target=live_clock,
                args=(call.message.chat.id, call.message.message_id)
            ).start() 

        threading.Thread(target=back).start()


bot.infinity_polling()
