import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# llm = VLLMOpenAI(
#     openai_api_key="EMPTY",
#     openai_api_base="http://192.168.100.231:8000/v1",
#     model_name="afsim-3b",
#     model_kwargs={"stop": ["."]},
# )

llm = ChatOpenAI(
    model="afsim-3b",
    openai_api_key="EMPTY",
    openai_api_base="http://192.168.100.231:8000/v1",
    # max_tokens=5,
    temperature=0.2,
)

def make_api_call(messages, max_tokens):
    for attempt in range(3):
        try:
            # response = llm.chat.completions.create(
            #         messages=messages,
            #         max_tokens=max_tokens,
            #         temperature=0.2,
            #     ) 
            # return response.choices[0].message.content
            return llm.invoke(messages)
        except Exception as e:
            if attempt == 2:
                return {"title": "Error", "content": f"Failed to generate step after 3 attempts. Error: {str(e)}", "next_action": "final_answer"}
            time.sleep(1)  # Wait for 1 second before retrying


if __name__ == "__main__":
    # messages = [
    #     {"role": "system", "content": """You are an expert AFSIM assistant."""},
    #     {"role": "user", "content": "生成"},
    # ]
    messages = [
        SystemMessage(
            content="You are an expert AFSIM assistant."
        ),
        HumanMessage(
            content="我的飞机需要通讯组件，能给我一个示例吗？"
        ),
    ]

    res = make_api_call(messages, 300)
    print(res.content)