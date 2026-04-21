from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")
conn.commit()

class User(BaseModel):
    username:str
    password:str

@app.get("/")
def home():
    return {"msg":"服务器运行成功"}

@app.post("/register")
def register(user:User):

    cur.execute("SELECT * FROM users WHERE username=?",(user.username,))
    old = cur.fetchone()

    if old:
        return {"msg":"账号已存在"}

    cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (user.username,user.password)
    )
    conn.commit()

    return {"msg":"注册成功"}

@app.post("/login")
def login(user:User):

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (user.username,user.password)
    )

    row = cur.fetchone()

    if row:
        return {"msg":"登录成功"}
    else:
        return {"msg":"账号密码错误"}
