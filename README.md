# Admin Tools Telegram Bot

Պարզ Telegram բոտ խմբերի ադմինների համար՝  
`/all` հրամանով բոլորին կանչելու հնարավորություն (subscription-ով)  
Վճարումներ Telegram Stars-ով (XTR)

## Ֆունկցիոնալ

- `/start [ref_id]` — սկիզբ + referral
- `/invite` — referral link
- `/subscribe` — վճարիր 2⭐ ամսական բաժանորդագրության համար
- `/all` — կանչիր խմբում (միայն վճարողները)
- `/stats` — referral-ների քանակը

## Տեղադրում

1. Ստեղծիր բոտը @BotFather-ում
2. Միացրու **Telegram Stars** payments-ը BotFather-ում (Payments → Telegram Stars)
3. Փոխիր `TOKEN` և `BOT_USERNAME` ֆայլում
4. Տեղադրիր կախվածությունները

```bash
pip install -r requirements.txt
