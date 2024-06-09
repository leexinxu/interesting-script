# %%
import yt_dlp
import time
from datetime import datetime

# %%
# 播放列表【破浪】
playlist_url = "https://www.youtube.com/playlist?list=PLxjtcx2z5_42QU_jjn1E9pX3YKTaxYFbD"

# 设置下载选项
ydl_opts = {
    'outtmpl': '/Volumes/Data/VideoTranslation/YouTubeDownload/%(title)s.%(id)s.%(ext)s',  # 保存路径和文件名模板
    'download_archive': '/Volumes/Data/VideoTranslation/YouTubeDownload/downloaded.txt',  # 记录已下载视频的文件
    'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',  # 下载最高质量的视频，不超过720p，并确保格式为MP4
    'merge_output_format': 'mp4',  # 合并下载的视频和音频为 mp4 格式
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4'
    }],  # 如果不是mp4 转换视频为 mp4 格式
    'writesubtitles': True, # 下载字幕
    'writeautomaticsub': True,  # 下载自动字幕
    'subtitlesformat': 'srt',  # 指定字幕格式为 srt
    'subtitleslangs': ['en', 'zh-Hans'],  # 下载英语和中文（简体）字幕
    'postprocessors': [{  # 使用字幕转换后处理器将vtt字幕转换为srt格式
        'key': 'FFmpegSubtitlesConvertor',
        'format': 'srt',
    }],
    'continuedl': True,  # 继续下载未完成的文件
    'ignoreerrors': True,  # 忽略下载错误，继续其他视频
    'proxy': '127.0.0.1:7890',  # 设置代理地址
}

# %%
while True:
    # 打印当前时间
    print(f"Checking for new videos Download at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # 下载播放列表
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])
    # 睡一分钟再去检查是否有新的下载
    time.sleep(60)


