import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from file_part import split_file
from rubika_client import rubika

API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# for test
# proxy = {
#     "scheme": "http",
#     "hostname": "192.168.49.1",
#     "port": "8282"
# }

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DOWNLOAD_PATH = "./downloads/"

# صف برای پردازش متوالی فایل‌ها
file_queue = asyncio.Queue()


async def process_file_worker():
    """کارگری که فایل‌ها را یکی‌یکی از صف برمی‌دارد و پردازش می‌کند."""
    while True:
        # دریافت یک آیتم از صف (اگر صف خالی باشد منتظر می‌ماند)
        message, status_msg = await file_queue.get()
        try:
            # به‌روزرسانی پیام وضعیت: دریافت فایل
            await status_msg.edit_text("⏳ در حال دریافت فایل... لطفاً صبر کنید.")

            print(f"[DOWNLOAD] شروع دانلود فایل...")
            file_path = await message.download(file_name=DOWNLOAD_PATH)

            if file_path:
                print(f"[DOWNLOAD] فایل با موفقیت در {file_path} ذخیره شد.")

                await status_msg.edit_text("✅ فایل دانلود شد. در حال ارسال...")

                parts_list = split_file(file_path)
                # ارسال هر بخش با استفاده از تابع همگام rubika.send_file در یک thread جدا
                for part in parts_list:
                    # اگر rubika.send_file همگام (sync) است، با asyncio.to_thread اجرا می‌کنیم
                    await asyncio.to_thread(rubika.send_file, part, "File")

                await status_msg.edit_text("✅ فایل با موفقیت آپلود شد.")
                # در صورت تمایل می‌توانید پیام دیگری هم بفرستید
                # await message.reply("اپلود فایل انجام شد")
            else:
                await status_msg.edit_text("❌ خطا در دانلود فایل.")
        except Exception as e:
            print(f"[ERROR] خطا در پردازش فایل: {e}")
            await status_msg.edit_text(f"❌ خطا: {str(e)[:200]}")
            # می‌توانید به فرستنده نیز اطلاع دهید
            # await message.reply(f"❌ متأسفانه خطایی رخ داد:\n`{str(e)}`")
        finally:
            # علامت‌گذاری به‌عنوان انجام‌شده در صف
            file_queue.task_done()


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
    """دریافت فایل و اضافه کردن آن به صف پردازش."""
    try:
        # ارسال پیام اولیه برای وضعیت صف
        status_msg = await message.reply("🔢 فایل شما در صف پردازش قرار گرفت...")
        # اضافه کردن به صف (پردازش توسط worker انجام می‌شود)
        await file_queue.put((message, status_msg))
    except Exception as e:
        print(f"[ERROR] خطا در افزودن به صف: {e}")
        await message.reply(f"❌ خطا در افزودن فایل به صف:\n`{str(e)}`")


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    welcome_text = (
        "👋 سلام! من ربات دانلود و آپلود فایل هستم.\n\n"
        "📎 هر فایلی برام بفرستی، دانلودش می‌کنم و برای آپلود به سرور ارسال می‌کنم.\n\n"
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
    await message.reply("⚠️ لطفاً یک فایل ارسال کنید تا پردازش کنم.")


# راه‌اندازی worker هنگام شروع ربات
@app.on_start()
async def start_worker():
    asyncio.create_task(process_file_worker())
    print("🔄 کارگر صف آماده به کار است.")


if __name__ == "__main__":
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
        print(f"📁 پوشه {DOWNLOAD_PATH} ساخته شد.")

    print("🤖 ربات در حال اجرا...")
    app.run()
