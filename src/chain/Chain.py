from langchain_core.runnables import RunnableLambda
from ..model.Agent import agent_executor
from ..chain.ChainFunction import flf,protect



first_llm_fun = RunnableLambda(flf)

protect_ans = RunnableLambda(protect)
# 链
chain = first_llm_fun | agent_executor | protect_ans