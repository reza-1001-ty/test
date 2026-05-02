import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from file_part import split_file
from rubika_client import rubika

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_PATH = "./downloads/"

# صف برای مدیریت پردازش فایل‌ها
job_queue = asyncio.Queue()


async def worker():
    """وظیفه‌ی پس‌زمینه که فایل‌ها را به ترتیب از صف برداشته و پردازش می‌کند."""
    while True:
        job = await job_queue.get()
        try:
            await job()          # اجرای وظیفه (coroutine)
        except Exception as e:
            print(f"[QUEUE] خطا در پردازش وظیفه: {e}")
        finally:
            job_queue.task_done()


@app.on_message(
    filters.document
    | filters.video
    | filters.photo
    | filters.audio
    | filters.voice
    | filters.video_note
    | filters.animation
    | filters.sticker
)
async def handle_file(client: Client, message: Message):
    # پاسخ سریع برای اطلاع به کاربر
    status_msg = await message.reply("⏳ فایل به صف پردازش اضافه شد...")

    # تعریف وظیفه‌ای که بعداً اجرا می‌شود
    async def process():
        try:
            await status_msg.edit_text("⏳ در حال دریافت فایل...")
            print(f"[DOWNLOAD] شروع دانلود فایل...")
            file_path = await message.download(file_name=DOWNLOAD_PATH)

            if not file_path:
                await status_msg.edit_text("❌ دانلود فایل ناموفق بود.")
                return

            print(f"[DOWNLOAD] فایل با موفقیت در {file_path} ذخیره شد.")
            await status_msg.edit_text("✅ فایل دانلود شد. در حال ارسال...")

            # اجرای split_file در یک thread جداگانه (تابع همزمان است)
            loop = asyncio.get_running_loop()
            parts_list = await loop.run_in_executor(None, split_file, file_path)

            for part in parts_list:
                # ارسال هر تکه از فایل (rubika.send_file همزمان است)
                result = await loop.run_in_executor(None, rubika.send_file, part, "File")
                if result["success"]:
                    print(f"[UPLOAD] تکه {part} با موفقیت ارسال شد.")
                else:
                    print(f"[UPLOAD] خطا در ارسال {part}: {result.get('error')}")

            await status_msg.edit_text("✅ آپلود کامل شد.")
        except Exception as e:
            print(f"[ERROR] خطا در پردازش صف: {e}")
            await status_msg.edit_text(f"❌ مشکلی پیش آمد:\n`{str(e)}`")

    # افزودن وظیفه به صف
    await job_queue.put(process)


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    welcome_text = (
        "👋 سلام! من ربات دانلود و آپلود فایل هستم.\n\n"
        "📎 هر فایلی برام بفرستی، به صف اضافه می‌شه و به ترتیب دانلود و آپلود می‌کنم.\n\n"
        "📂 فرمت‌های پشتیبانی شده:\n"
        "• اسناد (Document)\n"
        "• ویدیو (Video)\n"
        "• عکس (Photo)\n"
        "• صدا (Audio)\n"
        "• گیف (Animation)\n"
        "• استیکر (Sticker)\n"
        "• پیام صوتی (Voice)\n"
        "• ویدیو مسیج (Video Note)"
    )
    await message.reply(welcome_text)


@app.on_message()
async def other_messages(client: Client, message: Message):
    await message.reply("⚠️ لطفاً یک فایل ارسال کنید تا به صف اضافه کنم.")


if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
        print(f"📁 پوشه {DOWNLOAD_PATH} ساخته شد.")

    # شروع تسک worker
    app.loop.create_task(worker())
    print("🤖 ربات در حال اجرا...")
    app.run()
