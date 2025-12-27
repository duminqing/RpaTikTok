import threading
import queue
import time
import logging
from typing import Dict, Callable, Any

logger = logging.getLogger(__name__)

class Task:
    """任务类，表示需要执行的任务"""
    def __init__(self, task_func: Callable, *args, **kwargs):
        self.task_id = kwargs.get('task_id')
        self.device_id = kwargs.get('device_id')
        self.task_func = task_func
        self.args = args
        self.kwargs = kwargs
        self.created_time = time.time()
        self.start_time = None
        self.end_time = None
        self.status = 'pending'  # pending, running, completed, failed
        self.result = None
        self.error = None

    def __str__(self):
        return f"Task({self.task_id}, device={self.device_id}, status={self.status})"

class DeviceThread(threading.Thread):
    """设备线程类，管理单个设备的任务执行"""
    def __init__(self, device_id: str, timeout: int = 300):  # 默认5分钟超时
        super().__init__(name=f"DeviceThread-{device_id}")
        self.device_id = device_id
        self.task_queue = queue.Queue()
        self.timeout = timeout
        self._stop_event = threading.Event()
        self._last_task_time = time.time()

    def run(self):
        """线程主循环"""
        logger.info(f"Device thread started for device {self.device_id}")
        
        while not self._stop_event.is_set():
            try:
                # 等待任务，设置超时
                task = self.task_queue.get(timeout=self.timeout)
                self._last_task_time = time.time()
                
                # 执行任务
                logger.info(f"Executing task {task.task_id} for device {self.device_id}")
                task.status = 'running'
                task.start_time = time.time()
                
                try:
                    # 执行任务函数，device_id已经在kwargs中
                    task.result = task.task_func(*task.args, **task.kwargs)
                    task.status = 'completed'
                    logger.info(f"Task {task.task_id} completed successfully for device {self.device_id}")
                except Exception as e:
                    task.status = 'failed'
                    task.error = str(e)
                    logger.error(f"Task {task.task_id} failed for device {self.device_id}: {str(e)}")
                finally:
                    task.end_time = time.time()
                    # 标记任务完成
                    self.task_queue.task_done()
                    
            except queue.Empty:
                # 超时，检查是否需要释放线程
                if time.time() - self._last_task_time > self.timeout:
                    logger.info(f"Device thread for {self.device_id} timed out after {self.timeout} seconds, releasing...")
                    self.stop()
            except Exception as e:
                logger.error(f"Error in device thread {self.device_id}: {str(e)}")
                
        logger.info(f"Device thread stopped for device {self.device_id}")

    def add_task(self, task: Task):
        """添加任务到队列"""
        if self._stop_event.is_set():
            raise RuntimeError(f"Device thread {self.device_id} is already stopped")
        self.task_queue.put(task)
        logger.info(f"Added task {task.task_id} to device {self.device_id} queue")

    def stop(self):
        """停止线程"""
        self._stop_event.set()
        # 唤醒可能在等待的线程
        try:
            self.task_queue.put(None, timeout=1)
        except queue.Full:
            pass

    def is_alive(self):
        """检查线程是否存活"""
        return super().is_alive() and not self._stop_event.is_set()

    def get_queue_size(self):
        """获取队列大小"""
        return self.task_queue.qsize()

class TaskManager:
    """任务管理器，管理所有设备线程和任务"""
    def __init__(self, thread_timeout: int = 300):
        self.thread_timeout = thread_timeout
        self.device_threads: Dict[str, DeviceThread] = {}
        self._lock = threading.RLock()
        self._task_counter = 0

    def _get_next_task_id(self):
        """生成唯一任务ID"""
        with self._lock:
            self._task_counter += 1
            return f"task_{int(time.time() * 1000)}_{self._task_counter}"

    def _get_or_create_thread(self, device_id: str):
        """获取或创建设备线程"""
        with self._lock:
            # 清理已停止的线程
            self._cleanup_stopped_threads()
            
            # 检查是否已有活跃线程
            if device_id in self.device_threads and self.device_threads[device_id].is_alive():
                return self.device_threads[device_id]
            
            # 创建新线程
            logger.info(f"Creating new thread for device {device_id}")
            thread = DeviceThread(device_id, timeout=self.thread_timeout)
            self.device_threads[device_id] = thread
            thread.start()
            return thread

    def _cleanup_stopped_threads(self):
        """清理已停止的线程"""
        with self._lock:
            stopped_devices = []
            for device_id, thread in self.device_threads.items():
                if not thread.is_alive():
                    stopped_devices.append(device_id)
            
            for device_id in stopped_devices:
                logger.info(f"Cleaning up stopped thread for device {device_id}")
                del self.device_threads[device_id]

    def add_task(self, task_func: Callable, *args, **kwargs) -> str:
        """添加任务到对应设备的队列"""
        # 从kwargs中获取device_id
        device_id = kwargs.get('device_id')
        if not device_id:
            raise ValueError("device_id cannot be empty")
        
        # 创建任务
        task_id = self._get_next_task_id()
        kwargs['task_id'] = task_id
        
        # 创建Task实例，使用修改后的构造函数参数顺序
        task = Task(task_func, *args, **kwargs)
        
        # 获取或创建设备线程并添加任务
        thread = self._get_or_create_thread(device_id)
        thread.add_task(task)
        
        return task_id

    def get_device_queue_size(self, device_id: str) -> int:
        """获取设备队列大小"""
        with self._lock:
            if device_id in self.device_threads and self.device_threads[device_id].is_alive():
                return self.device_threads[device_id].get_queue_size()
            return 0

    def get_thread_count(self) -> int:
        """获取活跃线程数量"""
        with self._lock:
            self._cleanup_stopped_threads()
            return len(self.device_threads)

    def stop_all_threads(self):
        """停止所有线程"""
        with self._lock:
            logger.info("Stopping all device threads...")
            for device_id, thread in self.device_threads.items():
                if thread.is_alive():
                    thread.stop()
            
            # 等待所有线程结束
            for device_id, thread in self.device_threads.items():
                if thread.is_alive():
                    thread.join(timeout=5)
            
            self.device_threads.clear()
            logger.info("All device threads stopped")

# 全局任务管理器实例
task_manager = TaskManager()





