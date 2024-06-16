# %%
from biliup.plugins.bili_webup import BiliBili, Data
import os
from datetime import datetime
import glob
import shutil
import time

# %%
def log(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} - {message}")

# %%
def find_chinese_subbed_videos(base_folder):
    file_list = []
    
    # 遍历第一层文件夹
    for root, dirs, files in os.walk(base_folder):
        # 查找当前目录下符合模式的文件
        for file in glob.glob(os.path.join(root, '【中配】*.mp4')):
            file_list.append(os.path.abspath(file))
        
        # 遍历第二层文件夹
        for sub_dir in dirs:
            sub_dir_path = os.path.join(root, sub_dir)
            for file in glob.glob(os.path.join(sub_dir_path, '【中配】*.mp4')):
                file_list.append(os.path.abspath(file))
        
        # 只遍历两级，跳过子目录的子目录
        break
    
    return file_list

# %%
def move_folder(src_folder, dst_dir):
    try:
        # 创建目标目录（如果不存在）
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        # 移动文件夹
        shutil.move(src_folder, os.path.join(dst_dir, os.path.basename(src_folder)))
        log(f"Moved: {src_folder} to {dst_dir}")
    except Exception as e:
        log(f"Error moving folder {src_folder}: {e}")

# %%
def upload(filepath, cookies):
    if not os.path.exists(filepath):
        print(f'{filepath} not exists')
        return

    # 获取文件名, 文件名示例：【中配】人工智能【AI】
    filename = os.path.splitext(os.path.basename(filepath))[0]

    # 截取到最后一个 '【' 之前的内容
    title_part = filename[:filename.rfind('【')].strip()
    # 确保长度不超过80个字符
    max_length = 80
    if len(title_part) > max_length:
        title_part = title_part[:max_length].rsplit(' ', 1)[0]

    video = Data()
    video.copyright = 1   # 1自制 2转载
    video.title = title_part
    video.tid = 231 # 设置视频分区, 231 科技->计算机技术, https://biliup.github.io/tid-ref.html
    video.set_tag(['破浪', '科技', '未来', 'AI', '人工智能', 'AGI'])

    if video.copyright == 1:
        video.desc = filename[filename.rfind('【')+1:len(filename)-1]
    else:
        video.source = f"破浪 {filename[filename.rfind('【'):]}"

    print(f'{video=}')

    with BiliBili(video) as bili:
        bili.login_by_cookies(cookie=cookies)

        video_part = bili.upload_file(filepath=filepath)  # 上传视频

        # 防止报标题超过80字符的错误
        video_part['title'] = title_part
        print(f'{video_part=}')

        video.append(video_part)  # 添加已经上传的视频
        
        ret = bili.submit(submit_api='web')  # 提交视频
        print(f'{ret=}')

# %%
cookies = {
    'SESSDATA': 'f3fcfcf7,1733529039,ad1ea*61CjDDEelwr9JIeM99tZouwySvYaDbFGC-8Rpa-UkVxlTXb-QjZkZc4wewrI6TYZeopwMSVmlUb3J6N1lGS3h5YmdtMDdIX3lnRFFSOXNNd2pqSWVYZmV0LXp5dzRYa0VrTEgxTlVpUzhRVjQwQ21HMjFxNW5yWUplM1ZVekFBLTNJNWlncnZubUhnIIEC',
    'bili_jct': '8b12cd2116875005ad57ea3af6362e96',
    'sid': '5xbu4ygu',
    
    'DedeUserID': '3546691640756518',
    'DedeUserID__ckMd5': 'd0df0ac5cb88bd0e',
}

# %%
# 每分钟检查一下是否有新翻译完成的视频，如果有，则上传B站
def check_trans_completed_up(src_dir, dst_dir):
    log("******* Start Auto Video Bilibili Uploader *******")
    while True:
        log("Checking for new videos...")
        # 获取目录中两级的【中配】*.mp4文件
        mp4_files = find_chinese_subbed_videos(src_dir)
        log(f"Get new videos : {len(mp4_files)}")
        for mp4_file in mp4_files:
            # 上传视频到B站
            upload(mp4_file, cookies)
            
            # 上传完移动文件夹到TranslationCompletedUploadBilibiliMove
            move_folder(os.path.dirname(mp4_file), dst_dir)

            # 防止提交过快
            log("Waiting for 60 seconds before next upload...")
            time.sleep(60)

        # 等待 60 秒再检查
        log("Waiting for 60 seconds before next check...")
        time.sleep(60)

# %%
# 启动自动视频翻译系统
source_directory = '/Volumes/Data/VideoTranslation/TranslationCompleted'
destination_directory = '/Volumes/Data/VideoTranslation/TranslationCompletedUploadBilibiliMove'
check_trans_completed_up(source_directory, destination_directory)


