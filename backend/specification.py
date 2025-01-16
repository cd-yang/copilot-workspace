import threading
import time

from flask import Flask, abort, jsonify, make_response, request
from flask_cors import CORS

from ollama_api import generate_response

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 临时使用数组来保存 CoT 的数据，前端采用轮询的方式来获取。后续应采用长连接来推送到前端
task_list = []

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
    
    


if __name__ == "__main__":
    app.run()