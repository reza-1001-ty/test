import yt_dlp
import os

# لینک ویدیو از متغیر محیطی
video_url = os.environ.get("VIDEO_URL", "https://youtu.be/ZLaA58ANTck")

# تنظیمات yt-dlp
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(video_url, download=False)
    
    print("📹 Video Title:", info.get('title'))
    print("👤 Channel Name:", info.get('channel'))
    print("🔗 Channel URL:", info.get('channel_url'))
    print("🆔 Channel ID:", info.get('channel_id'))
