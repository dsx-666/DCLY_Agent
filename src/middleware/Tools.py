import os
import tempfile
from typing import Union
from langchain.tools import tool
from typing import Callable
tool_file_name = os.path.abspath(os.path.basename(__file__))
from typing import Any
tools_name = {"do_tools":"do_tools"}
import sys
import traceback
import sys
import io
from typing import Any
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
import psycopg2
from psycopg2 import OperationalError
from ..sql.SQLConfig import DB_CONFIG,conn
from ..docker.Pool import my_env,use_my_env
RAG_file_name = "faiss_rag"

from ..rag.RAG import *
min_score = 0.3
vectorstore = FAISS.load_local(RAG_file_name, embeddings=embeddings, allow_dangerous_deserialization=True)

@tool
def read_file(file_path:str)->str:
    """
        用于阅读文件内容
        :param file_path:文件名字
        :return:str表示文件内容或者出错
    """

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        try:
            with open(file_path, "r", encoding="gbk") as f:
                return f.read()
        except Exception as e:
            return f"出错了：{e}"

@tool
def write_to_file(file_path, content):
    """
        将指定内容写入指定文件，你可以写相关内容的决策
        :param file_path 你想保存的文件名字
        :param content 保存文件的内容
        :return: str表示写入成功或者出错
    """

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content.replace("\\n", "\n"))
        return "写入成功"
    except Exception as e:
        return f"出错了：{e}"

@tool
def run_terminal_command(command):
    """
        用于执行终端命令
        :param command 表示终端执行命令
        :return: 返回执行结果
    """
    import subprocess
    run_result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return "执行成功" if run_result.returncode == 0 else run_result.stderr

@tool
def get_current_time():
    """
        用于获取时间
        :return: 返沪时间
    """
    from datetime import datetime
    current_time = datetime.now()
    return f"当前时间:{current_time}"


@tool
def printf(string:str)->str:
    """
        打印信息
        :param string 需要打印的具体内容
        :return 已打印具体内容
    """
    print(string)
    return f"已打印：{string}"



@tool
def add_tool(def_str:str,def_name:str)->str:
    """
        注意：在加入新的工具前必须要对这个工具进行分析，一定要得到最好的新工具的分析再添加新工具，并且如果说需要导入包则需要将包放在函数里面导入，否则这个工具就是错误的
        参数加入新添的工具方法
        需要分析完了新添工具的代码后，在工具方法中动态加入该工具,并且会在工具文件中结合日志加入工具便于继续利用
        :param def_str: 写的函数的代码对应的str,并且这个字符串里面的代码只有一个函数,导包配置都在这个函数里面进行
        :param def_name: 函数名字并且函数名字和def_str函数里面的名字一样
        :return: 执行成功，或者工具方法添加失败
    """
    # import json
    from ..model.Agent import agent_executor
    from datetime import datetime
    global tool_file_name
    global tools
    local_vars = {}
    try:
        exec(def_str, globals(), local_vars)
        func = local_vars[def_name]
        tools.append(func)
        agent_executor.tools = tools
        current_time = datetime.now().strftime("%Y年%m月%d日 %H点%M分%S秒")
        with open(tool_file_name, "a", encoding="utf-8") as f:
            # 写日志
            f.write(f"\n# 函数写入时间: {current_time}\n\n")
            # 写注解
            f.write(f"@tool\n")
            # 写函数
            f.write(f"{def_str}\n")
            # 写tools的加入
            f.write(f"{tools_name['do_tools']}.append({def_name})\n")
        return f"工具添加成功"
    except Exception as e:
        return f"工具添加失败，{e}"



@tool
def run_foot(file_name:str)->Any:
    """
        运行脚本来获取想要的信息
        :param file_name:
        :return: 返回脚本运行的结果或者错误
    """
    try:
        exec(open(file_name).read())
        return "成功运行脚本"
    except Exception as e:
        return f"{e}"

@tool
def write_foot(file_name:str,content:str)->str:
    """
        将指定脚本写入指定文件,你使用这个工具的时候必须确保脚本对你有意义
        :param file_name: 你想保存的脚本的文件名字
        :param content: 脚本的内容
        :return: str表示写入成功或错误
    """
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(content)
        return f"脚本已经写完，保存在{file_name}"
    except Exception as e:
        return f"脚本写入错误,{e}"

@tool
def delete_foot(file_name):
    """
        觉得脚本没有意义的时候删除脚本
        :param file_name 你想删除的脚本的文件名字
        :return: str表示删除的成功或错误
    """
    try:
        os.remove(file_name)
        return f"{file_name}文件已删除"
    except Exception as e:
        return f"{e}"

@tool
def run_code(code: str) -> str:
    """
        执行任意 Python 代码字符串，注意每一次调用的code均在不同环境下进行，故每一次调用它必须忘记之前调用的其他code来。
        Agent 通过该工具不断执行代码。
        参数:
        :param code: 可执行的 Python 代码
        返回:
        :return: 执行成功得输出，或完整报错信息
    """
    # 防止原来的缓冲区有其他字符串

    return use_my_env(my_env, "run_code", {"code": code})


@tool
def query_mysql(
    host: str,
    user: str,
    password: str,
    database: str,
    query: str,
    limit: int = 100
) -> str:
    """
        安全查询 MySQL 数据库（仅支持 SELECT），返回 JSON 结构化结果。
        :param host: 数据库地址，例如 localhost
        :param user: 用户名
        :param password: 密码
        :param database: 数据库名称
        :param query: SQL 查询语句，仅允许 SELECT
        :param limit: 返回最大行数,默认 100
        :return:返回查询数据库内容（json格式）
    """
    import mysql.connector
    from mysql.connector import Error
    import json
    import re

    connection = None
    cursor = None
    # 只允许 SELECT
    if not re.match(r"^\s*select\b", query, re.I):
        return json.dumps({
            "success": False,
            "error": "只允许 SELECT 查询"
        }, ensure_ascii=False)

    # 自动 LIMIT
    if "limit" not in query.lower():
        query = f"{query.rstrip(';')} LIMIT {limit};"

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()

        return json.dumps({
            "success": True,
            "row_count": len(rows),
            "data": rows
        }, ensure_ascii=False, indent=2)

    except Error as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, ensure_ascii=False)

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()


@tool
def open_data_source(code: str) -> str:
    """
        用于执行“打开数据源”的 Python 代码。
        Agent 自行决定使用pandas等方式。
        :param code: 打开数据源并打印信息的 Python 代码
        :return: 执行结果或报错信息
    """
    return run_code.run(code)
@tool
def visualize(code: str) -> str:
    """
        你可以根据需求来进行绘图
        执行绘图相关代码，用matplotlib等工具来实现。
        Agent 只负责生成代码，工具只负责执行。
        参数:
        :param code: 绘图 Python 代码
        :return: 执行结果或报错信息
    """
    return run_code.run(code)


@tool
def use_rag(query, user_id):
    """
        使用本地 rag 向量库根据用户的自然语言问题查询相关文档，并返回生成的答案。因此在你需要获取一些信息时也可以通过这个工具来获取
        :param query: (str): 用户的自然语言问题，例如 "统计各币种的产品数量"。
        :param user_id: (int): 用户ID，用于加载专属RAG
        :return: str: 根据 rag 知识库检索并整理出的答案文本。
    """
    try:
        # ========== 核心修改部分开始 ==========



        cursor = conn.cursor()
        # 查询该用户是否有有效RAG记录
        cursor.execute("""
                       SELECT 1
                       FROM public.rag_knowledge
                       WHERE user_id = %s
                         AND is_expired = 0
                         AND knowledge_type = 'sql_query'
                         AND faiss IS NOT NULL
                         AND pkl IS NOT NULL LIMIT 1;
                       """, (user_id,))
        has_rag = cursor.fetchone()
        cursor.close()


        # 无RAG记录时，先初始化（执行save_faiss_to_database）
        if not has_rag:
            try:
                save_faiss_to_database(vectorstore, user_id)  # 执行初始化

            except Exception as init_e:
                return f"错误：初始化用户{user_id}的RAG知识库失败：{str(init_e)}"

        # 原有主逻辑（加载RAG+检索）
        with tempfile.TemporaryDirectory() as temp_dir:


            cursor = conn.cursor()
            cursor.execute("""
                           SELECT faiss, pkl
                           FROM public.rag_knowledge
                           WHERE user_id = %s
                             AND is_expired = 0
                             AND knowledge_type = 'sql_query'
                           ORDER BY write_time DESC LIMIT 1;
                           """, (user_id,))

            result = cursor.fetchone()
            cursor.close()

            if not result:
                return f"错误：未找到用户ID={user_id}的有效RAG知识库"

            # 补充faiss/pkl字段判空
            faiss_bytes, pkl_bytes = result
            if faiss_bytes is None or len(faiss_bytes) == 0:
                return f"错误：用户ID={user_id}的RAG记录中faiss字段为空"
            if pkl_bytes is None or len(pkl_bytes) == 0:
                return f"错误：用户ID={user_id}的RAG记录中pkl字段为空"

            # 写入临时文件并加载向量库
            faiss_path = os.path.join(temp_dir, "index.faiss")
            pkl_path = os.path.join(temp_dir, "index.pkl")
            with open(faiss_path, "wb") as f:
                f.write(faiss_bytes)
            with open(pkl_path, "wb") as f:
                f.write(pkl_bytes)

            # 原有检索逻辑
            retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
            docs = retriever.invoke(query)
            ans = ""
            for doc in docs:
                ans += doc.page_content
            return ans
    except Exception as e:
        return f"运行错误：{e}"

def add_rag(query):
    """
        获取分数,并根据分数动态的加入RAG
        :param query 查询RAG的内容
        :return：是否可用放入RAG
    """
    docs_and_scores = vectorstore.similarity_search_with_score(
        query,
        k=1
    )

    if docs_and_scores:
        _, score = docs_and_scores[0]
    else:
        score = float("inf")
    if score > min_score:
        doc = Document(
            page_content=query,
            metadata={
                "source": "agent_answer"
            }
        )

        vectorstore.add_documents([doc])
        vectorstore.save_local(RAG_file_name)

        return True  # 表示已写入

    return False


tools = [
            write_to_file,
            run_terminal_command,
            get_current_time,
            printf,
            use_rag,
            visualize,
            run_code,
            # query_mysql
            ]

# tools_name = [tool.func.__name__ for tool in middleware]

