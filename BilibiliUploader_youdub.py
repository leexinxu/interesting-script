# %%
from biliup.plugins.bili_webup import BiliBili, Data
import os
from datetime import datetime
import time
import json

# %%
def log(message):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_time} - {message}")

# %%
def find_videos(folder):
    dir_list = []
    for dir, _, files in os.walk(folder):
        if 'ok.json' in files and 'video.mp4' in files and 'bilibili.json' not in files:
            dir_list.append(dir)
    return dir_list

# %%
# 上传视频到B站
def upload(folder, cookies):
    log(f"上传视频到B站 {folder=}")

    video_path = os.path.join(folder, 'video.mp4')
    cover_path = os.path.join(folder, 'video.png')

    # Load summary data
    with open(os.path.join(folder, 'summary.json'), 'r', encoding='utf-8') as f:
        summary = json.load(f)
    summary['title'] = summary['title'].replace('视频标题：', '').strip()
    summary['summary'] = summary['summary'].replace(
        '视频摘要：', '').replace('视频简介：', '').strip()
    tags = summary.get('tags', [])
    if not isinstance(tags, list):
        tags = []
    
    with open(os.path.join(folder, 'download.info.json'), 'r', encoding='utf-8') as f:
        data = json.load(f)
    title_English = data['title']
    webpage_url = data['webpage_url']
    description = f'{summary["summary"]}\n\n{summary["author"]}\n\n{webpage_url}'

    title = f'【中配】{summary["title"]}【{title_English}】'

    # 去除空格并获取前10个标签
    tags = [tag[:20].replace(" ", "") for tag in tags][:10]

    # 标题长度不能超过80个字符
    title = title[:80]

    # 打印视频文件名、标题和标签
    print(f"视频文件名：{video_path}")
    print(f"标题：{title}")
    print(f"标签：{tags}")

    video = Data()
    video.copyright = 1   # 1自制 2转载
    video.title = title
    video.tid = 231 # 设置视频分区, 231 科技->计算机技术, https://biliup.github.io/tid-ref.html
    video.set_tag(tags)

    if video.copyright == 1:
        video.desc = description
    else:
        video.source = webpage_url

    print(f'{video=}')

    with BiliBili(video) as bili:
        bili.login_by_cookies(cookie=cookies)

        video_part = bili.upload_file(filepath=video_path)  # 上传视频

        # 防止报标题超过80字符的错误
        video_part['title'] = title
        print(f'{video_part=}')

        video.append(video_part)  # 添加已经上传的视频
        try:
            ret = bili.submit(submit_api='web')  # 提交视频
            print(f'{ret=}')

            with open(os.path.join(folder, 'bilibili.json'), 'w', encoding='utf-8') as f:
                json.dump(ret, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f'上传到B站发生异常，捕获，不影响后续处理，{e=}')
            with open(os.path.join(folder, 'bilibili.json'), 'w', encoding='utf-8') as f:
                json.dump({"e": str(e)}, f, ensure_ascii=False, indent=4)
    
    return True    

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
def check_up(src_dir):
    log(f"******* 启动上传到B站脚本, 检查视频目录: {src_dir} *******")
    while True:
        log("检查是否有视频需要上传到B站...")
        up_dir_list = find_videos(src_dir)
        log(f"找到需要上传B站: {len(up_dir_list)}")
        for up_dir in up_dir_list:
            # 上传视频到B站
            upload(up_dir, cookies)

            # 防止提交过快
            log("防止提交过快，等待1分钟上传下一个。。。")
            time.sleep(60)

        log("等待10分钟再检查。。。")
        time.sleep(60*10)


# %%
# 启动自动视频翻译系统
src_dir = '/Volumes/Data/AI/YouDub-webui/videos_20240808'
check_up(src_dir)


