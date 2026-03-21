# 迭代器
from collections.abc import Iterator, Iterable
# langchain框架
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import BaseMessage, BaseMessageChunk,AIMessage,AIMessageChunk
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain.agents import  create_openai_tools_agent
# 类型注解
from typing import Optional, Union, Any, Coroutine, AsyncIterator, Iterator, AsyncGenerator,Sequence
from typing_extensions import override
# 隐私字符串
from pydantic import SecretStr
# 异步
import asyncio

class BaseLLM:
    """ 模型基类 """
    def __init__(self):
        """ 初始化模型基类 """
        pass

    def change_string(self):
        """ 改变返回的结果是否是流式 """
        pass

    def change_base_config(
        self,
        base_url:str,
        model_name:str,
        api_key: Optional[SecretStr]
    )->dict:
        """ 修改llm基本配置 """
        pass
    def get_model(self)->Union[BaseLanguageModel,Runnable]:
        """ 获取LLM实例 """
        pass
    def change_llm_config(self,
       llm:BaseLanguageModel
    )->dict:
        """ 修改agent配置 """

class LLM(BaseLLM):
    def __init__(
        self,
        base_url:str,
        api_key:Optional[SecretStr],
        model_name:str,
        temperature:int=0,
        max_tokens:Union[int,None]=None,
        streaming:bool=True,
        **kwargs:dict[str, Any]
    )->None:
        """
            大语言模型的基类，根据这个类来创建大语言模型
            :param base_url: 模型URL
            :param api_key: 模型API_KEY
            :param model_name: 模型名称
            :param temperature: 温度
            :param max_tokens: 控制最大token
            :param streaming: 是否是流式
            :param kwargs: 其他参数
            :return: None
        """
        super().__init__()
        self.llm:BaseLanguageModel = ChatOpenAI(
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming,
            model=model_name,
        )
        self.base_url:str = base_url
        self.api_key:Optional[SecretStr] = api_key
        self.model_name:str = model_name
        self.temperature:int = temperature
        self.max_tokens:Union[int,None] = max_tokens
        self.streaming:bool = streaming

        # 是否是流式
        self.streaming:bool = streaming
        # 其他参数
        self.kwargs:dict = kwargs

    @override
    def get_model(self)->BaseLanguageModel:
        return self.llm

    @override
    def change_base_config(
            self,
            base_url: str,
            model_name: str,
            api_key: Optional[SecretStr]
    ) -> dict:
        try:
            self.base_url: str = base_url
            self.model_name: str = model_name
            self.api_key: Optional[SecretStr] = api_key
            self.llm: ChatOpenAI = ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                streaming=self.streaming,
                model=self.model_name,
            )
            return {"bool":True,"message":"成功更改"}
        except Exception as e:
            return {"bool":False,"message":f"更改失败，原因{e}"}

class Agent(BaseLLM):
    """ 智能体类 """
    def __init__(
        self,
        llm:BaseLanguageModel,
        tools: Sequence[BaseTool],
        prompt:ChatPromptTemplate,
        **kwargs:dict[str, Any]
    )->None:
        """
            Agent的基类，根据这个类来创建Agent
            :param llm: 大语言模型
            :param tools: 模型使用到的工具
            :param prompt: Agent的提示词
            :param kwargs: 其他参数
            :return: None
        """
        super().__init__()
        self.tools:Sequence[BaseTool] = tools
        self.prompt:ChatPromptTemplate = prompt
        self.agent:Runnable = create_openai_tools_agent(
            llm = llm,
            tools = tools,
            prompt = prompt,
        )
        self.kwargs:dict = kwargs
    @override
    def change_llm_config(
        self,
        llm: BaseLanguageModel
    ) -> dict:
        try:
            self.agent:Runnable = create_openai_tools_agent(
                llm = llm,
                tools = self.tools,
                prompt = self.prompt,
            )
            return {"bool":True,"message":"成功更改"}

        except Exception as e:
            return {"bool":False,"message":f"更改失败，原因{e}"}

    @override
    def get_model(self) -> Runnable:
        return self.agent
