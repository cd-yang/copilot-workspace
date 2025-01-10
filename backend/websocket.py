from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域
socketio = SocketIO(app, cors_allowed_origins="*")  # 启用 WebSocket

# 模拟数据库存储规格
specifications_db = [
    {"id": 1, "content": "规格示例 1"},
    {"id": 2, "content": "规格示例 2"}
]

# WebSocket 连接事件
@socketio.on('connect')
def handle_connect():
    print("客户端已连接")
    emit('message', {'data': '连接成功！'}, broadcast=True)

# WebSocket 消息事件
@socketio.on('get_specifications')
def handle_get_specifications(data):
    issue = data.get('issue', '').strip()

    if not issue:
        emit('specifications_response', {"error": "需求不能为空"})
        return

    # 模拟根据需求生成规格
    generated_specs = [
        {"id": len(specifications_db) + i + 1, "content": f"基于需求 '{issue}' 的规格 {i + 1}"}
        for i in range(3)
    ]
    specifications_db.extend(generated_specs)

    emit('specifications_response', {"data": generated_specs}, broadcast=True)

# WebSocket 更新规格事件
@socketio.on('update_specification')
def handle_update_specification(data):
    spec_id = data.get('id')
    new_content = data.get('content', '').strip()

    if not new_content:
        emit('update_response', {"error": "内容不能为空"})
        return

    for spec in specifications_db:
        if spec['id'] == spec_id:
            spec['content'] = new_content
            emit('update_response', {"message": "更新成功", "data": spec}, broadcast=True)
            return

    emit('update_response', {"error": "规格未找到"})

# WebSocket 删除规格事件
@socketio.on('delete_specification')
def handle_delete_specification(data):
    spec_id = data.get('id')

    global specifications_db
    specifications_db = [spec for spec in specifications_db if spec['id'] != spec_id]

    emit('delete_response', {"message": "删除成功"}, broadcast=True)

# WebSocket 新增规格事件
@socketio.on('add_specification')
def handle_add_specification(data):
    content = data.get('content', '').strip()

    if not content:
        emit('add_response', {"error": "内容不能为空"})
        return

    new_spec = {
        "id": max([spec['id'] for spec in specifications_db], default=0) + 1,
        "content": content
    }
    specifications_db.append(new_spec)

    emit('add_response', {"message": "新增成功", "data": new_spec}, broadcast=True)


# WebSocket 断开连接事件
@socketio.on('disconnect')
def handle_disconnect():
    print("客户端已断开连接")


if __name__ == '__main__':
    socketio.run(app, debug=True)
