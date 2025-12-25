from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import time

# 导入任务管理器
from .task_manager import task_manager

# 获取logger实例
logger = logging.getLogger(__name__)

def hello(request):
    return HttpResponse("Hello, World!")

def perform_tiktok_scrolling(**kwargs):
    """
    执行TikTok滚动任务的实际函数
    这个函数将由任务管理器的设备线程调用
    """
    try:
        # 从kwargs中获取参数
        device_id = kwargs.get('device_id')
        pad_code = kwargs.get('pad_code')
        local_ip = kwargs.get('local_ip')
        local_port = kwargs.get('local_port')
        scrolling_time = kwargs.get('scrolling_time')
        logger.info(f"设备名称{device_id}")
        time.sleep(10)
        return {"status": "success", "message": "Scrolling completed"}
        
    except Exception as e:
        device_id = kwargs.get('device_id', 'unknown')
        logger.error(f"Error during TikTok scrolling for device {device_id}: {str(e)}")
        raise

@csrf_exempt
def tiktok_scrolling(request):
    if request.method == 'POST':
        try:
            # 解析JSON请求体
            data = json.loads(request.body)
            
            # 获取参数
            device_id = data.get('device_id')
            pad_code = data.get('pad_code')
            local_ip = data.get('local_ip')
            local_port = data.get('local_port')
            scrolling_time = data.get('scrolling_time')
            
            # 将任务添加到任务管理器
            task_id = task_manager.add_task(
                device_id=device_id,
                task_func=perform_tiktok_scrolling,
                pad_code=pad_code,
                local_ip=local_ip,
                local_port=local_port,
                scrolling_time=scrolling_time
            )
            
            # 获取队列大小
            queue_size = task_manager.get_device_queue_size(device_id)
            
            logger.info(f"Task {task_id} added to device {device_id} queue. Current queue size: {queue_size}")
            
            # 返回成功响应
            return JsonResponse({
                'status': 'success',
                'message': 'Task added to queue successfully',
                'task_id': task_id,
                'queue_size': queue_size,
                'device_id': device_id
            }, status=200)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON format received")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON format'
            }, status=400)
        except Exception as e:
            logger.error(f"Error processing tiktok scrolling request: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    else:
        logger.warning(f"Invalid request method received: {request.method}")
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed, please use POST'
        }, status=405)