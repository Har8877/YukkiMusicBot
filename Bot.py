import telebot
import sqlite3
import time
from telebot.types import LabeledPrice, PreCheckoutQuery

TOKEN = "8610914950:AAHsgrKg8DBrzWUNyEGkDvVKF67tPDojT28"          # փոխիր քո բոտի token-ով
BOT_USERNAME = "HackLabBot"         # օրինակ՝ "admin_tools_bot" առանց @

bot = telebot.TeleBot(TOKEN)

# --- Database setup ---
conn = sqlite3.connect('bot.db', check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    subscription_until INTEGER DEFAULT 0
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS referrals (
    inviter_id INTEGER,
    new_user_id INTEGER
)
''')

conn.commit()

# --- Helper functions ---
def add_user(user_id):
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def add_referral(inviter_id, new_user_id):
    if inviter_id == new_user_id:
        return
    c.execute("INSERT INTO referrals (inviter_id, new_user_id) VALUES (?, ?)", (inviter_id, new_user_id))
    conn.commit()
    bot.send_message(inviter_id, "🎉 Դուք ստացաք referral bonus (հետագայում կարող եք ավելացնել Stars-ով վճարումից հետո)")

def is_subscribed(user_id):
    c.execute("SELECT subscription_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row and row[0] > int(time.time()):
        return True
    return False

def activate_subscription(user_id, days=30):
    until = int(time.time()) + days * 24 * 3600
    c.execute("UPDATE users SET subscription_until = ? WHERE user_id = ?", (until, user_id))
    conn.commit()
    return until

# --- Commands ---
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    user_id = message.from_user.id

    add_user(user_id)

    # Referral
    if len(args) > 1:
        try:
            inviter_id = int(args[1])
            add_referral(inviter_id, user_id)
        except:
            pass

    text = f"""
🤖 Admin Tools Bot

📌 /all → կոչի բոլորին խմբում (պահանջվում է ակտիվ բաժանորդագրություն)
💰 Ամսական վճար՝ 2⭐ Telegram Stars-ով

Օգտագործեք /invite հրավերի համար
/subscribe → վճարեք 2⭐ ամսական
/stats → referral-ների քանակը
"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['invite'])
def invite(message):
    user_id = message.from_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    bot.send_message(
        message.chat.id,
        f"🔗 Ձեր referral link՝\n{link}\n\nՀրավիրի 1 մարդու → ստացիր bonus (հետագայում)"
    )

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    prices = [LabeledPrice(label='Ամսական բաժանորդագրություն', amount=2)]  # 2 Stars

    try:
        bot.send_invoice(
            chat_id=message.chat.id,
            title="Admin Tools – Ամսական մուտք",
            description="Անսահմանափակ /all օգտագործում խմբերում (30 օր)",
            payload=f"sub_{message.from_user.id}_{int(time.time())}",
            provider_token="",              # պարտադիր դատարկ Stars-ի համար
            currency="XTR",
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
    except Exception as e:
        bot.reply_to(message, f"Վրեպ invoice-ի ժամանակ՝ {str(e)}")

@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload
    total_amount = message.successful_payment.total_amount  # Stars-ի քանակը

    if payload.startswith("sub_"):
        until = activate_subscription(user_id, days=30)
        date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(until))
        bot.send_message(
            message.chat.id,
            f"✅ Հաջող վճարում! {total_amount}⭐ վճարվեց\n"
            f"Բաժանորդագրությունը ակտիվ է մինչև {date_str}"
        )

@bot.message_handler(commands=['stats'])
def stats(message):
    user_id = message.from_user.id
    c.execute("SELECT COUNT(*) FROM referrals WHERE inviter_id=?", (user_id,))
    count = c.fetchone()[0]
    bot.send_message(message.chat.id, f"👥 Հրավիրած օգտատերեր՝ {count}")

@bot.message_handler(commands=['all'])
def all_command(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ /all աշխատում է միայն խմբերում։")
        return

    user_id = message.from_user.id

    if not is_subscribed(user_id):
        bot.reply_to(message, "❌ Բաժանորդագրությունը ժամկետանց է կամ բացակայում է։ Վճարեք /subscribe-ով։")
        return

    # Telegram-ը չի տալիս բոլոր անդամներին tag անել, ուստի պարզ տեքստ
    bot.send_message(
        message.chat.id,
        "📣 Attention everyone! /all կանչված է ադմինի կողմից!\n"
        "(Բոտը չի կարող tag անել բոլորին — դա Telegram-ի սահմանափակում է)"
    )

# --- Run bot ---
print("Bot started...")
bot.infinity_polling()
