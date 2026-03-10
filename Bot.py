import telebot
import sqlite3
import time
from telebot.types import LabeledPrice, PreCheckoutQuery

# ────────────────────────────────────────────────
# Կարգավորումներ — փոխիր սրանք
TOKEN = "8759605380:AAEYOqFb83txjuPR9QV0fcbLTbIRuwo4mLo"           # BotFather-ից ստացած token
BOT_USERNAME = "@cal1_f_bot"        # առանց @, օրինակ՝ admin_tools_bot
SUBSCRIPTION_COST = 2                       # Stars-ի քանակը 1 ամսվա համար
SUBSCRIPTION_DAYS = 30
# ────────────────────────────────────────────────

bot = telebot.TeleBot(TOKEN)

# Database կապ
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

# Helper functions
def add_user(user_id: int):
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def add_referral(inviter_id: int, new_user_id: int):
    if inviter_id == new_user_id:
        return
    c.execute("INSERT INTO referrals (inviter_id, new_user_id) VALUES (?, ?)", (inviter_id, new_user_id))
    conn.commit()
    try:
        bot.send_message(inviter_id, "🎉 Շնորհակալություն! Դուք ստացաք referral bonus (հետագայում կարող եք ավելացնել պարգևը Stars-ով վճարումից հետո)")
    except:
        pass  # եթե օգտատերը բլոկավորել է բոտը

def is_subscribed(user_id: int) -> bool:
    c.execute("SELECT subscription_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    return bool(row and row[0] > int(time.time()))

def activate_subscription(user_id: int, days: int = SUBSCRIPTION_DAYS) -> int:
    until = int(time.time()) + days * 86400
    c.execute("UPDATE users SET subscription_until = ? WHERE user_id = ?", (until, user_id))
    conn.commit()
    return until

# ─── Commands ───────────────────────────────────────

@bot.message_handler(commands=['start'])
def cmd_start(message):
    args = message.text.split()
    uid = message.from_user.id
    add_user(uid)

    # Referral
    if len(args) > 1:
        try:
            inviter = int(args[1])
            add_referral(inviter, uid)
        except:
            pass

    text = (
        "🤖 Admin Tools Bot\n\n"
        f"📌 /all — կոչ բոլորին խմբում (պահանջվում է ակտիվ բաժանորդագրություն)\n"
        f"💰 Ամսական վճար՝ {SUBSCRIPTION_COST}⭐ Telegram Stars-ով\n\n"
        "Հրամաններ՝\n"
        "/invite   — ստացիր referral link\n"
        "/subscribe — վճարիր բաժանորդագրության համար\n"
        "/stats    — տես referral-ների քանակը\n"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['invite'])
def cmd_invite(message):
    uid = message.from_user.id
    link = f"https://t.me/{BOT_USERNAME}?start={uid}"
    text = (
        f"🔗 Քո referral հղումը՝\n{link}\n\n"
        "Հրավիրի ընկերներիդ և ստացիր bonus (հետագայում)"
    )
    bot.reply_to(message, text)

@bot.message_handler(commands=['subscribe'])
def cmd_subscribe(message):
    prices = [LabeledPrice(label='Ամսական բաժանորդագրություն', amount=SUBSCRIPTION_COST)]

    try:
        bot.send_invoice(
            chat_id=message.chat.id,
            title="Admin Tools — Ամսական մուտք",
            description=f"Անսահմանափակ /all օգտագործում խմբերում ({SUBSCRIPTION_DAYS} օր)",
            payload=f"sub_{message.from_user.id}_{int(time.time())}",
            provider_token="",                  # պարտադիր դատարկ Telegram Stars-ի համար
            currency="XTR",
            prices=prices,
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
    except Exception as e:
        bot.reply_to(message, f"Վրեպ invoice ուղարկելիս:\n{str(e)}")

@bot.pre_checkout_query_handler(func=lambda q: True)
def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment_handler(message):
    uid = message.from_user.id
    payload = message.successful_payment.invoice_payload
    amount = message.successful_payment.total_amount

    if payload.startswith("sub_"):
        until = activate_subscription(uid)
        date_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(until))
        text = (
            f"✅ Վճարումը հաջողվեց!\n"
            f"Վճարվել է՝ {amount}⭐\n"
            f"Բաժանորդագրությունը ակտիվ է մինչև՝ {date_str}"
        )
        bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['stats'])
def cmd_stats(message):
    uid = message.from_user.id
    c.execute("SELECT COUNT(*) FROM referrals WHERE inviter_id = ?", (uid,))
    count = c.fetchone()[0]
    bot.reply_to(message, f"👥 Դուք հրավիրել եք՝ {count} օգտատեր")

@bot.message_handler(commands=['all'])
def cmd_all(message):
    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "❌ /all աշխատում է միայն խմբերում / supergroups-ում։")
        return

    uid = message.from_user.id
    if not is_subscribed(uid):
        bot.reply_to(message, f"❌ Բաժանորդագրություն չունես։ Վճարիր /subscribe-ով ({SUBSCRIPTION_COST}⭐)")
        return

    # Telegram-ը չի տալիս բոտերին բոլոր անդամներին tag անել → պարզ տեքստ
    bot.reply_to(message, "📢 Attention everyone!\n/all կանչվեց ադմինի կողմից!\n(բոտը չի կարող tag անել բոլորին — սա Telegram-ի սահմանափակում է)")

# ─── Start ──────────────────────────────────────────
if __name__ == "__main__":
    print("Bot is starting...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Critical error: {e}")
        time.sleep(10)
