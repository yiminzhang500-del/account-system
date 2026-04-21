from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# 数据库连接
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# 用户表
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# 记录表
cursor.execute("""
CREATE TABLE IF NOT EXISTS records(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
person TEXT,
type TEXT,
money TEXT,
remark TEXT,
date TEXT
)
""")

conn.commit()


# ================= 注册 =================
class User(BaseModel):
    username: str
    password: str


@app.post("/register")
def register(data: User):

    try:

        cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (data.username, data.password)
        )

        conn.commit()

        return {"msg": "注册成功"}

    except:

        return {"msg": "账号已存在"}


# ================= 登录 =================
@app.post("/login")
def login(data: User):

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data.username, data.password)
    )

    row = cursor.fetchone()

    if row:
        return {"msg": "登录成功"}
    else:
        return {"msg": "账号密码错误"}


# ================= 保存记录 =================
class Record(BaseModel):
    username: str
    person: str
    type: str
    money: str
    remark: str
    date: str


# 安卓端调用的是 /add_record
@app.post("/add_record")
def add_record(data: Record):

    try:

        cursor.execute("""
        INSERT INTO records(
        username,person,type,money,remark,date
        ) VALUES(?,?,?,?,?,?)
        """, (
            data.username,
            data.person,
            data.type,
            data.money,
            data.remark,
            data.date
        ))

        conn.commit()

        return {"msg": "成功"}

    except Exception as e:

        return {"msg": str(e)}


# 兼容旧版本接口 /save_record
@app.post("/save_record")
def save_record(data: Record):
    return add_record(data)


# ================= 获取记录 =================
@app.get("/get_records")
def get_records(username: str):

    cursor.execute(
        "SELECT * FROM records WHERE username=? ORDER BY id DESC",
        (username,)
    )

    rows = cursor.fetchall()

    arr = []

    for row in rows:

        arr.append({
            "id": row[0],
            "username": row[1],
            "person": row[2],
            "type": row[3],
            "money": row[4],
            "remark": row[5],
            "date": row[6]
        })

    return arr


# ================= 首页测试 =================
@app.get("/")
def home():
    return {"msg": "server ok"}
