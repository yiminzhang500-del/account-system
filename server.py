from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import datetime

app = FastAPI()

conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

# =========================
# 用户表
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
phone TEXT UNIQUE,
currency TEXT,
role TEXT,
status TEXT,
can_export INTEGER,
can_delete INTEGER,
create_time TEXT
)
""")

# =========================
# 注册申请表
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS register_requests(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT,
phone TEXT,
currency TEXT,
time TEXT
)
""")

# =========================
# 账目表
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS records(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
person TEXT,
type TEXT,
money TEXT,
remark TEXT,
date TEXT,
image TEXT
)
""")

# =========================
# 日志表
# =========================
cur.execute("""
CREATE TABLE IF NOT EXISTS logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
action TEXT,
time TEXT
)
""")

conn.commit()

# =========================
# 默认管理员账号
# =========================
cur.execute("SELECT * FROM users WHERE username='admin'")
row = cur.fetchone()

if not row:
    cur.execute("""
    INSERT INTO users(
    username,password,phone,currency,role,status,
    can_export,can_delete,create_time
    ) VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        "admin",
        "123456",
        "0000000000",
        "AED",
        "admin",
        "active",
        1,
        1,
        str(datetime.datetime.now())
    ))
    conn.commit()


# =========================
# 数据模型
# =========================
class RegisterModel(BaseModel):
    username:str
    password:str
    phone:str
    currency:str

class LoginModel(BaseModel):
    username:str
    password:str

class RecordModel(BaseModel):
    username:str
    person:str
    type:str
    money:str
    remark:str
    date:str
    image:str=""

class AdminModel(BaseModel):
    admin:str
    password:str


# =========================
# 首页
# =========================
@app.get("/")
def home():
    return {"msg":"服务器运行成功"}


# =========================
# 注册申请
# =========================
@app.post("/register")
def register(data:RegisterModel):

    cur.execute(
        "SELECT * FROM users WHERE username=?",
        (data.username,)
    )

    if cur.fetchone():
        return {"msg":"用户名已存在"}

    cur.execute(
        "SELECT * FROM register_requests WHERE username=?",
        (data.username,)
    )

    if cur.fetchone():
        return {"msg":"已提交审核"}

    cur.execute("""
    INSERT INTO register_requests(
    username,password,phone,currency,time
    ) VALUES(?,?,?,?,?)
    """,(
        data.username,
        data.password,
        data.phone,
        data.currency,
        str(datetime.datetime.now())
    ))

    conn.commit()

    return {"msg":"注册申请已提交，等待管理员审核"}


# =========================
# 登录
# =========================
@app.post("/login")
def login(data:LoginModel):

    cur.execute("""
    SELECT * FROM users
    WHERE username=? AND password=?
    """,(
        data.username,
        data.password
    ))

    row = cur.fetchone()

    if not row:
        return {"msg":"账号密码错误"}

    if row[6] != "active":
        return {"msg":"账号已被限制登录"}

    cur.execute("""
    INSERT INTO logs(username,action,time)
    VALUES(?,?,?)
    """,(
        data.username,
        "登录系统",
        str(datetime.datetime.now())
    ))
    conn.commit()

    return {
        "msg":"登录成功",
        "role":row[5],
        "currency":row[4]
    }


# =========================
# 添加记录
# =========================
@app.post("/add_record")
def add_record(data:RecordModel):

    cur.execute("""
    INSERT INTO records(
    username,person,type,money,remark,date,image
    ) VALUES(?,?,?,?,?,?,?)
    """,(
        data.username,
        data.person,
        data.type,
        data.money,
        data.remark,
        data.date,
        data.image
    ))

    cur.execute("""
    INSERT INTO logs(username,action,time)
    VALUES(?,?,?)
    """,(
        data.username,
        "新增记录",
        str(datetime.datetime.now())
    ))

    conn.commit()

    return {"msg":"添加成功"}


# =========================
# 查看个人记录
# =========================
@app.get("/get_records")
def get_records(username:str):

    cur.execute("""
    SELECT * FROM records
    WHERE username=?
    ORDER BY id DESC
    """,(username,))

    rows = cur.fetchall()

    arr = []

    for r in rows:
        arr.append({
            "id":r[0],
            "username":r[1],
            "person":r[2],
            "type":r[3],
            "money":r[4],
            "remark":r[5],
            "date":r[6],
            "image":r[7]
        })

    return arr


# =========================
# 管理员查看注册申请
# =========================
@app.get("/admin_requests")
def admin_requests():

    cur.execute("""
    SELECT * FROM register_requests
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    arr=[]

    for r in rows:
        arr.append({
            "id":r[0],
            "username":r[1],
            "phone":r[3],
            "currency":r[4],
            "time":r[5]
        })

    return arr


# =========================
# 管理员审核通过
# =========================
@app.get("/approve")
def approve(id:int):

    cur.execute(
        "SELECT * FROM register_requests WHERE id=?",
        (id,)
    )

    row = cur.fetchone()

    if not row:
        return {"msg":"申请不存在"}

    cur.execute("""
    INSERT INTO users(
    username,password,phone,currency,
    role,status,can_export,can_delete,create_time
    ) VALUES(?,?,?,?,?,?,?,?,?)
    """,(
        row[1],
        row[2],
        row[3],
        row[4],
        "user",
        "active",
        1,
        0,
        str(datetime.datetime.now())
    ))

    cur.execute(
        "DELETE FROM register_requests WHERE id=?",
        (id,)
    )

    conn.commit()

    return {"msg":"审核通过"}


# =========================
# 管理员禁用账号
# =========================
@app.get("/ban_user")
def ban_user(username:str):

    if username=="admin":
        return {"msg":"管理员不可禁用"}

    cur.execute("""
    UPDATE users
    SET status='ban'
    WHERE username=?
    """,(username,))

    conn.commit()

    return {"msg":"已禁用用户"}


# =========================
# 管理员查看日志
# =========================
@app.get("/logs")
def get_logs():

    cur.execute("""
    SELECT * FROM logs
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    arr=[]

    for r in rows:
        arr.append({
            "username":r[1],
            "action":r[2],
            "time":r[3]
        })

    return arr
