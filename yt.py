from pytube import YouTube
import os

video_url = "https://youtu.be/ZLaA58ANTck"

yt = YouTube(video_url)

print("📹 Video Title:", yt.title)
print("👤 Channel Name:", yt.author)
print("🔗 Channel URL:", yt.channel_url)
print("🆔 Channel ID:", yt.channel_id)
