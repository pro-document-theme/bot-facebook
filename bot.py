import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from playwright.async_api import async_playwright

# --- خادم وهمي لإبقاء السيرفر المجاني شغال 24/7 ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is online and running successfully!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

# بدء الخادم في الخلفية
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- تنظيف النصوص والأوامر ---
def normalize_text(text):
    if not text:
        return ""
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي")
    return text.strip().lower()

# الأوامر المتاحة في البوت
commands_dict = {
    "اوامر": "مرحباً بك يا غالي. إليك الأوامر المتاحة:\n- .اوامر\n- .سلام\n- .اهلاً",
    "سلام": "وعليكم السلام ورحمة الله وبركاته!",
    "اهلاً": "أهلاً بك يا صاحبي منور الدنيا!"
}

async def main():
    async with async_playwright() as p:
        # تشغيل المتصفح في وضع الخفاء (headless=True) لأنه سيرفر بدون شاشة
        browser = await p.firefox.launch(headless=True)
        
        # استخدام ملف الـ state.json لتسجيل الدخول تلقائياً عبر الكوكيز
        context = await browser.new_context(storage_state="state.json")
        page = await context.new_page()

        # رابط الجروب أو الشات المحدد
        chat_url = "https://www.messenger.com/t/27173566308963283"
        
        print("جاري فتح الشات وتسجيل الدخول عبر الكوكيز...")
        await page.goto(chat_url, wait_until="domcontentloaded")
        print("✅ البوت متصل بالجروب وجاهز للمراقبة والرد 24/7...")
        
        last_message = ""

        while True:
            try:
                await asyncio.sleep(3)
                # سحب آخر الرسائل من صندوق الشات
                messages = await page.locator('div[dir="auto"]').all_inner_texts()
                
                if not messages:
                    continue
                    
                current_raw_message = messages[-1].strip()
                
                if current_raw_message != last_message:
                    last_message = current_raw_message
                    reply = ""

                    clean_message = normalize_text(current_raw_message)

                    # فحص الأوامر التي تبدأ بـ نقطة (.)
                    if clean_message.startswith("."):
                        command = clean_message[1:].strip()
                        print(f"📩 أمر جديد تم استلامه: {command}")
                        
                        if command in commands_dict:
                            reply = commands_dict[command]
                        else:
                            reply = "عذراً، أمر غير معروف. اكتب '.اوامر' لعرض القائمة."

                    # إرسال الرد في شريط الكتابة والضغط إنتر
                    if reply:
                        await page.fill('div[role="textbox"]', reply)
                        await page.press('div[role="textbox"]', 'Enter')
                        print("✅ تم الرد بنجاح.")
                        
            except Exception as e:
                print(f"حدث خطأ مؤقت: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
