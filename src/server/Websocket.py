import asyncio
import websockets
from typing import Optional, Union,Any
from fastapi import FastAPI

WS_URL = "ws://111778qb4bq84.vicp.fun"
class MyWebsocket:
    def __init__(self, ws_url: str, userid: int,chatid:int) -> None:
        """
        初始化WebSocket客户端
        :param ws_url: 后端WS接口地址
        :param userid: 用户唯一标识，用于区分不同用户的WS连接
        :param chatid: 对话的唯一标识
        :return: None
        """
        self.ws_url: str = ws_url  # 后端WS地址
        self.userID: int = userid  # 用户ID
        self.chatID: int = chatid  # 对话id
        self.websocket: Optional[Any] = None  # WS连接对象

    # 建立WS连接
    async def connect(self) -> None:
        """
        建立与后端的WebSocket连接
        :return: None
        """
        self.websocket = await websockets.connect(f"{self.ws_url}/ws/model/{self.userID}/{self.chatID}")

    # 模型端发消息给后端（替代原print）
    async def send_message(self, message: str) -> None:
        """
        模型端向后端发送消息
        :param message: 要发送的文本消息
        :return: None
        """
        if self.websocket:
            await self.websocket.send(message)

    async def wait_response(self, timeout: int = 600) -> Union[str, Any,None]:
        """
        模型端等待后端推送的用户回复
        :param timeout: 超时时间，默认600秒
        :return: 成功返回用户回复字符串 | 超时返回"TIMEOUT" | 异常无返回（抛出）
        """
        if self.websocket:
            try:
                # 阻塞等待后端消息，超时600秒
                response: Any = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
                return response
            except asyncio.TimeoutError:
                return "TIMEOUT"
        # 规范抛出异常
        raise RuntimeError("websocket未开启")

    # 关闭连接
    async def close(self) -> None:
        """
        关闭WebSocket连接
        :return: None
        """
        if self.websocket:
            await self.websocket.close()
            self.websocket = None  # 关闭后清空连接对象

