from ..chain.Chain import chain
if __name__ == "__main__":
    # inputs = input("请输入问题：")
    # before_rag = use_rag.run(inputs)
    # from pprint import pprint
    #
    # for chunk in do_agent_executor.stream({
    #     "input": inputs,
    #     "rag_context": [before_rag],
    #     "important": [list_data_sources("14","28")]
    # }):
    #
    #     print("\n当前 chunk 完整格式：")
    #     pprint(chunk)
    #     # if "messages" in chunk:
    #     #     print("\n调用工具：")
    #     #     pprint(chunk["messages"])

    test = \
        {
            "input":"查看该数据内容",
            "userid":2,
            "chatid":3,
            "history": "",
            "summary": ""
        }

    for chunk in chain.stream(test):
        print(chunk)
