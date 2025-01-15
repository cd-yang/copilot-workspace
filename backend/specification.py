import time

from flask import Flask, abort, jsonify, make_response, request
from flask_cors import CORS

from ollama_api import generate_response

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 临时使用数组来保存 CoT 的数据，前端采用轮询的方式来获取。后续应采用长连接来推送到前端
task_list = []

def generate_task(user_query: str):    
    if user_query:
        for steps, total_thinking_time in generate_response(user_query):
                for i, (title, content, thinking_time) in enumerate(steps):
                    if title.startswith("Final Answer"):
                        task_list.append({
                            "id": time.time(),
                            "title": title, 
                            "content": content, 
                            "thinking_time": thinking_time,
                            "total_thinking_time": total_thinking_time,
                            "is_final_answer": True
                            })
                    else:
                        task = {
                            "id": time.time(),
                            "title": title, 
                            "content": content, 
                            "thinking_time": thinking_time,
                            "is_final_answer": False
                            }
                        task_list.append(task)
                        yield task
            
            # Only show total time when it's available at the end
            # if total_thinking_time is not None:
            #     time_container.markdown(f"**Total thinking time: {total_thinking_time:.2f} seconds**")


@app.route("/api/specifications", methods=['POST'])
async def post_specifications():
    requirement = request.get_json().get('requirement')
    if not requirement:
        return make_response(jsonify("未获取到参数"), 200)
    
    for first_task in generate_task(requirement):
        return make_response(jsonify({"data": [first_task]}), 200)
    


if __name__ == "__main__":
    app.run()