from langchain_core.runnables import Runnable

from ..interfaces.StateABC import IStateMachine
from typing import TypedDict, List, Tuple, Optional, Union
from pydantic import BaseModel
from langchain_core.agents import AgentAction, AgentStep, AgentFinish
from ..interfaces.WorkFlowABC import IWorkFlow
from ..interfaces.StateABC import IState

class ReactAgent(IState):
    input_config:dict
    intermediate_steps: List[Tuple[AgentAction, str]]
    plan: Optional[Union[AgentFinish,List[AgentAction]]]
    step: int = 1
    # 运行的最大步骤
    max_step: int = 10
    output: Optional[str]
    is_log:bool
    # RAG数量的最大值
    max_rag_index:int
    # 控制工具调用数量的最大值
    max_index: int
    # 重试的最大次数
    max_retries:int




class MyReactAgent(IStateMachine):
    """ 用于创建一个ReactAgent """
    def __init__(self,
        max_rag_index,
        max_step,
        max_index,
        max_retries = 1,
        is_log:bool=False,
        **kwargs
    ):
        self.max_step = max_step
        self.is_log = is_log
        self.max_rag_index = max_rag_index
        self.kwargs = kwargs
        self.max_index = max_step
        self.max_rag_index = max_rag_index
        self.max_index = max_index
        # self.workflow:IWorkFlow = workflow
        self.max_retries = max_retries

    def create_state(self,config:dict)->IState:
        return ReactAgent(
            intermediate_steps=[],
            plan=None,
            step=1,
            max_step=self.max_step,
            is_log=self.is_log,
            max_rag_index=self.max_rag_index,
            max_index=self.max_index,
            max_retries=self.max_retries,
            input_config=config,
            output=None,
        )

    def __call__(self,config:dict)->IState:
        """
        工作流运行
        """
        return self.create_state(config)



