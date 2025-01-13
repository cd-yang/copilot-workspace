from flask import Flask,make_response,jsonify,request,abort
from flask_cors import CORS
app = Flask(__name__)


app.config['JSON_AS_ASCII'] = False

@app.route("/api/hi", methods=['GET', 'POST'])
def hi():
    return "<p>Hi!</p>"

@app.route("/api/specifications", methods=['GET'])
def get_specifications():
    if request.args.get('issue'):
        data = {
            'data':
                  [
                {
                    "id": 1,
                    "content": "建议一：优化登录界面设计",
                    'title': '登录界面'
                },
                {
                    "id": 2,
                    "content": "建议二：改进用户权限管理",
                    'title': '用户权限'
                },
                {
                    "id": 3,
                    "content": "建议三：实现实时数据监控",
                    'title': '数据监控'
                },
                {
                    "id": 4,
                    "content": "建议四：实现实时数据监控",
                    'title': '数据监控'
                },
                {
                    "id": 5,
                    "content": "建议五：实现实时数据监控",
                    'title': '数据监控'
                }
            ]
            }
        return make_response(jsonify(data), 200)

    else:
        abort(404)
    
    


if __name__ == "__main__":
    app.run()