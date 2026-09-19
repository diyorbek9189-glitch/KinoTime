MY KINO BOT — ISHGA TUSHIRISH (5 daqiqa)

1) Kutubxonalarni o'rnating:
   pip install -r requirements.txt

2) Botni guruhga qo'shing:
   - Siz bergan ssilka: https://t.me/+7_5Cq4w9vyQ1OGRi
   - Botni shu guruhga qo'shib ADMIN qiling (xabarlarni o'qish + yuborish huquqi bilan).

3) ID larni oling:
   - Botni ishga tushiring:  python bot.py
   - Guruhda:  /id   -> chat_id chiqadi (masalan -1001234567890)
   - Lichkada: /myid -> sizning user_id chiqadi
   - Shu ikkisini .env ga yozing:
       STORAGE_CHAT_ID=-100...
       ADMIN_IDS=123456789

4) Qayta ishga tushiring: python bot.py

5) Kino qo'shish (admin):
   - Guruhga kino videosini yuboring
   - O'sha videoga REPLY qilib yozing:
       /add 12 Titanic 1998
   - Tekshirish: lichkada botga  12  deb yuboring -> kino keladi.

6) Qo'shimcha buyruqlar:
   /del 12  - o'chirish
   /list    - ro'yxat
   /stat    - statistika
   /random  - tasodifiy kino (user uchun)
   /top     - top kinolar

7) Kanallar:
   .env da:
     FORCE_CHANNELS=@kanal1,@kanal2   (majburiy obuna, bo'sh bo'lsa tekshirilmaydi)
     RECOMMEND_CHANNEL=@kanal         (kino ostida "Yangi kinolar" tugmasi)
     RECOMMEND_URL=https://t.me/...   (tugma ssilkasi, bo'lsa ustun)

MUHIM: .env dagi tokenni hech kimga bermang. Ochiq joyga (github) yuklamang.
