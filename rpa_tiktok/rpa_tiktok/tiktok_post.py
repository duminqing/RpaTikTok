import random
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
    #TODO try catch
    device = connect_device(device_id, pad_code, local_ip, local_port)
    upload_video(device, video_path)
    open_tiktok(device)
    post_video(device, device_id, video_desc)

def post_video(device, device_id, video_desc):
    if(device_id.startswith("VMOS")):
        logger.info(f"{device_id}点击发视频...")
        click_bound(device, (465,1822,615,1920)) #[465,1822][615,1920]
        time.sleep(3)
        logger.info(f"{device_id}选择相册...")
        click_bound(device, (804,1650,916,1762)) #[804,1650][916,1762]
        time.sleep(3)
        logger.info(f"{device_id}点击视频TAB...")
        device(text="Videos").click()
        time.sleep(3)
        logger.info(f"{device_id}选择第一个视频...")
        click_bound(device, (4,238,359,596)) #[4,238][359,596]
        time.sleep(3)
        logger.info(f"{device_id}点击下一步...")
        device(text="Next").click()
        time.sleep(3)
        logger.info(f"{device_id}输入视频描述...")
        input_element = device(textContains="Add description")
        input_element.set_text(video_desc)
        time.sleep(3)
        logger.info(f"{device_id}点击发布...")
        device(text="Post").click()
    else:
        logger.info(f"{device_id}点击发视频...")
        click_bound(device, (432,1794,648,1920))
        time.sleep(3)
        if(device_id=='MYT001'):
            logger.info(f"{device_id}点击相册...")
            click_bound(device, (48,1767,156,1875)) 
            time.sleep(3)
        else:
            logger.info(f"{device_id}选择相册...")
            click_bound(device, (807,1521,963,1677))
            time.sleep(3)
        logger.info(f"{device_id}点击视频TAB...")
        device(text="Videos").click()
        time.sleep(3)
        logger.info(f"{device_id}选择第一个视频...")
        click_bound(device, (6,357,358,713)) 
        time.sleep(3)
        logger.info(f"{device_id}点击下一步...")
        device(text="Next").click()
        time.sleep(3)
        logger.info(f"{device_id}输入视频描述...")
        input_element = device(textContains="Add description")
        input_element.set_text(video_desc)
        time.sleep(3)
        logger.info(f"{device_id}点击发布...")
        device(text="Post").click()

def open_tiktok(device):
    device.shell("am start -S -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.main.MainActivity")
    time.sleep(10)

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
    time.sleep(random.randint(3,5))

def upload_video(device, video_path):
    local_path = video_path
    tmp_path = f"/data/local/tmp/{video_path.split('/')[-1]}"      
    final_path = f"/sdcard/Download/{video_path.split('/')[-1]}"
    # 第一步：推送到临时目录
    logger.info(f"正在通过中转推送: {local_path}=>{tmp_path}")
    device.push(local_path, tmp_path)
    # 第二步：通过 shell 移动并清理（mv 命令在 shell 里通常权限更高）
    logger.info(f"正在通过shell移动: {tmp_path}=>{final_path}")
    device.shell(f"mv {tmp_path} {final_path}")
    # 第三步：关键！通知系统扫描新视频，否则 TikTok 选视频时看不到它
    device.shell(f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://{final_path}")
    logger.info(f"视频已成功就绪: {final_path}")
    time.sleep(10)
    return final_path