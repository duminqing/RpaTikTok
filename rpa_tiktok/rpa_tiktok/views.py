from django.http import HttpResponse, JsonResponse
import json
import logging

# 获取logger实例
logger = logging.getLogger(__name__)

def hello(request):
    return HttpResponse("Hello, World!")

def tiktok_scrolling(request):
    if request.method == 'POST':
        try:
            # 解析JSON请求体
            data = json.loads(request.body)
            
            # 获取参数
            device_id = data.get('deviceId')
            pad_code = data.get('padCode')
            local_ip = data.get('localIp')
            local_port = data.get('localPort')
            scrolling_time = data.get('scrollingTime')
            # 记录参数（用于调试）
            logger.debug(f"Received parameters:")
            logger.debug(f"deviceId: {device_id}")
            logger.debug(f"padCode: {pad_code}")
            logger.debug(f"localIp: {local_ip}")
            logger.debug(f"localPort: {local_port}")
            logger.debug(f"scrollingTime: {scrolling_time}")

            # 返回成功响应
            return JsonResponse({
                'status': 'success',
                'message': 'Parameters received successfully',
                'received_data': data
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