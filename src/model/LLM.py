from langchain_openai import ChatOpenAI
import os
from typing import *
from sympy.physics.units import years
from pydantic import SecretStr
from ..classes.ModelClass import LLM
from langchain.schema import HumanMessage, SystemMessage

llm_class = LLM(
    base_url="https://api.deepseek.com",
    api_key=SecretStr("sk-9c52795f8658483f9761a6190deb8197"),
    model_name="deepseek-chat",
)
llm = llm_class.get_model()


