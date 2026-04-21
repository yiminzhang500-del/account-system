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
password TEXT,
currency TEXT DEFAULT 'CNY',
role TEXT DEFAULT 'user'
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

# 自动创建管理员账号
cursor.execute("""
INSERT OR IGNORE INTO users
(username,password,currency,role)
VALUES
('admin','123456','CNY','admin')
""")

conn.commit()


# ---------------- 注册 ----------------
class User(BaseModel):
    username:str
    password:str
    currency:str = "CNY"


@app.post("/register")
def register(data:User):

    try:

        cursor.execute(
            """
            INSERT INTO users
            (username,password,currency,role)
            VALUES(?,?,?,?)
            """,
            (
                data.username,
                data.password,
                data.currency,
                "user"
            )
        )

        conn.commit()

        return {"msg":"注册成功"}

    except:

        return {"msg":"账号已存在"}


# ---------------- 登录 ----------------
@app.post("/login")
def login(data:User):

    cursor.execute(
        """
        SELECT role,currency
        FROM users
        WHERE username=? AND password=?
        """,
        (
            data.username,
            data.password
        )
    )

    row = cursor.fetchone()

    if row:

        return {
            "msg":"登录成功",
            "role":row[0],
            "currency":row[1]
        }

    return {"msg":"账号密码错误"}


# ---------------- 新增记录 ----------------
class Record(BaseModel):
    username:str
    person:str
    type:str
    money:str
    remark:str
    date:str


@app.post("/add_record")
def add_record(data:Record):

    cursor.execute(
        """
        INSERT INTO records
        (username,person,type,money,remark,date)
        VALUES(?,?,?,?,?,?)
        """,
        (
            data.username,
            data.person,
            data.type,
            data.money,
            data.remark,
            data.date
        )
    )

    conn.commit()

    return {"msg":"成功"}


# ---------------- 获取记录 ----------------
@app.get("/get_records")
def get_records(username:str):

    cursor.execute(
        """
        SELECT *
        FROM records
        WHERE username=?
        ORDER BY id DESC
        """,
        (username,)
    )

    rows = cursor.fetchall()

    arr = []

    for row in rows:

        arr.append({
            "id":row[0],
            "username":row[1],
            "person":row[2],
            "type":row[3],
            "money":row[4],
            "remark":row[5],
            "date":row[6]
        })

    return arr


# ---------------- 全部用户 ----------------
@app.get("/all_users")
def all_users():

    cursor.execute(
        """
        SELECT username,currency,role
        FROM users
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    arr = []

    for row in rows:

        arr.append({
            "username":row[0],
            "currency":row[1],
            "role":row[2]
        })

    return arr


# ---------------- 删除用户 ----------------
@app.get("/delete_user")
def delete_user(username:str):

    cursor.execute(
        "DELETE FROM users WHERE username=?",
        (username,)
    )

    cursor.execute(
        "DELETE FROM records WHERE username=?",
        (username,)
    )

    conn.commit()

    return {"msg":"删除成功"}


# ---------------- 删除记录 ----------------
@app.get("/delete_record")
def delete_record(id:int):

    cursor.execute(
        "DELETE FROM records WHERE id=?",
        (id,)
    )

    conn.commit()

    return {"msg":"删除成功"}
