import json
import threading
import queue
import time
import os
import tempfile
from typing import Any, Optional, Dict

import matplotlib as mpl
import requests
IMAGE_NAME = "agent:tool"
CONTAINER_NAME = "tool"
URL = "http://192.168.142.128:8888"
HOST_DATA_DIR = "/root/py39-agent-env/docker_use/data"    # 第一个文件夹
HOST_RESULT_DIR = "/root/py39-agent-env/docker_use/result"  # 第二个文件夹

CONTAINER_DATA_DIR = "/app/data"      # data
CONTAINER_RESULT_DIR = "/app/result"  # result

# 环境池核心类
class EnvPool:
    def __init__(self, max_envs=3, create_env_func=None, destroy_env_func=None):
        """
        环境池初始化
        :param max_envs: 池最大环境数（默认3个）
        :param create_env_func: 创建单个环境的函数
        :param destroy_env_func: 销毁单个环境的函数
        """
        self.max_envs = max_envs
        self.create_env = create_env_func
        self.destroy_env = destroy_env_func
        self.pool = queue.Queue(maxsize=max_envs)  # 环境队列
        self.lock = threading.Lock()  # 线程安全锁
        self.env_count = 0  # 当前已创建的环境数

    def get_env(self, timeout=60):
        """申请一个环境"""
        start_time = time.time()  # 记录开始等待的时间
        while True:
            # 检查是否已经超时
            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                raise TimeoutError(f"等待{timeout}秒后仍无可用环境，环境池已满")

            try:
                # 非阻塞尝试获取环境
                return self.pool.get(block=False)
            except queue.Empty:
                # 队列空 检查是否能创建新环境
                with self.lock:
                    if self.env_count < self.max_envs:
                        env = self.create_env(self.env_count)
                        self.env_count += 1
                        return env

                # 既没拿到环境，也不能创建新环境 短暂休眠后重试
                time.sleep(0.1)

    def return_env(self, env):
        """归还环境到池"""
        try:
            self.pool.put(env, block=False)
        except queue.Full:
            # 池满时直接销毁环境
            self.destroy_env(env)
            with self.lock:
                self.env_count -= 1

    def close(self):
        """销毁池内所有环境"""
        while not self.pool.empty():
            env = self.pool.get()
            if self.destroy_env(env) is False:
                raise "环境销毁失败"
        self.env_count = 0


# 定义环境的结构
class MyEnv:
    def __init__(self, env_name, img_name):
        self.env_name = env_name  # 环境名称
        self.img_name = img_name  # 环境镜像名称



# 创建单个环境的函数
def create_my_env(contain_id:int)->str:
    """创建自定义环境"""
    try:
        route = "/create-container"
        req = URL + route

        payload = {
            "image_name": IMAGE_NAME,
            "container_name": f"tool_{contain_id}",
            "mounts": [
                # 第一个挂载项：data目录（格式和文件完全一致）
                {
                    "type": "bind",
                    "source": HOST_DATA_DIR,
                    "target": CONTAINER_DATA_DIR,
                    "mode": "rw"
                },
                # 第二个挂载项：result目录
                {
                    "type": "bind",
                    "source": HOST_RESULT_DIR,
                    "target": CONTAINER_RESULT_DIR,
                    "mode": "rw"
                }
            ]
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(req, json=payload, headers=headers)
        time.sleep(5)
        return f"tool_{contain_id}"
    except Exception as e:
        raise f"错误{e}"


# 销毁单个环境的函数
def destroy_my_env(contain_name:str)->bool:
    """销毁自定义环境"""
    try:
        route = "/remove-container"
        req = URL + route
        payload = {
            "container_name": f"{contain_name}"
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(req, json=payload, headers=headers)

        return True
    except Exception as e:
        return False



# 核心业务逻辑：使用容器池执行任务
def use_my_env(env_pool: EnvPool, func_name: str, func_params):
    """
    从环境池获取容器，调用/call_func接口执行函数
    :param env_pool: 环境池实例
    :param func_name: 要调用的函数名
    :param func_params: 函数参数
    :return: 接口返回的执行结果
    """
    container_name = None
    try:
        container_name = env_pool.get_env()
        
        # 注意：如果后端接口需要关联容器名，需在params中添加container_name
        route = "/run-function"
        req = URL + route

        request_data = {
            "container_name":container_name,
            "func_name": func_name,          # 要调用的函数名
            "func_params": func_params # 函数参数（默认空字典）
        }


        # 3. 调用后端/call_func接口
        response = requests.post(
            url=req,          # 接口路径
            json=request_data,               # 传递函数名和参数
            headers={"Content-Type": "application/json"},
        )
        return response.json()["result"]

    except TimeoutError as e:
        return f"获取容器超时：{e}"

    except requests.exceptions.RequestException as e:
        return  f"接口调用失败：{e}"

    except Exception as e:
        return  f"执行失败：{e}"

    finally:
        # 归还容器到环境池
        if container_name:
            env_pool.return_env(container_name)

my_env = EnvPool(create_env_func=create_my_env, destroy_env_func=destroy_my_env)






