import json
import time
from loguru import logger

from ollama_api import make_reasoning_call

USE_CHINESE_PROMPT = True
INCLUDE_AFSIM_BACKGROUND = True
MAX_STEP_COUNT = 5 # Max steps to prevent infinite thinking time. Can be adjusted.

# Configure loguru
logger.add("file_{time}.log", level="INFO", format="{time} - {level} - {message}")

def generate_task_response(prompt):
    logger.info("Starting generate_task_response function")
    if INCLUDE_AFSIM_BACKGROUND:
        system_info = """AFSIM是一个通用的建模框架，由美国空军研究实验室（AFRL）开发和维护1。它的主要目的是用于模拟和分析作战环境，帮助用户评估军事战略和战术决策的有效性。
具体来说，AFSIM提供了完整的仿真环境，包括：
1.各种战斗平台（例如飞机、坦克、船只等）的模拟。
2.各种武器系统的模拟。
3.环境效应的建模，例如天气、地形等。

你是一位AFSIM建模的专家，将用户的需求，分解成一个个细颗粒度的需求。可以一步一步解释你的推理。"""
    else:
        system_info = "你是一位专业的人工智能助手，可以一步一步解释你的推理。"
    if USE_CHINESE_PROMPT:
        messages = [
            {"role": "system", "content": system_info + """对于每个步骤，提供一个标题来描述你在该步骤中所做的事情，以及内容。决定是否需要另一个步骤，或者是否准备好给出最终答案。
以 JSON 格式回复"title"、"content"和"next_action"（"continue"或"final_answer"）键。尽可能多地使用推理步骤。至少 3 个。了解你作为LLM的局限性，以及你能做什么和不能做什么。在你的推理中，包括对替代答案的探索。考虑你可能是错的，如果你的推理是错的，它会在哪里。充分测试所有其他可能性。你可能会错。当您说您正在重新检查时，请真正重新检查，并使用另一种方法进行。不要只是说您正在重新检查。使用至少 3 种方法来得出答案。使用最佳实践。

有效 JSON 响应的示例：
```json
{
"title"："识别关键信息"，
"content"："要开始解决这个问题，我们需要仔细检查给定的信息并确定将指导我们解决过程的关键要素。这涉及..."，
"next_action"："continue"
}```
"""},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "谢谢！我现在会按照我的指示一步一步思考，在分解问题之后从头开始。"}
        ]
    else:
        messages = [
            {"role": "system", "content": """You are an expert AI assistant that explains your reasoning step by step. For each step, provide a title that describes what you're doing in that step, along with the content. Decide if you need another step or if you're ready to give the final answer. Respond in JSON format with 'title', 'content', and 'next_action' (either 'continue' or 'final_answer') keys. USE AS MANY REASONING STEPS AS POSSIBLE. AT LEAST 3. BE AWARE OF YOUR LIMITATIONS AS AN LLM AND WHAT YOU CAN AND CANNOT DO. IN YOUR REASONING, INCLUDE EXPLORATION OF ALTERNATIVE ANSWERS. CONSIDER YOU MAY BE WRONG, AND IF YOU ARE WRONG IN YOUR REASONING, WHERE IT WOULD BE. FULLY TEST ALL OTHER POSSIBILITIES. YOU CAN BE WRONG. WHEN YOU SAY YOU ARE RE-EXAMINING, ACTUALLY RE-EXAMINE, AND USE ANOTHER APPROACH TO DO SO. DO NOT JUST SAY YOU ARE RE-EXAMINING. USE AT LEAST 3 METHODS TO DERIVE THE ANSWER. USE BEST PRACTICES.

Example of a valid JSON response:
```json
{
    "title": "Identifying Key Information",
    "content": "To begin solving this problem, we need to carefully examine the given information and identify the crucial elements that will guide our solution process. This involves...",
    "next_action": "continue"
}```
"""},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Thank you! I will now think step by step following my instructions, starting at the beginning after decomposing the problem."}
        ]
    
    # steps = []
    step_count = 0
    total_thinking_time = 0
    
    while True:
        logger.info(f"Starting step {step_count} in generate_task_response function")
        start_time = time.time()
        try:
            step_data = make_reasoning_call(messages, 300)
        except Exception as e:
            logger.error(f"Exception occurred in generate_task_response function: {str(e)}")
            raise e
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time

        if 'title' not in step_data:
            step_data['title'] = "..."
        if 'content' not in step_data:
            logger.warning('未生成有效 content，重试...')
            continue
        
        messages.append({"role": "assistant", "content": json.dumps(step_data)})
        
        if step_data['next_action'] == 'final_answer' or step_count > MAX_STEP_COUNT:
            break
        
        step_count += 1

        logger.info(f"Completed step {step_count} in generate_task_response function")
        yield f"Step {step_count}: {step_data['title']}", step_data['content'], thinking_time, None

    if USE_CHINESE_PROMPT:
        messages.append({"role": "user", "content": "请根据上述推理提供最终答案"})
    else:
        messages.append({"role": "user", "content": "Please provide the final answer based on your reasoning above."})
    
    logger.info("Generating final answer in generate_task_response function")
    start_time = time.time()
    try:
        final_data = make_reasoning_call(messages, 200, is_final_answer=True)
    except Exception as e:
        logger.error(f"Exception occurred in generate_task_response function while generating final answer: {str(e)}")
        raise e
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time
    
    logger.info("Completed generate_task_response function")
    yield f"Final Answer: {final_data['title']}", final_data['content'], thinking_time, total_thinking_time
