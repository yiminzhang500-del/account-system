# server.py
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

# ===============================
# 数据库连接
# ===============================
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# ===============================
# 用户表（企业授权版）
# ===============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
currency TEXT DEFAULT 'CNY',
role TEXT DEFAULT 'user',
approved INTEGER DEFAULT 0,
enabled INTEGER DEFAULT 1,
expire_date TEXT DEFAULT '',
device_id TEXT DEFAULT '',
create_time TEXT DEFAULT '',
last_login TEXT DEFAULT ''
)
""")

# ===============================
# 记录表
# ===============================
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

# ===============================
# 默认管理员账号
# admin / 123456
# ===============================
cursor.execute("""
INSERT OR IGNORE INTO users
(username,password,currency,role,approved,enabled,create_time)
VALUES
('admin','123456','CNY','admin',1,1,datetime('now'))
""")
conn.commit()

# ===============================
# 数据模型
# ===============================
class User(BaseModel):
    username:str
    password:str
    currency:str="CNY"

class Record(BaseModel):
    username:str
    person:str
    type:str
    money:str
    remark:str
    date:str

# ===============================
# 注册申请
# ===============================
@app.post("/register")
def register(data:User):

    try:
        cursor.execute("""
        INSERT INTO users
        (username,password,currency,role,approved,enabled,create_time)
        VALUES(?,?,?,?,?,?,?)
        """,(
            data.username,
            data.password,
            data.currency,
            "user",
            0,
            1,
            str(datetime.now())[:19]
        ))

        conn.commit()

        return {"msg":"注册申请已提交，等待管理员审核"}

    except:
        return {"msg":"账号已存在"}

# ===============================
# 登录
# ===============================
@app.post("/login")
def login(data:User):

    cursor.execute("""
    SELECT role,currency,approved,enabled,expire_date
    FROM users
    WHERE username=? AND password=?
    """,(
        data.username,
        data.password
    ))

    row = cursor.fetchone()

    if not row:
        return {"msg":"账号密码错误"}

    role = row[0]
    currency = row[1]
    approved = row[2]
    enabled = row[3]
    expire_date = row[4]

    if approved == 0:
        return {"msg":"账号待审核"}

    if enabled == 0:
        return {"msg":"账号已禁用"}

    if expire_date != "":
        try:
            today = datetime.now().date()
            exp = datetime.strptime(
                expire_date,
                "%Y-%m-%d"
            ).date()

            if today > exp:
                return {"msg":"账号已到期"}

        except:
            pass

    cursor.execute("""
    UPDATE users
    SET last_login=?
    WHERE username=?
    """,(
        str(datetime.now())[:19],
        data.username
    ))

    conn.commit()

    return {
        "msg":"登录成功",
        "role":role,
        "currency":currency
    }

# ===============================
# 新增记录
# ===============================
@app.post("/add_record")
def add_record(data:Record):

    cursor.execute("""
    INSERT INTO records
    (username,person,type,money,remark,date)
    VALUES(?,?,?,?,?,?)
    """,(
        data.username,
        data.person,
        data.type,
        data.money,
        data.remark,
        data.date
    ))

    conn.commit()

    return {"msg":"成功"}

# ===============================
# 获取记录
# ===============================
@app.get("/get_records")
def get_records(username:str):

    cursor.execute("""
    SELECT * FROM records
    WHERE username=?
    ORDER BY id DESC
    """,(username,))

    rows = cursor.fetchall()

    arr = []

    for r in rows:
        arr.append({
            "id":r[0],
            "username":r[1],
            "person":r[2],
            "type":r[3],
            "money":r[4],
            "remark":r[5],
            "date":r[6]
        })

    return arr

# ===============================
# 删除单条记录
# ===============================
@app.get("/delete_record")
def delete_record(id:int):

    cursor.execute(
        "DELETE FROM records WHERE id=?",
        (id,)
    )

    conn.commit()

    return {"msg":"删除成功"}

# ===============================
# 全部用户
# ===============================
@app.get("/all_users")
def all_users():

    cursor.execute("""
    SELECT username,currency,role,
    approved,enabled,expire_date,
    create_time,last_login
    FROM users
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    arr = []

    for r in rows:
        arr.append({
            "username":r[0],
            "currency":r[1],
            "role":r[2],
            "approved":r[3],
            "enabled":r[4],
            "expire_date":r[5],
            "create_time":r[6],
            "last_login":r[7]
        })

    return arr

# ===============================
# 审核通过用户
# ===============================
@app.get("/approve_user")
def approve_user(username:str):

    cursor.execute("""
    UPDATE users
    SET approved=1
    WHERE username=?
    """,(username,))

    conn.commit()

    return {"msg":"审核成功"}

# ===============================
# 禁用/启用用户
# ===============================
@app.get("/toggle_user")
def toggle_user(username:str):

    cursor.execute("""
    SELECT enabled FROM users
    WHERE username=?
    """,(username,))

    row = cursor.fetchone()

    val = 1

    if row[0] == 1:
        val = 0

    cursor.execute("""
    UPDATE users
    SET enabled=?
    WHERE username=?
    """,(val,username))

    conn.commit()

    return {"msg":"操作成功"}

# ===============================
# 删除用户
# ===============================
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
