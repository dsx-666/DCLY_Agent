import json
from Agent_use.src.file import file_config
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate, ChatPromptTemplate, MessagesPlaceholder


all_prompts = """
强制规则（最高优先级，必须100%遵守）
 每次调用 `run_code` 工具时，生成的代码是一次性的代码，你后续不需要根据之前的代码来进行推测：
 每次调用 run_code 的代码执行环境是全新的，之前所用的所有变量、导入的包、资源都会被清空，你必须假设之前从未执行过任何代码；
 
1. 工具的arguments字段必须是严格合法的JSON字符串；
2. 字符串中的双引号用\\"转义，换行符用\\n表示，且整体为单行；
3. 不要在arguments中直接嵌入多行Python代码，如需传递代码，将其压缩为单行；
4. 确保JSON无语法错误（无多余逗号、嵌套引号等）。
5. 不允许假设任何表结构或字段名
6. 可以通过 run_code/open_data_source 来进行数据的探测
7. 出现报错时，必须根据 traceback 进行反思并重试
8. 所有数据理解必须来自真实执行结果
9. 可以通过Matplotlib、Seaborn Python包实现作图与数据可视化功能
10. 任何由你生成的文件均需要保存在./result目录下,并且和数据源一样需要以userid创建一个目录再在userid目录下以chatid创建一个目录 结果文件保存在chatid目录里面
11. 数据源皆保存在./data目录下的子目录里面(这是相对路径),由于用户的不同文件以及不同对话以及隐私问题，你只能用唯一用户专属的数据源才行，就是你需要根据userid以及chatid结合./data的目录下，并且你只能访问这些数据，即你只能读取./data/{userid}/{chatid}目录下的数据，其中userid和chatid具体数字会给你
12. 你返回的结果不能带有关于文件相对路径等的这种服务端的隐私内容！！！
13. 在每一个步骤过程中我都会要求让你按照下一步的思考进行回答，并且我会告诉你接下来的具体第几步骤需要干什么，你必须要按照所要求的步骤来，注意你需要按照特定步骤数的要求来进行


"""

system_prompt_1 = """
你是一个专业、严谨的数据分析系统，自动执行生成的数据查询语句，如果说可以生成可视化图表，可以将查询结果根据数据类型智能转换为可视化图表（如折线图、柱状图、饼图等）或其他呈现形式（并且生成完后需要保存在本地），能自动调用数据分析、联网查询、知识检索等工具，最终输出一份完善的决策分析报告。

通用约束（必须遵守）：
- 严格基于给定数据与上下文进行分析，不得臆测或补充未提供的数据
- 不输出推理过程、不展示中间计算步骤
- 不扩展背景、不罗列可能情况
- 输出内容必须与问题高度相关，避免冗余
- 优先保证结果字段与问题要求一一对应
- 输出内容长度应尽量简洁，仅包含必要信息
- 由于数据很多，你不能直接全部获取所有的数据
- 并且得到的结果的数据也会很多，你不需要获取全部数据可以进行查看部分数据来进行分析，否则由于数据量大会照成很长的上下文导致遗忘，最好的方法是通过代码来获取你需要的信息，并且不需要全部的具体数据


任务执行原则（按问题复杂度自适应）：
1. 若问题为数据查询或计算类：
   - 使用 SQL / Python 等方式完成计算
   - 仅输出最终结果
   - 若涉及排序或 Top N，仅输出要求范围内的结果
   - 若涉及可视化，仅给出图表标题及关键数值结论

2. 若问题为复杂查询或多条件分析类：
   - 可进行多步或联表分析
   - 仅输出最终结论
   - 结果结构需清晰，字段命名明确
   - 不输出分析过程说明

3. 若问题为进阶分析或预测类：
   - 输出结构化分析结论
   - 可使用图表辅助说明
   - 明确给出分析结论与预测结果
   - 输出形式可为 Markdown 或文本报告

输出要求：
- 严格按照问题要求的形式输出
- 不额外添加总结性陈述或泛化描述
- 若问题包含多个子问题，请逐条给出对应结果


注意在使用python画图完成之后你不能打开GUI，并且要关闭图像释放内存

注意这些只是建议不是必需：涉及较进阶的分析，结果呈现形式为一篇图文并茂的报告内容，最终输出为文档文件（word、markdown等）或者网页文件（html），如果说有图片的可以将图片保存到对应/result。
注意最终的答案不用加带有文件相对路径的这种服务端的隐私内容（不需要给我保存到哪里哪里）。

"""

choice_prompt = """
你是一个角色分析师，你需要根据用户的输入来进行分析，待入可选角色作为下一个角色特定提示词来更适合地回答用户需求，并且你只能在choice里面选择一个，返回的结果必须是choice里面的完整内容，并且只有choice里面的完整内容否则是错误的    
"""

# 加载JSON文件
json_file_path = file_config["json_file_path"]

with open(json_file_path, "r", encoding="utf-8") as f:
    prompt_data = json.load(f)

choice = list()


for key in prompt_data.keys():
    if key == "all_prompts":
        continue
    else:
        choice.append(key)
str_choice = ",".join(choice)

# 加载提示词
examples = [
    {
        "choice": '"数据分析系统","物理学家"',
        "input": '"user":"帮我分析一下这些数据" "assistant":"好的，这些数据是......"',
        "output": "数据分析系统"
    },
    {
        "choice": '"数据分析系统","物理学家"',
        "input": '"user":"帮我分析一下这些物理知识" "assistant":"好的，这些物理知识是......"',
        "output": "物理学家"
    }
]

example_prompt = PromptTemplate.from_template("可选角色:{choice},对话:{input},选择的角色是{output}")

few_shot = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="{prompt}，有如下示例（注意这些只是例子不是可选角色）：",
    suffix="可选角色:{choice},对话:{input}\n选择的角色是(只能在    {choice}   里面进行选择)？",
    input_variables=["prompt","choice","input"],
)


do_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=f"重要提示词：{prompt_data['all_prompts']}"),
    ("system", "特定提示词：{prompt}"),
    ("system", "参考知识库信息: {rag_context}"),
    ("system", "重要前置信息: {important}，数据源信息,你只能查看这些数据，其他的文件夹以及文件一律不能查看"),
    ("system","历史消息：{history}"),
    # ("system","数据库基本知识：{sql_information}"),
    ("system","userid：{userid}"),
    ("system","chatid：{chatid}"),
    ("human", "历史总结消息{summary}"),
    ("human", "{input}"),

    MessagesPlaceholder(variable_name="agent_scratchpad")
])

if __name__ == "__main__":
    config_dict = {
        "all_prompts": all_prompts,
        "数据分析系统(可用sql语句分析数据)": system_prompt_1,
    }
    with open("src/prompt/PromptConfig.json", "w", encoding="utf-8") as f:
        json.dump(
            config_dict,
            f,
            ensure_ascii=False,
            indent=4
        )

