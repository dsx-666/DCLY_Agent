# RAG.py 开头添加（强制切换到Agent_use工作目录，避免路径错位）
import os
import sys
# 切换到Agent_use根目录（核心：确保模型路径基于此目录）
WORK_DIR = "D:\\PythonProject\\Agent_use"
os.chdir(WORK_DIR)
sys.path.append(WORK_DIR)

# 加载模型（绝对路径 + local_files_only=True）
from sentence_transformers import SentenceTransformer
# 替换为你的本地模型文件夹绝对路径（确保文件夹存在且文件完整）
MODEL_PATH = os.path.join(WORK_DIR, "local_text2vec-base-chinese")
# 打印路径验证（关键：确认路径正确）
print(f"加载本地模型：{MODEL_PATH}")
print(f"模型文件夹是否存在：{os.path.exists(MODEL_PATH)}")

# 核心：强制本地加载，且用绝对路径
model = SentenceTransformer(
    MODEL_PATH,  # 绝对路径，避免工作目录歧义
    local_files_only=True,  # 禁止联网
    cache_folder=os.path.join(WORK_DIR, "models_cache")  # 自定义缓存目录，避免默认缓存干扰
)