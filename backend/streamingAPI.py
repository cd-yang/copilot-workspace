from flask import Flask, Response
import time
import json

app = Flask(__name__)

@app.route("/api/generate", methods=["GET"])
def generate_data():
    def generate():
        data = [
            {"id": 1, "text": "生成数据：第一条"},
            {"id": 2, "text": "生成数据：第二条"},
            {"id": 3, "text": "生成数据：第三条"}
        ]
        for item in data:
            yield f"{json.dumps(item)}\n"  # 每条数据作为一个块返回
            time.sleep(2)  # 模拟大模型生成的延迟
    return Response(generate(), content_type="application/json")

if __name__ == "__main__":
    app.run(debug=True)
