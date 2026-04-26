from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "https://youtu.be/NXjnPUEWcmM?si=M2pQbskVTNrzb-Mo"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_highest_resolution()
ys.download()
