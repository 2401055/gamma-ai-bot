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
    bot.reply_to(message, "مرحباً بك في بوت أتمتة Gamma الخارق (V4.3)! 🚀\n\nتم تحديث البوت بتقنيات التخفي المتقدمة.\n\nاضغط على /referral للبدء.")

@bot.message_handler(commands=['referral'])
def start_referral(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "جاري تشغيل محرك الأتمتة المتخفي... 🕵️‍♂️")
    
    co = ChromiumOptions().set_argument('--headless').set_argument('--no-sandbox').set_argument('--disable-gpu').set_argument('--disable-dev-shm-usage')
    # إخفاء بصمة الأتمتة
    co.set_argument('--disable-blink-features=AutomationControlled')
    co.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    
    page = ChromiumPage(co)
    
    try:
        # 1. الحصول على بريد مؤقت
        username, domain, email = get_temp_mail()
        bot.send_message(chat_id, f"تم إنشاء بريد: {email}")
        
        # 2. التسجيل في Gamma
        bot.send_message(chat_id, "جاري محاكاة زيارة حقيقية لـ Gamma... ⏳")
        page.get(REFERRAL_LINK)
        time.sleep(20) # زيادة الوقت لتخطي أي تحدي أمان
        
        # محاولة إغلاق أي نوافذ منبثقة أو ملفات تعريف الارتباط
        try:
            cookie_btn = page.ele('@@text():Accept') or page.ele('@@text():Allow')
            if cookie_btn: cookie_btn.click()
        except: pass

        # إدخال البريد
        email_input = page.ele('@id=email') or page.ele('@type=email') or page.ele('tag:input')
        if email_input:
            # محاكاة الكتابة البشرية
            for char in email:
                email_input.input(char)
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(5)
            
            # البحث عن الزر باستخدام النص أو الترتيب
            submit_btn = page.ele('@@text():Continue with email') or page.ele('tag:button@@text():Continue with email')
            
            if not submit_btn:
                # إذا لم يجد النص، يبحث عن أي زر بعد حقل الإيميل
                submit_btn = page.ele('tag:button')
            
            if submit_btn:
                bot.send_message(chat_id, "تم العثور على الزر! جاري الضغط... 🔘")
                submit_btn.click()
                time.sleep(5)
                
                bot.send_message(chat_id, "تم إرسال الطلب بنجاح! بانتظار رسالة التأكيد... 📩")
                
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
                    time.sleep(15)
                    
                    # إكمال البيانات
                    first_name = page.ele('@placeholder=First name')
                    if first_name:
                        first_name.input('Youssef')
                        page.ele('@placeholder=Last name').input('Saleh')
                        page.ele('@type=password').input('GammaPass2026!')
                        time.sleep(3)
                        final_btn = page.ele('tag:button@@text():Continue') or page.ele('@@text():Continue')
                        if final_btn: final_btn.click()
                        time.sleep(10)
                    
                    bot.send_message(chat_id, "🎉 تمت المهمة بنجاح! تم إضافة 200 كريديت لحسابك.")
                else:
                    bot.send_message(chat_id, "❌ لم تصل الرسالة. قد يكون الموقع كشف البوت أو النطاق محظور.")
            else:
                bot.send_message(chat_id, "❌ فشل العثور على زر التسجيل. الموقع قد يكون فعل حماية Turnstile.")
        else:
            bot.send_message(chat_id, "❌ فشل العثور على حقل البريد.")
            
    except Exception as e:
        bot.send_message(chat_id, f"حدث خطأ تقني: {str(e)}")
    finally:
        page.quit()

if __name__ == "__main__":
    bot.infinity_polling()
