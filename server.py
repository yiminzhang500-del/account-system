from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

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


class User(BaseModel):
    username: str
    password: str


class Record(BaseModel):
    username: str
    type: str
    money: str
    remark: str
    date: str
    currency: str


@app.get("/")
def home():
    return {"msg": "server ok"}


@app.post("/register")
def register(user: User):
    try:
        cur.execute(
            "insert into users(username,password) values(?,?)",
            (user.username, user.password)
        )
        conn.commit()
        return {"msg": "注册成功"}
    except:
        return {"msg": "账号已存在"}


@app.post("/login")
def login(user: User):
    cur.execute(
        "select * from users where username=? and password=?",
        (user.username, user.password)
    )
    data = cur.fetchone()

    if data:
        return {"msg": "登录成功"}
    else:
        return {"msg": "账号密码错误"}


@app.post("/add_record")
def add_record(r: Record):
    cur.execute("""
    insert into records(username,type,money,remark,date,currency)
    values(?,?,?,?,?,?)
    """, (
        r.username,
        r.type,
        r.money,
        r.remark,
        r.date,
        r.currency
    ))
    conn.commit()
    return {"msg": "成功"}


@app.get("/get_records")
def get_records(username: str):
    cur.execute(
        "select id,type,money,remark,date,currency from records where username=? order by id desc",
        (username,)
    )

    rows = cur.fetchall()

    arr = []

    for row in rows:
        arr.append({
            "id": row[0],
            "type": row[1],
            "money": row[2],
            "remark": row[3],
            "date": row[4],
            "currency": row[5]
        })

    return arr
