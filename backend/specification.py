import threading
import time
from typing import List

from flask import Flask, abort, jsonify, make_response, request
from flask_cors import CORS

from ollama_api import generate_response
from vllm_api import generate_code_from_task

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 临时使用数组来保存 CoT 的数据，前端采用轮询的方式来获取。后续应采用长连接来推送到前端
task_list = []
code_plans = []

def generate_task(user_query: str):    
    global task_list
    if not user_query:
        print("未获取到参数 user_query")
        return
    
    # for steps, total_thinking_time in generate_response(user_query):
    #     for i, (title, content, thinking_time) in enumerate(steps):
    for title, content, thinking_time, total_thinking_time in generate_response(user_query):
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
            print(f"生成了 Final Answer: {task}")
        else:
            task = {
                "id": time.time(),
                "title": title, 
                "content": content, 
                "thinking_time": thinking_time,
                "is_final_answer": False
                }
            task_list.append(task)
            print(f"生成了 Task: {task}")
            # yield task
        
        # Only show total time when it's available at the end
        # if total_thinking_time is not None:
        #     time_container.markdown(f"**Total thinking time: {total_thinking_time:.2f} seconds**")


@app.route("/api/specifications", methods=['POST'])
async def post_specifications():
    global task_list
    args = request.get_json()
    requirement = args.get('requirement')
    is_first_query = args.get('isFirstQuery')
    if is_first_query:
        if requirement:
            print(f"获取到参数 requirement: {requirement}")
            task_list = []
            threading.Thread(target=generate_task, args=(requirement,)).start()
            time.sleep(10)
            return make_response(jsonify({"data": task_list}), 200)
        else:
            return make_response(jsonify("未获取到参数"), 200)
    else:
        return make_response(jsonify({"data": task_list}), 200)
    # for first_task in generate_task(requirement):
    #     return make_response(jsonify({"data": [first_task]}), 200)



def generate_code_plan(origin_requirement: str, task_details: List[str]):    
    global code_plans
    if not task_details:
        print("未获取到参数 task_details")
        return
    
    for file_name, content, is_last_file in generate_code_from_task(origin_requirement, task_details):
        code_plan = {
            "fileName": file_name, 
            "content": content, 
            "isLastFile": is_last_file,
            }
        code_plans.append(code_plan)
        print(f"生成了 code_plan: {code_plan}")


@app.route("/api/codePlan", methods=['POST'])
async def post_codePlan():
    global code_plans
    args = request.get_json()
    origin_requirement = args.get('originRequirement')
    task_details = args.get('taskDetails')
    is_first_query = args.get('isFirstQuery')
    if is_first_query:
        print(f"获取到参数 task_details: {task_details}")
        code_plans = []
        threading.Thread(target=generate_code_plan, args=(origin_requirement, task_details,)).start()
        time.sleep(10)
        return make_response(jsonify({"data": code_plans}), 200)
    else:
        return make_response(jsonify({"data": code_plans}), 200)


if __name__ == "__main__":
    app.run()