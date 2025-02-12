import time
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.base import BaseMessage
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="afsim-3b-bf16",
    openai_api_key="EMPTY",
    openai_api_base="http://192.168.100.202:8000/v1",
    max_tokens=2000,
    temperature=0.2,
)

def make_code_gen_call(messages: List[BaseMessage]):
    """
    使用训练后的 afsim-3b 模型，将需求转换为代码
    """
    for attempt in range(3):
        try:
            return llm.invoke(messages)
        except Exception as e:
            if attempt == 2:
                return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

