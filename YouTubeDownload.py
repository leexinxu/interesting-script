# %%
import yt_dlp
import time
from datetime import datetime
import os
import shutil

# %%
def move_mp4_files(src_dir, dst_dir):
    # 检查源目录是否存在
    if not os.path.exists(src_dir):
        print(f"源目录 {src_dir} 不存在")
        return

    # 检查目标目录是否存在，不存在则创建
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    # 检查源目录是否为空
    if not os.listdir(src_dir):
        print(f"源目录 {src_dir} 是空的")
        return

    # 计数器，用于跟踪移动的 .mp4 文件数量
    mp4_files_count = 0

    # 移动源目录下的所有 .mp4 文件到目标目录
    for filename in os.listdir(src_dir):
        src_file = os.path.join(src_dir, filename)
        dst_file = os.path.join(dst_dir, filename)

        if os.path.isfile(src_file) and filename.lower().endswith('.mp4'):
            shutil.move(src_file, dst_file)
            print(f"已移动 {src_file} 到 {dst_file}")
            mp4_files_count += 1

    # 根据计数器的值打印相应的消息
    if mp4_files_count > 0:
        print(f"所有 .mp4 文件已从 {src_dir} 移动到 {dst_dir}，共移动了 {mp4_files_count} 个文件。")
    else:
        print("没有需要移动的 .mp4 文件")

# %%
tmpdir = '/Volumes/Data/VideoTranslation/YouTubeDownloadTmp'  # 下载时保存路径
okdir = '/Volumes/Data/VideoTranslation/YouTubeDownload'  # 下载完成移动到该目录
downloaded = '/Volumes/Data/VideoTranslation/YouTubeDownload/downloaded.txt'  # 记录已下载视频的文件

# 播放列表【破浪】
playlist_url = "https://www.youtube.com/playlist?list=PLxjtcx2z5_42QU_jjn1E9pX3YKTaxYFbD"

# 设置下载选项
ydl_opts = {
    'outtmpl': tmpdir + '/%(title)s.%(id)s.%(ext)s',  # 保存路径和文件名模板
    'download_archive': downloaded,  # 记录已下载视频的文件
    'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',  # 下载最高质量的视频，不超过720p，并确保格式为MP4
    'merge_output_format': 'mp4',  # 合并下载的视频和音频为 mp4 格式
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4'
    }],  # 如果不是mp4 转换视频为 mp4 格式
    'writesubtitles': True, # 下载字幕
    'writeautomaticsub': False,  # 下载自动字幕
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
        # 移动文件
        move_mp4_files(tmpdir, okdir)

    # 睡一分钟再去检查是否有新的下载
    time.sleep(60)


