from typing import List, Tuple, Any
from langchain_core.agents import AgentAction
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from ..log.Log import logger
from ..interfaces.NodeABC import IToolNode
from ..interfaces.StateABC import IState
class MyToolUse(IToolNode):
    """ 用于创建一个 ToolNode（用于简单的调用工具） """
    def __init__(self, tools_use:List[BaseTool]):
        # 构建函数字典
        self.tool = {tool.name:tool for tool in tools_use}
    def run(self,state:IState) ->List[Tuple[AgentAction, str]]:
        ans = []

        for action in state.plan:
            try:
                # 获取工具实例
                tool = self.tool.get(action.tool)
                if tool is None:
                    raise ValueError(f"未找到名为 '{action.tool}' 的工具")

                # 执行工具调用
                if isinstance(action.tool_input, dict):
                    result = tool.invoke(action.tool_input)
                else:
                    result = tool.invoke(str(action.tool_input))

                ans.append((
                    action,
                    f"当前是第{state.step}步，调用工具 {action.tool} 成功，结果：{result}"
                ))

            except Exception as e:
                error_msg = str(e)
                # 判断错误类型以决定策略
                # 1. 适合回退的错误 (Retriable Errors):
                #    - 网络超时、连接错误 (Timeout, ConnectionError)
                #    - 资源暂时不可用 (Resource temporarily unavailable)
                #    - 速率限制 (RateLimitError, 429 Too Many Requests)
                #    - 临时性的服务内部错误 (503 Service Unavailable)
                # 2. 适合直接退出/终止循环的错误 (Fatal Errors):
                #    - 工具不存在 (ValueError: Tool not found)
                #    - 参数验证失败 (ValidationError, TypeError)
                #    - 认证/权限错误 (AuthenticationError, PermissionError)
                #    - 逻辑错误导致的不可恢复状态

                is_retriable = any(keyword in error_msg.lower() for keyword in [
                    "timeout", "connection", "rate limit", "temporarily", "503", "network"
                ])
                                
                if is_retriable:
                    msg = f"当前是第{state.step}步，遇到可重试错误：{error_msg}，建议回退或重试"
                else:
                    msg = f"当前是第{state.step}步，遇到致命错误：{error_msg}，程序将停止执行该步骤"
                    # 对于致命错误，可以选择抛出异常中断整个流程，或者仅记录并返回错误信息供上游处理
                    # 这里选择抛出异常以明确终止当前执行流，符合"直接退出"的语义
                    raise RuntimeError(f"工具执行失败且不可重试：{error_msg}") from e
                
                ans.append((action, msg))
        return ans

    def __call__(self, state:IState) -> List[Tuple[AgentAction, str]]:
        # 尝试运行函数，如果说运行失败返回报错
        return self.run(state)