from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# 创建数据库
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


# ---------------- 注册 ----------------
class User(BaseModel):
    username:str
    password:str

@app.post("/register")
def register(data:User):
    try:
        cursor.execute(
            "insert into users(username,password) values(?,?)",
            (data.username,data.password)
        )
        conn.commit()
        return {"msg":"注册成功"}
    except:
        return {"msg":"账号已存在"}


# ---------------- 登录 ----------------
@app.post("/login")
def login(data:User):

    cursor.execute(
        "select * from users where username=? and password=?",
        (data.username,data.password)
    )

    if cursor.fetchone():
        return {"msg":"登录成功"}
    else:
        return {"msg":"账号密码错误"}


# ---------------- 保存记录 ----------------
class Record(BaseModel):
    username:str
    person:str
    type:str
    money:str
    remark:str
    date:str

@app.post("/save_record")
def save_record(data:Record):

    try:
        cursor.execute("""
        insert into records
        (username,person,type,money,remark,date)
        values(?,?,?,?,?,?)
        """,(
            data.username,
            data.person,
            data.type,
            data.money,
            data.remark,
            data.date
        ))

        conn.commit()

        return {"msg":"保存成功"}

    except Exception as e:
        return {"msg":str(e)}


# ---------------- 获取记录 ----------------
@app.get("/get_records")
def get_records(username:str):

    cursor.execute(
        "select * from records where username=? order by id desc",
        (username,)
    )

    rows = cursor.fetchall()

    data = []

    for row in rows:
        data.append({
            "id":row[0],
            "username":row[1],
            "person":row[2],
            "type":row[3],
            "money":row[4],
            "remark":row[5],
            "date":row[6]
        })

    return data
