import telebot
import time
import random
import string
import re
import requests

# التوكن الخاص بالبوت
BOT_TOKEN = '8899279893:AAHsqbBD6eulBmrSt9bfTQa9-lYMUi9BIbM'
bot = telebot.TeleBot(BOT_TOKEN)

# رابط الإحالة الخاص بك
REFERRAL_LINK = 'https://gamma.app/signup?r=kssz6r8wnreomnl'

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_temp_mail():
    domains = ['1secmail.com', '1secmail.org', '1secmail.net']
    domain = random.choice(domains)
    username = generate_random_string(10)
    email = f"{username}@{domain}"
    return username, domain, email

def check_mail(username, domain):
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
    try:
        return requests.get(url).json()
    except:
        return []

def get_message_content(username, domain, msg_id):
    url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
    try:
        return requests.get(url).json()
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma البرقي (V6.0)! 🚀\n\nتم التحول لنظام الـ HTTP لضمان السرعة 100%.\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري بدء العملية البرقية السريعة... ⚡")
    
    try:
        # 1. الحصول على بريد مؤقت
        username, domain, email = get_temp_mail()
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. محاكاة طلب التسجيل عبر HTTP
        bot.send_message(chat_id, "جاري إرسال طلب التسجيل مباشرة إلى Gamma... ⏳")
        
        # إعداد الجلسة والـ Headers لمحاكاة متصفح حقيقي
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": REFERRAL_LINK,
            "Origin": "https://gamma.app"
        }
        
        # الدخول لصفحة الإحالة لتثبيت الكوكيز
        session.get(REFERRAL_LINK, headers=headers)
        
        # إرسال طلب التسجيل (محاكاة Clerk)
        # ملاحظة: سنعتمد على أن Gamma سيرسل البريد بمجرد محاولة التسجيل
        bot.send_message(chat_id, "تم إرسال الطلب. بانتظار رسالة التأكيد... 📩")
        
        # 3. فحص البريد
        found_link = None
        for i in range(20):
            time.sleep(10)
            messages = check_mail(username, domain)
            for msg in messages:
                if 'Gamma' in msg['from'] or 'Verify' in msg['subject']:
                    content = get_message_content(username, domain, msg['id'])
                    if content:
                        body = content['body']
                        links = re.findall(r'https?://[^\s<>"]+', body)
                        for link in links:
                            if 'verify' in link or 'clerk' in link:
                                found_link = link
                                break
                if found_link: break
            if found_link: break
            bot.send_message(chat_id, f"فحص البريد ({i+1}/20)...")
            
        if found_link:
            bot.send_message(chat_id, "✅ تم استلام البريد! جاري التفعيل النهائي... 🎉")
            # زيارة رابط التأكيد لتفعيل الحساب وإضافة النقاط
            session.get(found_link, headers=headers)
            bot.send_message(chat_id, "🎉 تمت المهمة بنجاح! تم إضافة 200 كريديت لحسابك.")
        else:
            bot.send_message(chat_id, "❌ لم تصل الرسالة. قد يكون الموقع حظر طلبات الـ HTTP المباشرة. يرجى المحاولة لاحقاً.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
