from typing import Any, Iterator, Optional, Union
from langchain.agents import AgentExecutor
from langchain.agents.agent import ExceptionTool
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.exceptions import OutputParserException
from langchain_core.tools import BaseTool
from pydantic import Field
from ..llm_use_function.Function import is_important,summarize_all,summarize_rag,summarize_step
from langchain_core.agents import AgentAction, AgentStep, AgentFinish
from ..model.LLM import llm
from ..middleware.Tools import add_rag
from ..chain.ChainFunction import ask_change_plan
from ..server.Websocket import *
from ..server.AsyncLoop import global_loop

# 改写AgentExecutor类
from ..server.Websocket import MyWebsocket,WS_URL
ws = MyWebsocket(WS_URL,1,1)
class CustomExecutor(AgentExecutor):
    max_rag_index:int =  Field(-1, description="RAG数量的最大值")
    max_index: int = Field(-1, description="工具数量的最大值")
    step: int = Field(-1, description="步骤")
    last_intermediate_steps: int = Field(-1, description="上一个intermediate_steps的长度")
    k: int = Field(-1,description="控制历史对话")

    def __init__(self, max_index:int,max_rag_index:int,k:int, **kwargs):
        super().__init__(**kwargs)
        self.max_rag_index:int = max_rag_index
        self.max_index:int = max_index
        self.last_intermediate_steps = 0
        self.k: int = k


    def _iter_next_step(
        self,
        name_to_tool_map: dict[str, BaseTool],
        color_mapping: dict[str, str],
        inputs: dict[str, Any],
        intermediate_steps: list[tuple[AgentAction, str]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    )-> Iterator[Union[AgentFinish, AgentAction, AgentStep]]:

        # 处理intermediate_steps
        if len(intermediate_steps) > self.max_index+1:
            # 截取超过部分
            removed = intermediate_steps.pop(1)
            _, now = removed
            action,history = intermediate_steps[0]
            history = summarize_all(llm, history, now,self.step - self.max_index)
            intermediate_steps[0] = (action,history)

        if len(intermediate_steps) != 0:
            # 处理RAG
            if self.last_intermediate_steps != len(intermediate_steps):
                action, obs = intermediate_steps[len(intermediate_steps) - 1]
                if action.tool == "use_rag":
                    inputs["rag_context"].append(obs)
                    if len(inputs["rag_context"]) > self.max_rag_index+1:
                        e = inputs["rag_context"].pop(1)
                        inputs["rag_context"][0] = summarize_rag(llm,inputs["rag_context"][0] , e)
                if is_important(obs, llm):
                    add_rag(obs)
            action,obs = intermediate_steps[len(intermediate_steps) - 1]
            summary = f"当前是第{self.step}步: {obs}"
            # action.log = f"调用工具{action.tool}"
            intermediate_steps[len(intermediate_steps) - 1] = (action, summary)
            if action.tool:
                print(obs)
            self.step+=1

            if len(intermediate_steps) > 1:
                action, obs = intermediate_steps[len(intermediate_steps) - 1]
                print("-"*60+"action","-"*60)
                print(action)
                print("-" * 60 + "obs", "-" * 60)
                print("obs:", obs)
                # inc = input()

        else:
            fake_action = AgentAction(
                tool = "_summary_",
                tool_input = {},
                log = "中间步骤总结（非工具调用）"
            )
            intermediate_steps.append((fake_action, "历史记录"))
            self.step = 1

        self.last_intermediate_steps = len(intermediate_steps)

        try:
            intermediate_steps = self._prepare_intermediate_steps(intermediate_steps)

            # Call the LLM to see what to do.
            output = self._action_agent.plan(
                intermediate_steps,
                callbacks=run_manager.get_child() if run_manager else None,
                **inputs,
            )
        except OutputParserException as e:
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                msg = (
                    "An output parsing error occurred. "
                    "In order to pass this error back to the agent and have it try "
                    "again, pass `handle_parsing_errors=True` to the AgentExecutor. "
                    f"This is the error: {e!s}"
                )
                raise ValueError(msg) from e
            text = str(e)
            if isinstance(self.handle_parsing_errors, bool):
                if e.send_to_llm:
                    observation = str(e.observation)
                    text = str(e.llm_output)
                else:
                    observation = "Invalid or incomplete response"
            elif isinstance(self.handle_parsing_errors, str):
                observation = self.handle_parsing_errors
            elif callable(self.handle_parsing_errors):
                observation = self.handle_parsing_errors(e)
            else:
                msg = "Got unexpected type of `handle_parsing_errors`"
                raise ValueError(msg) from e  # noqa: TRY004
            output = AgentAction("_Exception", observation, text)
            if run_manager:
                run_manager.on_agent_action(output, color="green")
            tool_run_kwargs = self._action_agent.tool_run_logging_kwargs()
            observation = ExceptionTool().run(
                output.tool_input,
                verbose=self.verbose,
                color=None,
                callbacks=run_manager.get_child() if run_manager else None,
                **tool_run_kwargs,
            )
            yield AgentStep(action=output, observation=observation)
            return

        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            yield output
            return
        if len(output) == 1:
            tool_log = output[0].log
            summary_obs = f"{summarize_step(llm, tool_log)}"
            print(summary_obs)

            ans = ask_change_plan()
            if ans == "STOP":
                yield AgentFinish(
                    return_values={
                        "output": "暂停运行"
                    },
                    log="用户停止运行"
                )
                return
            elif ans == "CHANGE":
                output = AgentAction(
                    tool="",
                    tool_input={},
                    log="用户需要重新规划下一步"
                )
                observation = input("请您提出需求：")
                intermediate_steps.append((AgentAction(
                    tool="",
                    tool_input={},
                    log=f"当前是第{self.step}步:用户需要重新规划下一步，你的下一步需要{observation}这样做"
                ),
                                           observation))
                self.last_intermediate_steps = len(intermediate_steps)
                self.step += 1
                # print(self.last_intermediate_steps)
                yield AgentAction(
                    tool="",
                    tool_input={},
                    log=f"无"
                )
                return



        else:
            raise "多工具使用目前暂不支持"

        actions: list[AgentAction]
        actions = [output] if isinstance(output, AgentAction) else output
        for agent_action in actions:
            yield agent_action
        for agent_action in actions:
            yield self._perform_agent_action(
                name_to_tool_map,
                color_mapping,
                agent_action,
                run_manager,
            )