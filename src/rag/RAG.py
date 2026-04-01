import json

import psycopg2
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
import os
from langchain.embeddings.base import Embeddings
import requests
import numpy as np
from ..sql.SQLConfig import DATABASES,DB_CONFIG,conn
docs = []
d_name = "rag"

from sentence_transformers import SentenceTransformer
import os

# 使用绝对路径
MODEL_PATH = os.path.abspath("text2vec-base-chinese")
# print(f"模型路径: {MODEL_PATH}")

# 使用本地的safetensors格式模型文件
# print("开始加载模型...")
model = SentenceTransformer(
    MODEL_PATH,
    local_files_only=True,
    trust_remote_code=True
)
# print("模型加载成功！")

class My_Embeddings(Embeddings):
    def embed_documents(self, texts):
        return [np.array(vec, dtype=np.float32) for vec in model.encode(texts)]
    def embed_query(self, text):
        return np.array(model.encode([text])[0], dtype=np.float32)


def creat_one_json_rag(dir_name):
    global docs
    for file_name in os.listdir(d_name):
        # 拼接文件的完整相对路径
        file_path = os.path.join(d_name, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # print(data)
        for key, value in data.items():
            print(value)
            for item in value:
                content = f"""
                        问题: {item['problem']}，对应的SQL语句: {item['sql']}
                    """.strip()
                docs.append(
                    Document(
                        page_content=content,
                        metadata={"type": "query_sql"}
                    )
                )

embeddings = My_Embeddings()


# 读取文件为二进制字节流
def read_file_to_bytes(file_path):
    """读取文件内容为二进制字节流"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件 {file_path} 不存在")

    with open(file_path, "rb") as f:
        return f.read()


# 将FAISS向量库保存到数据库
def save_faiss_to_database(vectorstore,user_id, save_local_path="faiss_rag"):
    """
    将FAISS向量库保存到数据库rag_knowledge表
    :param vectorstore: FAISS向量库对象
    :param save_local_path: 本地临时保存路径
    """
    # 先保存到本地（生成index.faiss和index.pkl）
    vectorstore.save_local(save_local_path)

    # 读取二进制文件内容
    faiss_file_path = os.path.join(save_local_path, "index.faiss")
    pkl_file_path = os.path.join(save_local_path, "index.pkl")

    try:
        faiss_bytes = read_file_to_bytes(faiss_file_path)
        pkl_bytes = read_file_to_bytes(pkl_file_path)
    except Exception as e:
        return

    # 连接数据库插入数据

    cursor = conn.cursor()
    # SQL
    insert_sql = """
                 INSERT INTO public.rag_knowledge (user_id, knowledge_content, knowledge_type, faiss, pkl, \
                                                   write_time, is_expired)
                 VALUES (%s, %s, %s, %s, %s, NOW(), 0) RETURNING knowledge_id; \
                 """

    # 执行逻辑
    try:
        # 拼接知识库内容
        total_content = "\n\n".join([doc.page_content for doc in docs]) if docs else "默认RAG知识库内容"

        # 执行插入
        cursor.execute(insert_sql, (
            user_id,  # user_id (bigint)
            total_content,  # knowledge_content (text)
            "sql_query",  # knowledge_type (varchar)
            faiss_bytes,  # faiss (bytea)
            pkl_bytes  # pkl (bytea)
        ))

        # 获取新增ID并提交
        knowledge_id = cursor.fetchone()[0]
        conn.commit()

    except psycopg2.Error as e:
        conn.rollback()
        raise "数据库错误"
    except Exception as e:
        raise e


if __name__ == "__main__":
    creat_one_json_rag(d_name)
    vectorstore = FAISS.from_documents(
        docs,
        embeddings
    )
    save_faiss_to_database(vectorstore,1)
