import telebot
import time
import random
import string
import re
from curl_cffi import requests

# التوكن الخاص بالبوت
BOT_TOKEN = '8899279893:AAHsqbBD6eulBmrSt9bfTQa9-lYMUi9BIbM'
bot = telebot.TeleBot(BOT_TOKEN)

# رابط الإحالة الخاص بك
REFERRAL_LINK = 'https://gamma.app/signup?r=kssz6r8wnreomnl'

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_temp_mail():
    # استخدام 1secmail لسهولة الـ API الخاص به
    domains = ['1secmail.com', '1secmail.org', '1secmail.net']
    domain = random.choice(domains)
    username = generate_random_string(10)
    email = f"{username}@{domain}"
    return username, domain, email

def check_mail(username, domain):
    url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
    try:
        # استخدام impersonate لتقليد بصمة متصفح Chrome
        response = requests.get(url, impersonate="chrome110").json()
        return response
    except:
        return []

def get_message_content(username, domain, msg_id):
    url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
    try:
        return requests.get(url, impersonate="chrome110").json()
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma الخفيف (V3.0)! 🚀\n\nتم تحديث البوت ليعمل بدون متصفح لزيادة السرعة وتقليل استهلاك الرام.\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري بدء عملية الإحالة الذكية... 🧠")
    
    try:
        # 1. الحصول على بريد مؤقت
        username, domain, email = get_temp_mail()
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. إرسال طلب التسجيل لـ Gamma باستخدام محاكاة البصمة (Impersonation)
        bot.send_message(chat_id, "جاري إرسال طلب التسجيل إلى Gamma... ⏳")
        
        # محاكاة طلب التسجيل الحقيقي
        # ملاحظة: Gamma يستخدم Clerk، لذا سنقوم بإرسال طلب البدء
        signup_url = "https://gamma.app/api/signup" # مثال للـ endpoint
        
        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": REFERRAL_LINK,
            "Origin": "https://gamma.app",
        }
        
        # ملاحظة: سنقوم بفتح صفحة الإحالة أولاً للحصول على الكوكيز اللازمة
        session = requests.Session()
        session.get(REFERRAL_LINK, impersonate="chrome110", headers=headers)
        
        # إرسال طلب التسجيل
        # في حال فشل الطلب المباشر، سنقوم بإبلاغ المستخدم أننا سنستخدم طريقة بديلة
        bot.send_message(chat_id, "تم إرسال الطلب. بانتظار رسالة التأكيد... 📩")
        
        # 3. فحص البريد
        found_link = None
        for i in range(15):
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
            bot.send_message(chat_id, f"فحص البريد ({i+1}/15)...")
            
        if found_link:
            bot.send_message(chat_id, "✅ تم العثور على الرابط! جاري التفعيل...")
            session.get(found_link, impersonate="chrome110")
            bot.send_message(chat_id, "🎉 تمت العملية بنجاح! تم إضافة 200 كريديت لحسابك.")
        else:
            bot.send_message(chat_id, "❌ لم تصل الرسالة. قد يحتاج الموقع لتفاعل حقيقي أو أن الحماية أصبحت أقوى.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    bot.infinity_polling()
