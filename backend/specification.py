import threading
import time
import logging
from typing import List

from flask import Flask, jsonify, make_response, request
from loguru import logger

from step_1_task import generate_task_response
from step_2_code_plan import generate_code_from_task

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Configure loguru
logger.add("file_{time}.log", level="INFO", format="{time} - {level} - {message}")

# 临时使用数组来保存 CoT 的数据，前端采用轮询的方式来获取。后续应采用长连接来推送到前端
task_list = []
code_plans = []

def generate_task(user_query: str):    
    global task_list
    logger.info("Starting generate_task function")
    if not user_query:
        logger.error("未获取到参数 user_query")
        return
    
    for title, content, thinking_time, total_thinking_time in generate_task_response(user_query):
        if title.startswith("Final Answer"):
            task = {
                "id": time.time(),
                "title": title, 
                "content": content, 
                "thinking_time": thinking_time,
                "total_thinking_time": total_thinking_time,
                "is_final_answer": True
                }
            task_list.append(task)
            logger.info(f"生成了 Final Answer: {task}")
        else:
            task = {
                "id": time.time(),
                "title": title, 
                "content": content, 
                "thinking_time": thinking_time,
                "is_final_answer": False
                }
            task_list.append(task)
            logger.info(f"生成了 Task: {task}")
    
    logger.info("Ending generate_task function")


@app.route("/api/specifications", methods=['POST'])
async def post_specifications():
    global task_list
    logger.info("Received request for /api/specifications")
    args = request.get_json()
    requirement = args.get('requirement')
    is_first_query = args.get('isFirstQuery')
    if is_first_query:
        if requirement:
            logger.info(f"获取到参数 requirement: {requirement}")
            task_list = []
            threading.Thread(target=generate_task, args=(requirement,)).start()
            time.sleep(10)
            return make_response(jsonify({"data": task_list}), 200)
        else:
            logger.error("未获取到参数")
            return make_response(jsonify("未获取到参数"), 200)
    else:
        return make_response(jsonify({"data": task_list}), 200)


def generate_code_plan(origin_requirement: str, task_details: List[str]):    
    global code_plans
    logger.info("Starting generate_code_plan function")
    if not task_details:
        logger.error("未获取到参数 task_details")
        # return
    
    for code_plan in generate_code_from_task(origin_requirement, task_details):
        code_plans.append(code_plan)
        logger.info(f"生成了 code_plan: {code_plan}")
    
    logger.info("Ending generate_code_plan function")


@app.route("/api/codePlan", methods=['POST'])
async def post_codePlan():
    global code_plans
    logger.info("Received request for /api/codePlan")
    args = request.get_json()
    origin_requirement = args.get('originRequirement')
    task_details = args.get('taskDetails')
    is_first_query = args.get('isFirstQuery')
    if is_first_query:
        logger.info(f"获取到参数 task_details: {task_details}")
        code_plans = []
        threading.Thread(target=generate_code_plan, args=(origin_requirement, task_details,)).start()
        time.sleep(10)
        return make_response(jsonify({"data": code_plans}), 200)
    else:
        return make_response(jsonify({"data": code_plans}), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
