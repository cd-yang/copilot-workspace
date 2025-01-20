import json
import time
from typing import List

from ollama import Client

ollama_client = Client(
    host='http://192.168.100.231:11434',
    # host='http://192.168.100.201:11434',
)
# model="qwen2.5:72b"
# model="qwen2.5:32b"
model="qwen2.5-coder:32b"
# model="qwen2.5-coder:32b-instruct-fp16"
# model="qwq:32b-preview-fp16"
# model="qwq:32b"

USE_CHINESE_PROMPT = True
INCLUDE_AFSIM_BACKGROUND = True
MAX_STEP_COUNT = 5 # Max steps to prevent infinite thinking time. Can be adjusted.

def make_reasoning_call(messages: List, max_tokens=300, is_final_answer=False):
    """
    使用 qwen2.5-coder 模型，对文本进行推理
    """
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
            # print('ollama response:', response)

            # 尝试处理 qwen2.5:72b 模型返回的 content 包含的 unicode 字符错误，但是似乎没有效果，先不使用 qwen2.5:72b 模型
            # response_content = response['message']['content']
            # response_content = response_content.encode('utf-8').decode('unicode_escape')
            # return json.loads(response_content)

            return json.loads(response['message']['content'])
        except Exception as e:
            print('********** Exception start *********', f"Error: {str(e)}\n")
            if attempt == 2:
                if is_final_answer:
                    return {"title": "Error", "content": f"Failed to generate final answer after 3 attempts. Error: {str(e)}"}
                else:
                    return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying
