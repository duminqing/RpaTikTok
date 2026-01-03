from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .tiktok_scrolling import perform_tiktok_scrolling
from .tiktok_post import perform_tiktok_post
from .tiktok_video_data import perform_tiktok_videa_data
# 导入任务管理器
from .task_manager import task_manager

# 获取logger实例
logger = logging.getLogger(__name__)

def hello(request):
    return HttpResponse("Hello, World!")
@csrf_exempt
def tiktok_videa_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            device_id = data.get('device_id')
            pad_code = data.get('pad_code')
            local_ip = data.get('local_ip')
            local_port = data.get('local_port')
            task_id = task_manager.add_task(
                task_func=perform_tiktok_videa_data,
                device_id=device_id,
                pad_code=pad_code,
                local_ip=local_ip,
                local_port=local_port,
                task_type='tiktok_videa_data'
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
            logger.error(f"Error processing tiktok video data request: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

@csrf_exempt
def tiktok_post(request):
    if request.method == 'POST':
        try:
            # 解析JSON请求体
            data = json.loads(request.body)
            
            # 获取参数
            device_id = data.get('device_id')
            pad_code = data.get('pad_code')
            local_ip = data.get('local_ip')
            local_port = data.get('local_port')
            video_path = data.get('video_path')
            video_desc = data.get('video_desc')
            
            # 将任务添加到任务管理器
            task_id = task_manager.add_task(
                task_func=perform_tiktok_post,
                device_id=device_id,
                pad_code=pad_code,
                local_ip=local_ip,
                local_port=local_port,
                video_path=video_path,
                video_desc=video_desc,
                task_type='tiktok_post'
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
                task_func=perform_tiktok_scrolling,
                device_id=device_id,
                pad_code=pad_code,
                local_ip=local_ip,
                local_port=local_port,
                scrolling_time=scrolling_time,
                task_type='tiktok_scrolling'
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