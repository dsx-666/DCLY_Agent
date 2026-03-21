import threading
import asyncio

from fastapi import FastAPI, Request
global_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
asyncio.set_event_loop(global_loop)


def start_async_loop():
    """后台线程运行全局事件循环（专门处理WebSocket异步逻辑）"""
    global_loop.run_forever()


async def lifespan(app: FastAPI):
    # 启动逻辑（替代钩子函数）
    # 启动后台线程运行事件循环
    loop_thread = threading.Thread(target=start_async_loop, daemon=True)
    loop_thread.start()
    # 将全局循环挂载到 app.state，供其他文件调用（解耦）
    app.state.global_loop = global_loop

    # yield 分隔 以上是启动逻辑，以下是关闭逻辑
    yield

    # 关闭逻辑
    # 跨线程安全停止事件循环
    global_loop.call_soon_threadsafe(global_loop.stop)
