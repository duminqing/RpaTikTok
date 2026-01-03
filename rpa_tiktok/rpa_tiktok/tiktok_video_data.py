
from . connect_device import connect_device
import logging
from . tiktok_common import click_bound,open_tiktok,click_element, random_sleep

logger = logging.getLogger(__name__)

def perform_tiktok_videa_data(**kwargs):
    device_id = kwargs.get('device_id')
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    task_id = kwargs.get('task_id')
    # 连接设备
    logger.info(f"{device_id}连接设备")
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
    except Exception as e:
        logger.error(f"{device_id}连接设备失败: {str(e)}")
        return {"status": "error", "message": f"连接设备失败: {str(e)}"}
    
    # 创建字典保存视频数据
    video_data_dict = {}
    swipe_len = 0
    # open_tiktok(device)
    # click_bound(device, (864, 1794,1080,1920))
    frame_layouts = device.xpath('//android.widget.GridView/android.widget.FrameLayout').all()
    is_swipe = True
    
    while is_swipe:
        # 遍历并解析每个 FrameLayout
        for index in range(len(frame_layouts) - 1, -1, -1):
            fl = frame_layouts[index]
            print(f"\n===== 第 {index + 1} 个 FrameLayout =====")
            # 获取 FrameLayout 的基本信息
            # 点击元素
            click_element(device, fl)
            # 计算滑动距离
            swipe_len = swipe_len(fl)
        
            #获取链接
            click_bound(device, (954,1367,1050,1463))
            device(description="Copy link").click()
            post_url= device.clipboard
            #如果存在了说明已经全都都已经获取过了
            if post_url in video_data_dict:
                logger.info(f"第 {index + 1} 个 FrameLayout 链接已存在，跳过")
                device.press("back")
                random_sleep(1, 3)
                break
            #没有浏览数据则跳过
            if device(text="0 views").exists():
                logger.info(f"第 {index + 1} 个 FrameLayout 没有views，跳过")
                video_data_dict[post_url] = {
                    "Views": "0",
                    "Likes": "0",
                    "Comments": "0"
                }
                device.press("back")
                random_sleep(1, 3)
                continue

            # 获取text包含"views"的元素
            # 判断元素是否可点击
            click_element(device, device.xpath('//*[contains(@text, "views")]').get())
            logger.info(f"点击views元素")
            
            Views_text = ""
            Likes_text = ""
            Comments_text = ""
            
            if device(textContains="Views").exists():
                Views = device.xpath('//*[contains(@text, "Views")]').get()
                Views_text = Views.text
                logger.info(f"Views元素: {Views_text}")
            if device(textContains="Likes").exists():
                Likes = device.xpath('//*[contains(@text, "Likes")]').get()
                Likes_text = Likes.text
                logger.info(f"Likes元素: {Likes_text}")
            if device(textContains="Comments").exists():
                Comments = device.xpath('//*[contains(@text, "Comments")]').get()
                Comments_text = Comments.text
                logger.info(f"Comments元素: {Comments_text}")
            
            # 保存数据到字典
            video_data_dict[post_url] = {
                "Views": Views_text,
                "Likes": Likes_text,
                "Comments": Comments_text
            }
            
            logger.info(f"链接: {post_url},{Views_text},{Likes_text},{Comments_text}")
            device.press("back")
            random_sleep(1, 3)
            device.press("back")
            random_sleep(1, 3)
        # 滑动到下一个
        device.swipe(0.5, 0.8, 0.5, 0.2, duration=0.5)
        random_sleep(1, 3)
        # 重新获取 FrameLayout 列表
        frame_layouts = device.xpath('//android.widget.GridView/android.widget.FrameLayout').all()
        # 如果没有新的 FrameLayout 出现，说明到底了
        if len(frame_layouts) == len(video_data_dict):
            is_swipe = False
    
    # 返回保存的数据字典
    return video_data_dict

def swipe_len(element):
    bounds = element.info.get('bounds')
    if bounds:
        y1 = bounds.get('top')
        y2 =  bounds.get('bottom')
    return y2-y1

        





