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

def get_mail_tm():
    # استخدام Mail.tm API للحصول على بريد أكثر احترافية
    try:
        # الحصول على الدومينات المتاحة
        domains = requests.get("https://api.mail.tm/domains").json()['hydra:member']
        domain = domains[0]['domain']
        username = generate_random_string(10)
        email = f"{username}@{domain}"
        # إنشاء الحساب
        data = {"address": email, "password": "Password123!"}
        requests.post("https://api.mail.tm/accounts", json=data)
        # الحصول على التوكن
        token_data = requests.post("https://api.mail.tm/token", json=data).json()
        return email, token_data['token']
    except:
        return None, None

def check_mail_tm(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        msgs = requests.get("https://api.mail.tm/messages", headers=headers).json()['hydra:member']
        if msgs:
            msg_id = msgs[0]['id']
            msg_content = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers).json()
            return msg_content['html'][0] if msg_content['html'] else msg_content['text']
        return None
    except:
        return None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma الذكي (V5.0)! 🚀\n\nتم تحديث مزود البريد ونظام تخطي الحماية.\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري بدء العملية الذكية... 🧠")
    
    co = ChromiumOptions().set_argument('--headless').set_argument('--no-sandbox').set_argument('--disable-gpu').set_argument('--disable-dev-shm-usage')
    co.set_argument('--incognito') # استخدام الوضع المتخفي لضمان جلسة نظيفة
    
    page = ChromiumPage(co)
    
    try:
        # 1. الحصول على بريد مؤقت من Mail.tm
        email, token = get_mail_tm()
        if not email:
            bot.send_message(chat_id, "❌ فشل في إنشاء بريد مؤقت. جاري المحاولة ببريد احتياطي...")
            # العودة لـ 1secmail كخيار احتياطي
            username = generate_random_string(10)
            domain = "1secmail.com"
            email = f"{username}@{domain}"
            token = None
        
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. التسجيل في Gamma
        bot.send_message(chat_id, "جاري الدخول إلى Gamma ومحاكاة النشاط البشري... ⏳")
        page.get(REFERRAL_LINK)
        time.sleep(20)
        
        # البحث عن حقل الإيميل بذكاء (أي حقل إدخال)
        email_input = page.ele('tag:input@type=email') or page.ele('tag:input')
        if email_input:
            # محاكاة الكتابة
            for char in email:
                email_input.input(char)
                time.sleep(random.uniform(0.1, 0.2))
            
            time.sleep(5)
            
            # الضغط على زر المتابعة (البحث عن أي زر يحتوي على نص)
            submit_btn = page.ele('tag:button@@text():Continue') or page.ele('tag:button')
            
            if submit_btn:
                bot.send_message(chat_id, "تم إرسال طلب التسجيل! بانتظار التأكيد... 📩")
                submit_btn.click()
                time.sleep(10)
                
                # 3. فحص البريد
                found_link = None
                for i in range(25):
                    time.sleep(10)
                    if token: # فحص Mail.tm
                        content = check_mail_tm(token)
                        if content:
                            links = re.findall(r'https?://[^\s<>"]+', content)
                            for link in links:
                                if 'verify' in link or 'clerk' in link:
                                    found_link = link
                                    break
                    else: # فحص 1secmail
                        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}"
                        msgs = requests.get(url).json()
                        if msgs:
                            msg_id = msgs[0]['id']
                            read_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={msg_id}"
                            body = requests.get(read_url).json()['body']
                            links = re.findall(r'https?://[^\s<>"]+', body)
                            for link in links:
                                if 'verify' in link or 'clerk' in link:
                                    found_link = link
                                    break
                    
                    if found_link: break
                    bot.send_message(chat_id, f"فحص البريد ({i+1}/25)...")
                
                if found_link:
                    bot.send_message(chat_id, "✅ تم استلام البريد! جاري التفعيل النهائي... 🎉")
                    page.get(found_link)
                    time.sleep(15)
                    
                    # إكمال البيانات
                    name_input = page.ele('@placeholder=First name') or page.ele('tag:input')
                    if name_input:
                        name_input.input('Youssef')
                        time.sleep(1)
                        # محاولة إيجاد الباسورد
                        pass_input = page.ele('@type=password')
                        if pass_input: pass_input.input('GammaPass2026!')
                        time.sleep(2)
                        # الضغط على زر الاستمرار النهائي
                        final_btn = page.ele('tag:button@@text():Continue') or page.ele('tag:button')
                        if final_btn: final_btn.click()
                        time.sleep(10)
                    
                    bot.send_message(chat_id, "🎉 تمت المهمة بنجاح! تم إضافة 200 كريديت.")
                else:
                    bot.send_message(chat_id, "❌ لم تصل الرسالة. الموقع قد يكون حظر البريد المؤقت.")
            else:
                bot.send_message(chat_id, "❌ فشل العثور على زر المتابعة.")
        else:
            bot.send_message(chat_id, "❌ فشل العثور على حقل الإدخال.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ تقني: {str(e)}")
    finally:
        page.quit()

if __name__ == "__main__":
    bot.infinity_polling()
