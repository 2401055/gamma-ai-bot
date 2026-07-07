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
    domain = random.choice(['1secmail.com', '1secmail.org', '1secmail.net'])
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
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma المطور! 🚀\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري بدء العملية باستخدام محاكي المتصفح لضمان تخطي الحماية... 🛡️")
    
    co = ChromiumOptions().set_argument('--headless').set_argument('--no-sandbox')
    page = ChromiumPage(co)
    
    try:
        # 1. الحصول على بريد مؤقت
        username, domain, email = get_temp_mail()
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. التسجيل في Gamma عبر المتصفح
        page.get(REFERRAL_LINK)
        time.sleep(5)
        
        # البحث عن حقل الإيميل وإدخاله
        email_input = page.ele('@id=email')
        if email_input:
            email_input.input(email)
            time.sleep(1)
            # البحث عن زر المتابعة والضغط عليه
            submit_btn = page.ele('tag:button@@text():Continue with email')
            if not submit_btn:
                submit_btn = page.ele('@@text():Continue with email')
            
            if submit_btn:
                submit_btn.click()
                bot.send_message(chat_id, "تم إدخال البريد بنجاح. بانتظار رسالة التأكيد... 📩")
                
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
                    bot.send_message(chat_id, "✅ تم العثور على الرابط! جاري التفعيل النهائي...")
                    page.get(found_link)
                    time.sleep(10)
                    
                    # إكمال بيانات الحساب إذا طلب الموقع (الاسم والباسورد)
                    if page.ele('@placeholder=First name'):
                        page.ele('@placeholder=First name').input('Alex')
                        page.ele('@placeholder=Last name').input('Dev')
                        page.ele('@type=password').input('Gamma@2026')
                        page.ele('tag:button@@text():Continue').click()
                        time.sleep(5)
                    
                    bot.send_message(chat_id, "🎉 تمت العملية بنجاح! تم إضافة 200 كريديت لحسابك.")
                else:
                    bot.send_message(chat_id, "❌ فشل في استلام البريد. قد يكون الموقع حظر النطاق.")
            else:
                bot.send_message(chat_id, "❌ لم يتم العثور على زر التسجيل.")
        else:
            bot.send_message(chat_id, "❌ لم يتم العثور على حقل الإدخال.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ: {str(e)}")
    finally:
        page.quit()

if __name__ == "__main__":
    bot.infinity_polling()
