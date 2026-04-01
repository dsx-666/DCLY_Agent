import time
from typing import Any, Union, Type

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain_core.runnables import Runnable
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph


from ..interfaces.NodeABC import IToolNode
from ..interfaces.StateABC import IState
from ..interfaces.WorkFlowABC import IWorkFlow
from ..log.Log import logger
from typing import TypeVar,Generic

T = TypeVar('T', bound=IState)


# noinspection PyUnresolvedReferences
class AgentWorkFlowBuild(IWorkFlow, Generic[T]):
    def __init__(self,agent:Runnable,tool_use:IToolNode,state_class: Type[T]):
        self.agent = agent
        self.tool_use = tool_use
        self.graph:Union[StateGraph,CompiledStateGraph] = StateGraph(state_class)
    def create_node(self):
        def react_agent_node(state: T) -> T:
            retry_count = 0

            while retry_count < state.max_retries:
                try:
                    response = self.agent.invoke({
                        **state.input_config,
                        "intermediate_steps": state.intermediate_steps
                    })
                    state.plan = response
                    return state

                except OutputParserException as e:
                    # LLM 格式错误 - 立即重试
                    retry_count += 1
                    state.intermediate_steps.append((
                        AgentAction(tool="_retry_", tool_input={}, log="格式错误"),
                        f"输出格式错误，第{retry_count}次重试：{str(e)}"
                    ))
                    continue

                except (TimeoutError, ConnectionError) as e:
                    # 临时错误 - 延迟后重试
                    retry_count += 1
                    time.sleep(2 ** retry_count)  # 指数退避
                    continue

                except (ValueError, TypeError) as e:
                    # 参数错误 - 不重试，直接返回错误
                    state.plan = [AgentAction(
                        tool="_error_",
                        tool_input={},
                        log=f"参数错误，无法继续：{str(e)}"
                    )]
                    return state

                except Exception as e:
                    # 其他错误 - 记录并终止
                    if state.is_log:
                        logger.error(f"未预期的错误：{type(e).__name__} - {str(e)}")
                    raise RuntimeError(f"未预期的错误：{type(e).__name__} - {str(e)}") from e

            # 超过重试次数
            raise RuntimeError(f"超过最大重试次数 ({state.max_retries})")

        def tool_node(state: T) -> T:
            try:
                if state.is_log:
                    logger.info(f"执行工具：{state.plan}")
                ans = self.tool_use(state)
                for action, observation in ans:
                    # 将观察结果添加到 intermediate_steps
                    state.intermediate_steps.append((action, observation))
                    if state.is_log:
                        logger.info(f"工具 {action.tool} 执行完成,{observation}")
            except Exception as e:
                raise

            # 清空 plan，让 Agent 重新规划下一步
            state.plan = None
            state.step += 1
            return state

        self.graph.add_node("react_agent_node", react_agent_node)
        self.graph.add_node("tool_node", tool_node)

    def create_edge(self) -> Any:
        def conditional_condition(state: T) -> str:
            if isinstance(state.plan, list):
                return "tool_node"
            if isinstance(state.plan, AgentFinish):
                state.output = state.plan.log
                print(60 * "-")
                if state.is_log:
                    logger.info(state.output)
                state.plan = None
                return "__end__"
            return "__end__"

        self.graph.add_edge("tool_node", "react_agent_node")
        self.graph.add_conditional_edges("react_agent_node",
                                    conditional_condition,
                                    {
                                        "__end__": END,
                                        "tool_node": "tool_node",
                                    }
                                    )
        self.graph.add_edge(START, "react_agent_node")
    def create_graph(self) -> None:
        self.create_node()
        self.create_edge()
        self.graph = self.graph.compile()


    def run(self, inputs:T)->str:
        return self.graph.invoke(inputs)

    def __call__(self, inputs:T)->str:
        return self.graph.invoke(inputs)









