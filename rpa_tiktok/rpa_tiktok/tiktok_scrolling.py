from . connect_device import connect_device
import logging
import time
import random
from . tiktok_post import click_bound,open_tiktok,random_sleep,screenshot,press_home
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
    scrolling_time =(int) (kwargs.get('scrolling_time'))
    task_id=kwargs.get('task_id')   
    # 连接设备
    logger.info(f"{device_id}正在连接设备task_id:{task_id}")    
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
        open_tiktok(device)
        search(device)
    except Exception as e:
        logger.error(f"{device_id}连接设备失败: {str(e)}")
        return {"status": "error", "message": f"连接设备失败: {str(e)}"}
    
    end_time = time.time() + scrolling_time*60
    total=0
    while time.time()<end_time:
        try:
            logger.info(f"{device_id}刷第{total+1}次")
            total+=1
            device.swipe_ext("up")
            app_current = device.app_current()['package']
            if app_current != 'com.zhiliaoapp.musically' and app_current != 'om.ss.android.ugc.trill':
                logger.error(f"{device_id}当前应用包名：{app_current} 当前应用不是TikTok，可能已经退出，截图路径: {screenshot(device, "EXIT", **kwargs)}")
                open_tiktok(device)
                continue
            random_sleep()
            live_now_exists = device(text="LIVE now").exists()
            watch_live_exists = device(text="Tap to watch LIVE").exists()
            if live_now_exists or watch_live_exists:
                logger.debug(f"{device_id}发现LIVE视频，继续下一个视频")
                continue
            else:
                random_sleep(10,30)
                if(random.randint(0,100)<3):
                    click_like(device)
                    random_sleep()
                if(random.randint(0,100)<3):
                    click_favourites(device)
                    random_sleep()
        except Exception as e:
            logger.error(f"{device_id}刷视频异常，截图路径: {screenshot(device, "ERROR", **kwargs)}，错误信息: {str(e)}")
            open_tiktok(device)
            continue
    press_home(device)
    return {"status": "success", "message": "Scrolling completed"}

def search(device,**kwargs):
    try:
        click_bound(device, (912,75,1080,243))#[912,75][1080,243]
        #//android.widget.EditText
        # 方式2：简化写法（直接链式调用，若控件不存在会抛出异常，可按需使用）
        device.xpath('//android.widget.EditText').set_text("pads")
        random_sleep()
        # search按钮[836,84][1080,216]  //*[@text="Search"]
        click_bound(device, (836,84,1080,216))
        # Videos tab[466,228][615,348]  //*[@text="Videos"]
        device(text="Videos").click()
        # 第一个视频 [24,372][528,1178]
        logger.info(f"点击第一个视频")
        click_bound(device, (24,372,528,1178))
    except:
        logger.error(f"点击搜索失败,{screenshot(device, "SEARCH_ERROR", **kwargs)}")

def click_like(device,**kwargs):
    try:
        device(descriptionContains="Like").click()
    except:
        logger.error(f"点击点赞失败,{screenshot(device, "LIKE_ERROR", **kwargs)}")

def click_favourites(device,**kwargs):
    try:
        click_bound(device, (975,1370,1065,1460))
    except:
        logger.error(f"点击收藏失败,{screenshot(device, "FAVOURITES_ERROR", **kwargs)}")
