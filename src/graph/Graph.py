from ..graph.WorkFlow import AgentWorkFlowBuild
from ..graph.React import MyReactAgent,ReactAgent
from ..middleware.Tools import tools
from ..chain.Chain import chain
from ..graph.ToolNode import MyToolUse



tool_use = MyToolUse(tools)


Agent = MyReactAgent(max_rag_index=5,max_step=10,max_index=5,max_retries=1,is_log=True)
work = AgentWorkFlowBuild(chain,tool_use,ReactAgent)
work.create_graph()
if __name__ == "__main__":
    work(Agent(
        {
            "input":"请帮我分析这里面有一些什么数据",
            "userid":2,
            "chatid":3,
            "history": "",
            "summary": ""
        }
    ))





