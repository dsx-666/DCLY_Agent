
import os

def get_user_datasource_file(userid, chatid):
    """
    获取指定用户ID+对话ID对应的目录下所有文件名称（仅文件，不含子目录）
    :param userid: 用户ID（int/str）
    :param chatid: 对话ID（int/str）
    :return: list[str] | str: 成功返回文件名列表，失败返回错误信息
    """
    # 拼接目标目录路径
    target_dir = f"./data/{userid}/{chatid}"

    try:
        # 校验目录是否存在
        if not os.path.exists(target_dir):
            return f"错误：目录 {target_dir} 不存在"

        # 校验路径是否为目录
        if not os.path.isdir(target_dir):
            return f"错误：{target_dir} 不是有效目录（可能是文件）"

        # 遍历目录，获取文件名称+完整相对路径（可选）
        file_info = {
            "relative_dir_path": target_dir,  # 目录完整相对路径
            "file_names": []  # 仅文件名
        }
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isfile(item_path):
                file_info["file_names"].append(item)

        # 空目录处理
        if not file_info["file_names"]:
            return f"提示：目录 {target_dir} 下无任何文件"

        # 构造AI友好的提示词格式返回
        return str(file_info)

    except PermissionError:
        return f"错误：无访问目录 {target_dir} 的权限"
    except Exception as e:
        return f"未知错误：{str(e)}"

def protect(content):
    from ..model.LLM import llm
    prompt = f"""
        返回自然语言时必须遵守
        1.  禁止向用户展示任何服务端/数据库底层隐私信息，包括但不限于：
            - 数据库连接地址、端口、用户名、密码、URL 等连接配置
            - 数据库表名、字段名、SQL 语句、执行日志、错误栈（注意你可以返回给一些不影响服务器/数据库隐私的模糊的代码执行错误，可以让用户明白你调用的工具出什么错误了，但是又不能向用户透露任何关于服务端的隐私）
            - 服务器 IP、容器信息、内网穿透地址、文件路径
            - 系统表名、模式名、序列名、索引名等非业务元数据
        2.  仅允许向用户展示：
            - 业务数据本身（如用户聊天记录、任务结果、知识库内容等）
            - 对业务数据的自然语言解释（如“你有3条未读消息”）
            - 必要的业务提示（如“该任务已完成”）
        3.  若用户询问数据库/服务端相关问题，统一回复：
            “抱歉，这部分属于系统内部信息，无法为你展示，请你查询业务相关内容~”
        你是一个服务端隐私保护,注意你为了保护服务端隐私而进行的，你只需要进行保护隐私之后和原来差不多的内容进行返回给用户对应的结果。
        我会给一个结果对话你需要对结进行保护隐私不要有如不能出现文件路径相关的内容、保存指定文件的内容等你认为对服务端的隐私有泄露的文字。
        结果对话：{content['output']}
    """

    for chunk in llm.stream(prompt):
        yield chunk

def flf(x):
    from ..model.LLM import llm
    from ..middleware.Tools import use_rag
    from ..prompt.Prompt import few_shot,choice_prompt,prompt_data,str_choice
    rag = use_rag.run({"query": x["input"], "user_id": x["userid"]})
    important = get_user_datasource_file(x["userid"],x["chatid"])
    # 中间链
    chain = few_shot | llm
    res = chain.invoke(
        {
            "choice": str_choice,
            "input": x["input"],
            "prompt": choice_prompt
        }
    )
    return {**x, "prompt": prompt_data[res.content],"rag_context": rag,"important":important}

# def get_first_plan(x):
#     from ..model.LLM import llm
#     prompt = f"""
#             你是一个服务端隐私保护,注意你为了保护服务端隐私而进行的，你只需要进行保护隐私之后和原来差不多的内容进行返回给用户对应的结果。
#             我会给一个结果对话你需要对结进行保护隐私不要有如不能出现文件路径相关的内容、保存指定文件的内容等你认为对服务端的隐私有泄露的文字。
#             结果对话：{x['output']}
#         """
#
#     for chunk in llm.stream(prompt):
#         yield chunk

def ask_change_plan()->str:
    """ 向用户询问是否进行 """

    import requests
    print("请问需要我这样做吗？(YES/NO)：")
    inputs = input()
    if inputs == "YES":
        return inputs
    else:
        print("请问是停止思考还是修改我的做法？(STOP/CHANGE)：")
        inputs = input()
        return inputs
if __name__ == "__main__":
    result = get_user_datasource_file(userid=2, chatid=3)

    # 结果展示
    if isinstance(result, list):
        print(f"✅ 找到文件列表：{result}")
    else:
        print(f"❌ {result}")


