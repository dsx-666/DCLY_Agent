import uuid
import os
from urllib.parse import unquote
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException,Response
from fastapi.responses import StreamingResponse,FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import os, shutil, json
from typing import Union
# from fastapi.responses import FileResponse
from scipy.sparse import dia_array
import requests
from ..server.AsyncLoop import lifespan
from ..server.ServerFunction import *
from ..server.Websocket import ws_instances,MyWebsocket,WS_URL

# import os
print("当前运行目录:", os.getcwd())
data_dir_name = "data"

result_dir_name = "result"
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from ..server.Websocket import MyWebsocket,WS_URL
@app.post("/delete")
def delete_file(data: dict):
    userid = str(data["userId"])
    file_name = data["sourceName"]
    chat_id = str(data["chatId"])
    save_dir_path = os.path.join(data_dir_name, userid,chat_id)
    file_url = data["filePath"]
    msg = download_file(file_url,file_name, save_dir_path)
    res_msg = {"msg":msg}
    return res_msg
@app.get("/download")
def download_file(dir_name:str,file_name:str):
    try:
        file_name = unquote(file_name)
    except:
        raise HTTPException(status_code=400, detail="文件名格式错误")
        # 拼接绝对路径
    file_path = os.path.join(dir_name, file_name)
    file_path = os.path.abspath(file_path)
    # 文件必须存在，且是文件
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type="application/octet-stream"
    )
@app.api_route("/chat", methods=["GET", "POST"])
def chat(data:dict):
    try:
        
        ws_instances[f"{data["userId"]}_{data["chatId"]}"] = MyWebsocket(WS_URL,data["userId"],data["chatId"])
        chat_history = get_chat_records_by_id(data["userId"],data["chatId"])
        chat = {
            "userId": str(data["userId"]),
            "chatId": str(data["chatId"]),
            "input": chat_history["input"],
            "history": [
                f"user: {user},assistant: {assistant}"
                for user,assistant in zip(chat_history["user"],chat_history["assistant"])
            ]
        }

        return StreamingResponse(
            stream_to_user(chat),
            media_type="text/event-stream"
        )
    except Exception as e:
        if f"{data["userId"]}_{data["chatId"]}" in ws_instances:
            ws_instances[f"{data["userId"]}_{data["chatId"]}"].close()
        return f'data: {json.dumps({"type": "COMPLETE","think":False,"message": {"content": f"{e}"}, "file_url": None,"rag": None}, ensure_ascii=False)}\n\n'




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9100)




