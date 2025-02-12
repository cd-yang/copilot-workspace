import json
import time
from typing import List

from loguru import logger
from ollama import Client

ollama_client = Client(
    host='http://192.168.100.231:11434',
    # host='http://192.168.100.202:11434',
)
model="qwen2.5-coder:32b"
# model="deepseek-r1:14b"

USE_CHINESE_PROMPT = True
INCLUDE_AFSIM_BACKGROUND = True
MAX_STEP_COUNT = 5 # Max steps to prevent infinite thinking time. Can be adjusted.

def make_reasoning_call(messages: List, max_tokens=300, is_final_answer=False):
    """
    使用 qwen2.5-coder 模型，对文本进行推理
    """
    logger.info("Starting make_reasoning_call function")
    logger.info(f"API request: {messages}")

    for attempt in range(3):
        try:
            response = ollama_client.chat(
                model,
                messages=messages,
                options={"temperature":0.2, 
                        #  "num_predict":max_tokens # 这里可能会导致 unicode 解析错误
                         },
                format='json',
            )
            logger.info(f"API response: {response}")

            return json.loads(response['message']['content'])
        except Exception as e:
            logger.error(f"Exception occurred: {str(e)}")
            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying

    logger.info("Ending make_reasoning_call function")
