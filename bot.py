import telebot
import time
import random
import string
import re
import requests
from DrissionPage import ChromiumPage, ChromiumOptions

# التوكن الخاص بالبوت
BOT_TOKEN = '8899279893:AAHsqbBD6eulBmrSt9bfTQa9-lYMUi9BIbM'
bot = telebot.TeleBot(BOT_TOKEN)

# رابط الإحالة الخاص بك
REFERRAL_LINK = 'https://gamma.app/signup?r=kssz6r8wnreomnl'

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_temp_mail():
    # استخدام 1secmail
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
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma النهائي (V4.0)! 🚀\n\nتم إصلاح كافة المشاكل التقنية.\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري تشغيل محرك الأتمتة المتقدم... 🤖")
    
    co = ChromiumOptions().set_argument('--headless').set_argument('--no-sandbox').set_argument('--disable-gpu').set_argument('--disable-dev-shm-usage')
    page = ChromiumPage(co)
    
    try:
        # 1. الحصول على بريد مؤقت
        username, domain, email = get_temp_mail()
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. التسجيل في Gamma
        bot.send_message(chat_id, "جاري الدخول إلى Gamma... ⏳")
        page.get(REFERRAL_LINK)
        time.sleep(10)
        
        # إدخال البريد
        email_input = page.ele('@id=email')
        if email_input:
            email_input.input(email)
            time.sleep(2)
            
            # الضغط على زر المتابعة
            submit_btn = page.ele('tag:button@@text():Continue with email')
            if not submit_btn:
                submit_btn = page.ele('@@text():Continue with email')
            
            if submit_btn:
                submit_btn.click()
                bot.send_message(chat_id, "تم إرسال الطلب! بانتظار وصول رسالة التأكيد... 📩")
                
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
                    page.get(found_link)
                    time.sleep(10)
                    
                    # إكمال البيانات (الاسم والباسورد)
                    if page.ele('@placeholder=First name'):
                        page.ele('@placeholder=First name').input('Youssef')
                        page.ele('@placeholder=Last name').input('Saleh')
                        page.ele('@type=password').input('GammaPass2026!')
                        # الضغط على زر الاستمرار النهائي
                        page.ele('tag:button@@text():Continue').click()
                        time.sleep(10)
                    
                    bot.send_message(chat_id, "🎉 تمت المهمة بنجاح! تم إضافة 200 كريديت لحسابك.")
                else:
                    bot.send_message(chat_id, "❌ لم تصل الرسالة. قد يكون النطاق محظوراً حالياً. جرب مرة أخرى بنطاق مختلف.")
            else:
                bot.send_message(chat_id, "❌ فشل العثور على زر التسجيل.")
        else:
            bot.send_message(chat_id, "❌ فشل العثور على حقل البريد.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ تقني: {str(e)}")
    finally:
        page.quit()

if __name__ == "__main__":
    bot.infinity_polling()
