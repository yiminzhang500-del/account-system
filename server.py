# -*- coding: utf-8 -*-
from flask import Flask, send_from_directory, request, jsonify
import os
import json
from datetime import datetime

# 初始化 Flask
app = Flask(__name__)

# ====================== 配置 ======================
# 数据存储文件
DATA_FILE = "data.json"
# 管理员账号密码（可自己修改）
ADMIN_USER = "ADMIN"
ADMIN_PWD = "123456"

# ================ 初始化数据文件 ================
def init_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "expense": [],
            "income": [],
            "users": []
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

init_data()

# ====================== 页面路由 ======================
@app.route('/')
def index():
    return send_from_directory(os.getcwd(), "index.html")

# ====================== 登录接口 ======================
@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        username = data.get("username", "")
        password = data.get("password", "")

        if username == ADMIN_USER and password == ADMIN_PWD:
            return jsonify({"code": 0, "msg": "登录成功", "isAdmin": True})
        else:
            return jsonify({"code": -1, "msg": "账号或密码错误"})
    except:
        return jsonify({"code": -1, "msg": "参数错误"})

# ====================== 提交报销 ======================
@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    data = load_data()
    req = request.get_json()
    exp = {
        "type": "expense",
        "报销人员": req.get("person"),
        "金额": float(req.get("money")),
        "备注": req.get("remark"),
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["expense"].append(exp)
    save_data(data)
    return jsonify({"code": 0, "msg": "保存成功"})

# ====================== 提交收入 ======================
@app.route('/api/add_income', methods=['POST'])
def add_income():
    data = load_data()
    req = request.get_json()
    inc = {
        "type": "income",
        "来源": req.get("person"),
        "金额": float(req.get("money")),
        "方式": req.get("type"),
        "备注": req.get("remark"),
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["income"].append(inc)
    save_data(data)
    return jsonify({"code": 0, "msg": "保存成功"})

# ====================== 获取所有数据 ======================
@app.route('/api/get_all', methods=['POST'])
def get_all():
    data = load_data()
    return jsonify({
        "code": 0,
        "expense": data["expense"],
        "income": data["income"]
    })

# ====================== 启动服务 ======================
if __name__ == '__main__':
    # 监听 0.0.0.0:5000 外网可访问
    app.run(host="0.0.0.0", port=5000, debug=False)
