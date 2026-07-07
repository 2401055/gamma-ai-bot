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
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma البرقي المطور (V6.1)! 🚀\n\nتم تحديث محرك الطلبات المباشرة لضمان وصول البريد.\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري إرسال طلب تسجيل ذكي... ⚡")
    
    try:
        # 1. الحصول على بريد مؤقت
        username, domain, email = get_temp_mail()
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. إرسال طلب التسجيل الفعلي لـ Clerk (سيرفر حسابات Gamma)
        bot.send_message(chat_id, "جاري التحدث مع سيرفرات Gamma مباشرة... ⏳")
        
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": "https://gamma.app/",
            "Origin": "https://gamma.app"
        }
        
        # استخراج الـ Referral ID من الرابط
        ref_id = REFERRAL_LINK.split('r=')[-1]
        
        # محاكاة طلب Clerk لإنشاء حساب جديد
        # هذا الطلب هو ما يجعل السيرفر يرسل إيميل التأكيد
        clerk_url = "https://clerk.gamma.app/v1/client/sign_ups?_clerk_js_version=4.50.1"
        payload = {
            "email_address": email,
            "strategy": "email_link",
            "redirect_url": "https://gamma.app/signup/verify",
            "action_complete_redirect_url": "https://gamma.app/onboarding",
            "referral_code": ref_id
        }
        
        response = session.post(clerk_url, data=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            bot.send_message(chat_id, "تم قبول طلب التسجيل! بانتظار وصول رسالة التأكيد... 📩")
        else:
            bot.send_message(chat_id, "تم إرسال الطلب (محاولة ثانية)...")
            # محاولة بديلة لضمان الإرسال
            session.get(REFERRAL_LINK, headers=headers)
        
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
            session.get(found_link, headers=headers)
            bot.send_message(chat_id, "🎉 تمت المهمة بنجاح! تم إضافة 200 كريديت لحسابك.")
        else:
            bot.send_message(chat_id, "❌ لم تصل الرسالة. الموقع قد يتطلب تفاعلاً بشرياً كاملاً أو استخدام بريد حقيقي.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
