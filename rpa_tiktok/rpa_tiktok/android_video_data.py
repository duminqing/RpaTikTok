
from . android_connect_device import connect_device
import logging
from . android_common import click_bound,open_tiktok,click_element, random_sleep
import requests
from urllib.parse import urlparse, urlunparse
logger = logging.getLogger(__name__)

def perform_tiktok_video_data(**kwargs):
    device_id = kwargs.get('device_id')
    pad_code = kwargs.get('pad_code')
    local_ip = kwargs.get('local_ip')
    local_port = kwargs.get('local_port')
    task_id = kwargs.get('task_id')
    # 连接设备
    logger.info(f"{task_id} 连接设备{device_id}")
    try:
        device = connect_device(device_id, pad_code, local_ip, local_port)
    except Exception as e:
        logger.error(f"{task_id} 连接设备失败{device_id}: {str(e)}")
        return {"status": "error", "message": f"连接设备失败: {str(e)}"}
    
    # 创建字典保存视频数据
    video_data_dict = {}
    # open_tiktok(device)
    # click_bound(device, (864, 1794,1080,1920))
    frame_layouts = device.xpath('//android.widget.GridView/android.widget.FrameLayout').all()
    if len(frame_layouts) == 0:
        logger.error(f"{task_id} 没有视频")
        return {"status": "error", "message": f"没有视频"}
    swipe_len =2* len_y(frame_layouts[0])
    device.swipe(540,1344 , 540, 1344-swipe_len, duration=0.5)

    random_sleep(1, 3)
    frame_layouts = device.xpath('//android.widget.GridView/android.widget.FrameLayout').all()
    for index in range(0, min(len(frame_layouts), 9)):
            logger.info(f"{task_id} 点击第{index}个视频")
            fl = frame_layouts[index]
            click_element(device, fl)
            #获取链接
            logger.info(f"{task_id} 点击更多") #
            share_elem = device.xpath('//*[contains(@content-desc, "Share video")]').get()
            click_element(device, share_elem)
            device(description="Copy link").click()
            post_url= device.clipboard
            #post_url = get_pure_long_url(short_url)
            logger.info(f"{task_id} 本视频URL是==>  {post_url}")
            #如果存在了说明已经全都都已经获取过了
            # if post_url in video_data_dict:
            #     logger.info(f"{task_id} 链接{post_url}已存在，结束内部循环")
            #     device.press("back")
            #     random_sleep(1, 3)
            #     break
            # if index == len(frame_layouts) - 1:
            #     logger.info(f"{task_id} 滑动后检查第一个")
            #     if post_url == last_url:
            #         logger.info(f"{task_id} 第一个视频与上次相同，结束滑动continue_swipe=false")
            #         continue_swipe = False
            #         break
            #     logger.info(f"{task_id} 第一个视频与上次不同，记录{post_url}")
            #     last_url = post_url
            #没有浏览数据则跳过
            if device(text="0 views").exists():
                logger.info(f"{task_id} 没有views，跳过")
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
                Views_text = Views.text.replace("Views","").strip()
                logger.info(f"Views元素: {Views_text}")
            if device(textContains="Likes").exists():
                Likes = device.xpath('//*[contains(@text, "Likes")]').get()
                Likes_text = Likes.text.replace("Likes","").strip()
                logger.info(f"Likes元素: {Likes_text}")
            if device(textContains="Comments").exists():
                Comments = device.xpath('//*[contains(@text, "Comments")]').get()
                Comments_text = Comments.text.replace("Comments","").strip()
                logger.info(f"Comments元素: {Comments_text}")
            
            # 保存数据到字典
            logger.info(f"链接: {post_url},{Views_text},{Likes_text},{Comments_text}")
            video_data_dict[post_url] = {
                "Views": Views_text,
                "Likes": Likes_text,
                "Comments": Comments_text
            }
            
            device.press("back")
            random_sleep(1, 3)
            device.press("back")
            random_sleep(1, 3)
    # 返回保存的数据字典
    return video_data_dict

def len_y(element):
    bounds = element.info.get('bounds')
    if bounds:
        y1 = bounds.get('top')
        y2 =  bounds.get('bottom')
    return y2-y1

def get_pure_long_url(short_url, timeout=10):
    """
    从短路径获取去除动态参数的纯净长路径
    """
    try:
        # 获取跳转后的长路径
        response = requests.get(short_url, allow_redirects=True, timeout=timeout)
        long_url = response.url

        # 解析URL，去除query参数（?后面的动态参数）
        parsed_url = urlparse(long_url)
        # 重新构建URL，query部分置空
        pure_parsed_url = (parsed_url.scheme, parsed_url.netloc, parsed_url.path,
                           parsed_url.params, '', parsed_url.fragment)
        pure_long_url = urlunparse(pure_parsed_url)
        return pure_long_url
    except Exception as e:
        print(f"获取纯净长路径失败：{str(e)}")
        return None        







