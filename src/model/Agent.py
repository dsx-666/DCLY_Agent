from ..classes.CustomExecutor import CustomExecutor
from ..classes.ModelClass import Agent
from ..middleware.Tools import tools
from ..prompt.Prompt import do_prompt
from ..model.LLM import llm
# 加载agent
agent_class = Agent(
    llm=llm,
    tools=tools,
    prompt=do_prompt,
)

agent = agent_class.get_model()

agent_executor = CustomExecutor(
    max_index= 5,
    max_rag_index= 3,
    k = 5,
    agent=agent,
    tools=tools,
    # verbose=True,
    max_iterations = 1000,
    # memory=memory,
)




# if __name__ == "__main__":
#     # inputs = input("请输入问题：")
#     # before_rag = use_rag.run(inputs)
#     # from pprint import pprint
#     #
#     # for chunk in do_agent_executor.stream({
#     #     "input": inputs,
#     #     "rag_context": [before_rag],
#     #     "important": [list_data_sources("14","28")]
#     # }):
#     #
#     #     print("\n当前 chunk 完整格式：")
#     #     pprint(chunk)
#     #     # if "messages" in chunk:
#     #     #     print("\n调用工具：")
#     #     #     pprint(chunk["messages"])
#
#     test = \
#         {
#             "input":"你好",
#             "important":list_data_sources("14","28"),
#             "history": "",
#             "summary": ""
#         }
#
#     for chunk in chain.stream(test):
#         print(chunk.content,end="")



