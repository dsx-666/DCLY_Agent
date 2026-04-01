import psycopg2

from ..model.Agent import  agent_executor
from ..chain.Chain import chain
# from ..llm_use_function.Function import list_data_sources
from ..llm_use_function.Function import summarize
from ..model.LLM import llm
import json
import requests
import os
import shutil
from ..sql.SQLConfig import conn
from concurrent.futures import ThreadPoolExecutor  # 多线程提速
from urllib.parse import urlparse
from langchain_core.messages import HumanMessage, AIMessage

domain = "http://11ou939nk8818.vicp.fun:39858"


def delete_result_folder():
    result_dir = os.path.join(os.getcwd(), "result")
    if os.path.exists(result_dir) and os.path.isdir(result_dir):
        shutil.rmtree(result_dir)



def download_file(file_url: str, save_name: str, save_dir):
    """
        从指定URL下载文件到本地
        :param file_url: 文件的网络URL
        :param save_name: 保存到本地的文件名
        :param save_dir: 保存目录
        :return: ture or false
    """
    try:
        # 发送GET请求下载文件
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()

        # 拼接本地完整文件路径
        local_file_path = os.path.join(save_dir, save_name)
        os.makedirs(save_dir, exist_ok=True)
        # 写入文件
        with open(local_file_path, "wb") as f:
            f.write(response.content)
        return f"文件下载成功"

    except requests.exceptions.RequestException as e:
        # 捕获网络请求异常，返回具体错误信息
        return f"文件下载失败：{str(e)}"

def sum_fun(history:list):
    """
        LLM的前置处理
        :param history: str 表示历史对话
        :return: 返回截断后的历史对话和总结
    """
    if len(history) > agent_executor.k:
        his = history[-agent_executor.k:]
        summary = summarize(llm,history[:-agent_executor.k])
    else:
        his = history
        summary = None

    return his,summary
def download_url():
    result_url_list = list()
    rag_url_list = list()
    result = "result"
    rag = "faiss_rag"
    result_abs = os.path.abspath(result)
    rag_abs = os.path.abspath(rag)
    for file_name in os.listdir(result_abs):
        # 拼接当前文件的完整请求
        file_full_path = os.path.join(result, file_name)
        if os.path.isfile(file_full_path):
            url = f"{domain}/download?dir_name={result}&file_name={file_name}"
            result_url_list.append(url)
    for file_name in os.listdir(rag_abs):
        # 拼接当前文件的完整请求
        file_full_path = os.path.join(rag, file_name)
        if os.path.isfile(file_full_path):
            url = f"{domain}/download?dir_name={rag}&file_name={file_name}"
            rag_url_list.append(url)
    return result_url_list, rag_url_list

def stream_to_user(chat:dict):
    """
        将 LangChain Agent stream 转换为用户可展示的逐 token 流
    """
    try:
        history, summary = sum_fun(chat['history'])

        qes = {
            "history": history,
            "summary": summary or "",
            "input": chat['input'],
            "userid": chat['userId'],
            "chatid": chat['chatid']
        }

        for chunk in chain.stream(qes):
            yield f'data: {json.dumps({"type": "CONTINUE", "think": False, "message": {"content": chunk.content}, "file_url": None, "rag": None}, ensure_ascii=False)}\n\n'


        result_url_list, rag_url_list = download_url()

        yield f'data: {json.dumps({"type": "COMPLETE","think":False,"message": {"content": ""}, "file_url": result_url_list,"rag": rag_url_list}, ensure_ascii=False)}\n\n'

        delete_result_folder()
        return

    except Exception as e:
        yield f'data: {json.dumps({"type": "COMPLETE","think":False,"message": {"content": f"{e}"}, "file_url": None,"rag": None}, ensure_ascii=False)}\n\n'

        return


def get_user_datasource_by_uid(user_id):
    """
    根据用户ID查询public.user_data_source表中的所有数据源信息
    :param user_id: 目标用户ID
    :return: list[dict] 数据源列表，每个元素包含source_id/chat_id/file_path(阿里云URL)等字段
    """

    try:
        # 连接数据库

        cursor = conn.cursor()

        # 查询指定用户的所有有效数据源（仅查user_data_source表）
        query_sql = """
                    SELECT source_id, user_id, chat_id, source_name, file_path, file_ext
                    FROM public.user_data_source
                    WHERE user_id = %s \
                      AND is_valid = 1; \
                    """
        cursor.execute(query_sql, (user_id,))

        # 获取字段名和数据
        columns = [desc[0] for desc in cursor.description]
        datasource_list = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return datasource_list

    except psycopg2.Error as e:

        return []



def create_dir_by_uid_chatid(user_id, chat_id):
    """
    按用户ID→对话ID创建分级文件夹（./data/{user_id}/{chat_id}/）
    :param user_id: 用户ID
    :param chat_id: 对话ID
    :return: str 创建的文件夹路径
    """
    # 根目录固定为./data
    base_dir = f"./data/{user_id}"
    chat_dir = f"{base_dir}/{chat_id}"

    # 递归创建目录（忽略已存在）
    os.makedirs(chat_dir, exist_ok=True)

    return chat_dir


def download_aliyun_file(url, save_path, timeout=30, chunk_size=1024 * 1024 * 8):
    """
    下载阿里云盘文件
    :param url: 阿里云盘下载URL
    :param save_path: 本地保存路径
    :param timeout: 请求超时时间
    :param chunk_size: 分片大小
    :return: bool 是否下载成功
    """
    # 阿里云盘下载请求头优化
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # 移除Referer/Accept等可能触发升级的字段
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }

    try:

        # 禁用重定向限制，阿里云盘URL可能有302跳转
        response = requests.get(
            url,
            headers=headers,
            stream=True,
            timeout=timeout,
            allow_redirects=True
        )
        response.raise_for_status()  # 捕获HTTP错误

        # 分片写入文件
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

        return True

    except requests.exceptions.RequestException as e:
        # 清理未下载完成的文件
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def download_aly_file(user_id, max_workers=3):
    """
    主函数：按用户ID下载所有阿里云盘文件，分目录保存
    :param user_id: 目标用户ID
    :param max_workers: 多线程数
    """
    # 查询用户所有数据源
    datasource_list = get_user_datasource_by_uid(user_id)
    print(datasource_list)
    if not datasource_list:
        return

    # 多线程批量下载
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for data in datasource_list:
            # 跳过无阿里云URL的数据源
            if not data.get("file_path") or not data["file_path"].startswith("http"):
                continue

            # 跳过无对话ID的数据源
            if not data.get("chat_id"):
                continue

            # 生成保存路径
            chat_dir = create_dir_by_uid_chatid(user_id, data["chat_id"])

            source_name = data["source_name"]
            # 分离名称和后缀
            pure_name = os.path.splitext(source_name)[0]
            # 清理纯名称末尾的.（兜底处理）
            pure_name = pure_name.rstrip('.')

            # 处理文件后缀（清理开头的.，确保仅保留后缀名）
            if data.get("file_ext") and data["file_ext"].strip():
                clean_ext = data["file_ext"].lstrip('.')  # 如.xlsx→xlsx，xlsx→xlsx
                file_name = f"{pure_name}.{clean_ext}"
            else:
                file_name = pure_name  # 无后缀时仅用纯名称
            save_path = os.path.join(chat_dir, file_name)

            # 提交多线程任务
            futures.append(executor.submit(download_aliyun_file, data["file_path"], save_path))

        # 等待所有任务完成
        for future in futures:
            future.result()




def get_chat_records_by_id(user_id: str, chat_id: str) -> dict:
    """
    根据用户ID和对话ID查询public.user_chat_record表中的所有记录
    :param user_id: 目标用户ID
    :param chat_id: 目标对话ID
    :return: list[dict] 对话记录列表，包含user和assistant的context
    """
    try:
        # 检查数据库连接
        if conn is None:
            print("数据库连接失败")
            return []
        
        # 连接数据库
        cursor = conn.cursor()
        
        # 查询指定用户和对话的所有有效记录
        query_sql = """
                    SELECT record_id, content, role
                    FROM public.user_chat_record
                    WHERE user_id = %s
                      AND chat_id = %s
                    ORDER BY record_id ASC;
                    """
        cursor.execute(query_sql, (user_id, chat_id))
        
        # 获取结果
        records = cursor.fetchall()
        # print(records)
        # 按role分组，根据record_id排序
        user_contexts = []
        assistant_contexts = []
        
        for record in records:
            record_id, context, role = record
            if role == 'user':
                user_contexts.append(context)
            elif role == 'assistant':
                assistant_contexts.append(context)
        
        # 构建返回结果
        result = {
            "user":[ans for ans in user_contexts[:-1]],
            "assistant": [ans for ans in assistant_contexts],
            "input": user_contexts[-1]
        }
        
        return result
        
    except psycopg2.Error as e:
        print(f"数据库查询错误: {str(e)}")
        return []
    except Exception as e:
        print(f"其他错误: {str(e)}")
        return []
    finally:
        # 确保游标关闭
        if 'cursor' in locals() and cursor:
            try:
                cursor.close()
            except:
                pass

if __name__ == "__main__":
    # 下载用户ID=1的所有阿里云盘数据源文件
    print(get_chat_records_by_id(user_id="2", chat_id="3"))



