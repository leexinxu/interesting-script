# %%
import schedule
import time
import subprocess
import os
from datetime import datetime
import chinese_calendar

# %%
def is_todesk_running():
    import psutil
    """检查ToDesk是否正在运行"""
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        #print(f'{datetime.now()} - ToDesk Running proc = {proc.info}')
        if proc.info['name'] == 'ToDesk' and proc.info['status'] == psutil.STATUS_RUNNING:
            print(f'{datetime.now()} - ToDesk Running')
            return True
    print(f'{datetime.now()} - ToDesk Not Running')
    return False

# %%
def start_todesk():
    """启动ToDesk应用"""
    print(f'{datetime.now()} - ToDesk start...')
    if not is_todesk_running():
        subprocess.Popen(["/Applications/ToDesk.app/Contents/MacOS/ToDesk"])
        print(f'{datetime.now()} - ToDesk started')

def stop_todesk():
    """关闭ToDesk应用"""
    print(f'{datetime.now()} - ToDesk stop...')
    if is_todesk_running():
        os.system("pkill -f ToDesk")
        print(f'{datetime.now()} - ToDesk stopped')

# %%
def is_workday(date):
    """判断给定日期是否为工作日"""
    return chinese_calendar.is_workday(date)

# %%
# 创建一个特定日期
test_date = datetime(2024, 9, 14)

# 检查该日期是否为工作日
if is_workday(test_date):
    print(f"{test_date.date()} 是工作日")
else:
    print(f"{test_date.date()} 不是工作日")

# %%
def job():
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()
    # 打印当前时间、小时和星期几
    print(f'job() Run: Current time: {now}, Hour: {current_hour}, Weekday: {current_weekday}')
    # 检查是否在工作日和指定时间范围内
    if is_workday(now) and 7 <= current_hour < 19:
        start_todesk()
    else:
        stop_todesk()

# %%
job()

# %%
# 安排任务每10分钟调度一次job函数
schedule.every(10).minutes.do(job)

# %%
while True:
    # 每分钟检查一次是否有任务调度
    schedule.run_pending()
    time.sleep(60)


