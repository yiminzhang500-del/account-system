from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

# 用户表
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# 账目表
cur.execute("""
CREATE TABLE IF NOT EXISTS records(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
type TEXT,
money TEXT,
remark TEXT,
date TEXT,
currency TEXT
)
""")

conn.commit()


# 模型
class User(BaseModel):
    username:str
    password:str

class Record(BaseModel):
    username:str
    type:str
    money:str
    remark:str
    date:str
    currency:str

class DeleteModel(BaseModel):
    id:int


@app.get("/")
def home():
    return {"msg":"服务器运行成功"}


# 注册
@app.post("/register")
def register(user:User):

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        (user.username,)
    )

    if cur.fetchone():
        return {"msg":"账号已存在"}

    cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (user.username,user.password)
    )

    conn.commit()

    return {"msg":"注册成功"}


# 登录
@app.post("/login")
def login(user:User):

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user.username,user.password)
    )

    if cur.fetchone():
        return {"msg":"登录成功"}

    return {"msg":"账号密码错误"}


# 添加账目
@app.post("/add_record")
def add_record(r:Record):

    cur.execute("""
    INSERT INTO records(
    username,type,money,remark,date,currency
    ) VALUES(?,?,?,?,?,?)
    """,(
        r.username,
        r.type,
        r.money,
        r.remark,
        r.date,
        r.currency
    ))

    conn.commit()

    return {"msg":"保存成功"}


# 获取账目（换机恢复）
@app.get("/get_records")
def get_records(username:str):

    cur.execute(
        "SELECT * FROM records WHERE username=? ORDER BY id DESC",
        (username,)
    )

    rows = cur.fetchall()

    arr = []

    for row in rows:
        arr.append({
            "id":row[0],
            "username":row[1],
            "type":row[2],
            "money":row[3],
            "remark":row[4],
            "date":row[5],
            "currency":row[6]
        })

    return arr


# 删除单条账目
@app.post("/delete_record")
def delete_record(d:DeleteModel):

    cur.execute(
        "DELETE FROM records WHERE id=?",
        (d.id,)
    )

    conn.commit()

    return {"msg":"删除成功"}


# 清空某用户数据
@app.get("/clear_records")
def clear_records(username:str):

    cur.execute(
        "DELETE FROM records WHERE username=?",
        (username,)
    )

    conn.commit()

    return {"msg":"已清空"}
