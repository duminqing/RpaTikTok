from . connect_device import connect_device
import json
import logging
import time
logger = logging.getLogger(__name__)


def perform_tiktok_scrolling(**kwargs):
    """
    执行TikTok滚动任务的实际函数
    这个函数将由任务管理器的设备线程调用
    """
    # 从kwargs中获取参数
    device_id = kwargs.get('device_id')
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    scrolling_time = kwargs.get('scrolling_time')
    # 连接设备
    logger.info(f"连接设备{device_id}")
    #TODO try catch
    device = connect_device(device_id, pad_code, local_ip, local_port)
    open_tiktok(device)
    end_time = time.time() + scrolling_time*60
    while time.time()<end_time:
        try:
            device.swipe_ext("up")
            app_current = device.app_current()['package']
            if app_current != 'com.zhiliaoapp.musically' and app_current != 'om.ss.android.ugc.trill':
                logger.info(f"{device_id}当前应用包名：{app_current} 当前应用不是TikTok，可能已经退出")
                #截图并保存当前界面
                #screenshot(device,device_id,"EXIT")
                open_tiktok(device)
                continue
        except Exception as e:
            device_id = kwargs.get('device_id', 'unknown')
            logger.error(f"Error during TikTok scrolling for device {device_id}: {str(e)}")
            raise

        time.sleep(10)
        return {"status": "success", "message": "Scrolling completed"}
        
        
def open_tiktok(device):
    device.shell("am start -S -n com.zhiliaoapp.musically/com.ss.android.ugc.aweme.main.MainActivity")
    time.sleep(10)