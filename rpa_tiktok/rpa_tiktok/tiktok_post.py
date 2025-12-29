import random
import requests
import datetime
from . connect_device import connect_device
import logging
import time
logger = logging.getLogger(__name__)

def perform_tiktok_post(**kwargs):
    device_id = kwargs.get('device_id')
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    video_path = kwargs.get('video_path')
    video_desc = kwargs.get('video_desc')
    # 连接设备
    logger.info(f"{device_id}连接设备")
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
        upload_video(device, video_path)
    except Exception as e:
        logger.error(f"{device_id}连接设备失败: {str(e)}")
        return {"status": "error", "message": f"连接设备失败: {str(e)}"}
    open_tiktok(device)
    try:
        post_video(device, device_id, video_desc)
    except Exception as e:
        logger.error(f"{device_id}发布视频失败: {str(e)}，截图地址{screenshot(device,"POST_ERROR", **kwargs)}")
        return {"status": "error", "message": f"发布视频失败: {str(e)}"}
    press_home(device)

def post_video(**kwargs):
    device_id = kwargs.get('device_id')
    device = kwargs.get('device')
    video_desc = kwargs.get('video_desc')
    if(device_id.startswith("VMOS")):
        logger.info(f"{device_id}点击发视频...")
        click_bound(device, (465,1822,615,1920)) #[465,1822][615,1920]
        logger.info(f"{device_id}选择相册...")
        click_bound(device, (804,1650,916,1762)) #[804,1650][916,1762]
        logger.info(f"{device_id}点击视频TAB...")
        device(text="Videos").click()
        random_sleep()
        logger.info(f"{device_id}选择第一个视频...")
        click_bound(device, (4,238,359,596)) #[4,238][359,596]
        logger.info(f"{device_id}点击下一步...")
        device(text="Next").click()
        random_sleep()
        logger.info(f"{device_id}输入视频描述...")
        input_element = device(textContains="Add description")
        input_element.set_text(video_desc)
        random_sleep()
        logger.info(f"{device_id}点击发布...")
        device(text="Post").click()
        random_sleep()
    else:
        logger.info(f"{device_id}点击发视频...")
        click_bound(device, (432,1794,648,1920))
        if(device_id=='MYT001'):
            logger.info(f"{device_id}点击相册...")
            click_bound(device, (48,1767,156,1875)) 
        else:
            logger.info(f"{device_id}选择相册...")
            click_bound(device, (807,1521,963,1677))
        logger.info(f"{device_id}点击视频TAB...")
        device(text="Videos").click()
        random_sleep()
        logger.info(f"{device_id}选择第一个视频...")
        click_bound(device, (6,357,358,713)) 
        logger.info(f"{device_id}点击下一步...")
        device(text="Next").click()
        random_sleep()
        logger.info(f"{device_id}输入视频描述...")
        input_element = device(textContains="Add description")
        input_element.set_text(video_desc)
        random_sleep()
        logger.info(f"{device_id}点击发布...")
        device(text="Post").click()
        random_sleep()
    screenshot(device, "POST_END", **kwargs)


def upload_video(device, video_path):
    # 获取当前日期，格式为YYYYMMDDHHMMSS
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # 获取原文件名
    ext_part = video_path.split('.')[-1]
    video_name = f"{current_date}.{ext_part}"
    tmp_path = f"/data/local/tmp/{video_name}"      
    final_path = f"/sdcard/Download/{video_name}"
    # 第一步：推送到临时目录
    logger.info(f"正在通过中转推送: {video_path}=>{tmp_path}")
    device.push(video_path, tmp_path)
    # 第二步：通过 shell 移动并清理（mv 命令在 shell 里通常权限更高）
    logger.info(f"正在通过shell移动: {tmp_path}=>{final_path}")
    device.shell(f"mv {tmp_path} {final_path}")
    # 第三步：关键！通知系统扫描新视频，否则 TikTok 选视频时看不到它
    device.shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}")
    logger.info(f"视频已成功就绪: {final_path}")
    random_sleep(10,11)
    return final_path
##################################################################

def press_home(device):
    device.press("home")

def screenshot(device, error_detail, **kwargs):
    device_id = kwargs.get('device_id')
    screenshot_path = rf"E:/ScreenShot/{error_detail}_{device_id}_{time.strftime('%Y%m%d_%H%M%S', time.localtime())}.png"
    device.screenshot(screenshot_path)
    random_sleep()
    send_log(screenshot_path, error_detail, **kwargs)
    return screenshot_path

def open_tiktok(device):
    device.shell("am start -S -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.main.MainActivity")
    random_sleep(8,10)

def random_sleep(min_sleep=3, max_sleep=5):
    sleep_time = random.randint(min_sleep, max_sleep)
    time.sleep(sleep_time)

def click_bound(device, bounds):
    x1, y1, x2, y2 = bounds
    # 模拟真人的“中心偏向”随机（正态分布）
    # 相比均匀分布，这更像人类点击习惯：更倾向于点中心，偶尔点到边缘
    mean_x = (x1 + x2) / 2
    mean_y = (y1 + y2) / 2
    std_x = (x2 - x1) / 6
    std_y = (y2 - y1) / 6
    target_x = int(random.gauss(mean_x, std_x))
    target_y = int(random.gauss(mean_y, std_y))
    # 确保坐标最终没超出边界
    target_x = max(x1, min(target_x, x2))
    target_y = max(y1, min(target_y, y2))
    device.click(target_x, target_y)
    random_sleep()

def send_log(screenshot, error_desc, **kwargs):
    """
    调用外部接口发送日志数据
    """
    try:
        # 从kwargs中获取参数
        device_id = kwargs.get('device_id')
        task_id = kwargs.get('task_id')
        task_type = kwargs.get('task_type')
        # 构建请求数据
        payload = {
            "deviceId": device_id,
            "rpaTaskId": task_id,
            "taskType": task_type,
            "errorDesc": error_desc,
            "screenshot": screenshot
        }
        
        # 发送POST请求
        url = 'http://localhost/rpa/log/add'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        
        # 检查响应状态
        if response.status_code == 200:
            logger.info(f"日志发送成功，设备ID: {device_id}, 任务ID: {task_id}")
            return True
        else:
            logger.error(f"日志发送失败，状态码: {response.status_code}, 响应内容: {response.text}")
            return False
    except Exception as e:
        logger.error(f"发送日志时发生错误: {str(e)}")
        return False