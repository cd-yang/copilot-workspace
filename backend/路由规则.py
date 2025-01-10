from flask import Flask
app = Flask(__name__)

# 使用 route() 装饰器来把函数绑定到 URL:
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/hi", methods=['GET', 'POST'])
def hi():
    return "<p>Hi!</p>"

#post请求直接键入访问不到
@app.route("/haha", methods=['POST'])
def ha():
    return "<p>Hahahaha!</p>"

@app.route("/user/<int:id>")
def user(id):
   if id == 1:
       return 'python'
   if id == 2:
       return 'java'
   return 'No User'

if __name__ == "__main__":
 app.run()