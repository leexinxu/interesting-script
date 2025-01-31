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


def get_series_map(bili_client):
    """获取合集名称和ID的映射关系"""
    try:
        series_url = 'https://member.bilibili.com/x2/creative/web/seasons'
        params = {
            'pn': 1,
            'ps': 30  # 增加每页数量以获取更多合集
        }
        
        response = bili_client._BiliBili__session.get(series_url, params=params)
        result = response.json()
        
        if result['code'] == 0:
            series_map = {}
            series_list = result['data']['seasons']
            for series in series_list:
                series_map[series['season']['title']] = series['sections']['sections'][0]['id']
            return series_map
        else:
            print(f"获取合集列表失败: {result['message']}")
            return {}
            
    except Exception as e:
        print(f'获取合集列表失败：{e}')
        return {}

def add_to_series(bili_client, aid, title, series_name):
    """添加视频到合集
    Args:
        bili_client: BiliBili客户端实例
        aid: 视频的aid
        title: 视频标题
        series_name: 合集名
    Returns:
        bool: 是否成功添加到合集
    """
    try:
        # 获取合集映射，合集名对应合集id
        series_map = get_series_map(bili_client)
        print(f'{series_map=}')
        
        if series_name not in series_map:
            print(f'未找到合集: {series_name}')
            return False
            
        series_id = series_map[series_name]
        
        # 调用添加到合集的API
        add_series_url = 'https://member.bilibili.com/x2/creative/web/season/section/episodes/add?csrf='+bili_client._BiliBili__bili_jct
        add_series_data = {
            "sectionId": series_id,
            "episodes": [{
                "title": title,
                "aid": aid
            }]
        }
        print(f"添加到合集：{add_series_data=}")
        response = bili_client._BiliBili__session.post(add_series_url, json=add_series_data)
        series_result = response.json()
        print(f"添加到合集结果：{series_result}")
        
        return series_result.get('code') == 0
        
    except Exception as e:
        print(f'添加到合集失败：{e}')
        return False


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
    description = f'{summary["summary"]}\n{title_English}\n{summary["author"]}'

    # 获取视频分类
    category = folder.split('/')[6]  # 根据路径结构提取
    keywords = ['中配男', '多角色', '原音色克隆']
    if any(keyword in category for keyword in keywords):
        category = '中配'

    title = f'【{category}】{summary["title"]}'

    # 去除空格并获取前10个标签
    tags = [tag[:20].replace(" ", "") for tag in tags][:10]

    # 标题长度不能超过80个字符
    title = title[:80]

    # 打印视频文件名、标题和标签
    print(f"视频文件名：{video_path}")
    print(f"标题：{title}")
    print(f"标签：{tags}")

    video = Data()
    video.copyright = 2   # 1自制 2转载
    video.title = title
    video.tid = 232 # 设置视频分区, 231 科技->计算机技术, 232 科技->工业·工程·机械 , https://biliup.github.io/tid-ref.html
    video.set_tag(tags)
    video.desc = description
    if video.copyright == 2:
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

            if ret['code'] == 0:
                # 添加视频到合集
                add_to_series(bili, ret['data']['aid'], title, category)

            with open(os.path.join(folder, 'bilibili.json'), 'w', encoding='utf-8') as f:
                json.dump(ret, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f'上传到B站发生异常，捕获，不影响后续处理，{e=}')
            with open(os.path.join(folder, 'bilibili.json'), 'w', encoding='utf-8') as f:
                json.dump({"e": str(e)}, f, ensure_ascii=False, indent=4)
    
    return True    

# %%
# 破浪
with open('data/bilibili_cookie_polang.json', 'r') as f:
    cookie_polang = json.load(f)

# 长风
with open('data/bilibili_cookie_changfeng.json', 'r') as f:
    cookies_changfeng = json.load(f)

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
            upload(up_dir, cookies_changfeng)

            # 防止提交过快
            log("防止提交过快，等待1分钟上传下一个。。。")
            time.sleep(60)

        log("等待10分钟再检查。。。")
        time.sleep(60*10)


# %%
# 启动自动视频翻译系统
src_dir = '/Volumes/Data/AI/YouDub-webui/videos'
check_up(src_dir)



