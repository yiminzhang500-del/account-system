from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# ================= 数据库 =================
conn = sqlite3.connect("data.db", check_same_thread=False)
cur = conn.cursor()

# 用户表
cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT,
phone TEXT,
status TEXT DEFAULT '正常',
role TEXT DEFAULT 'user'
)
""")

# 记录表
cur.execute("""
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

# 默认管理员
cur.execute("SELECT * FROM users WHERE username='admin'")
if cur.fetchone() is None:
    cur.execute("""
    INSERT INTO users(username,password,phone,status,role)
    VALUES('admin','123456','0000000000','正常','admin')
    """)
    conn.commit()


# ================= 数据模型 =================
class User(BaseModel):
    username:str
    password:str

class RegisterModel(BaseModel):
    username:str
    password:str
    phone:str

class RecordModel(BaseModel):
    username:str
    person:str
    type:str
    money:str
    remark:str
    date:str


# ================= 首页 =================
@app.get("/")
def home():
    return {"msg":"server ok"}


# ================= 注册 =================
@app.post("/register")
def register(data:RegisterModel):

    try:
        cur.execute("""
        INSERT INTO users(username,password,phone)
        VALUES(?,?,?)
        """,(data.username,data.password,data.phone))

        conn.commit()

        return {"msg":"注册成功"}

    except:
        return {"msg":"账号已存在"}


# ================= 登录 =================
@app.post("/login")
def login(data:User):

    cur.execute("""
    SELECT status,role FROM users
    WHERE username=? AND password=?
    """,(data.username,data.password))

    row = cur.fetchone()

    if row is None:
        return {"msg":"账号密码错误"}

    if row[0] == "禁用" and row[1] != "admin":
        return {"msg":"账号已被禁用"}

    return {
        "msg":"登录成功",
        "role":row[1]
    }


# ================= 添加记录 =================
@app.post("/add_record")
def add_record(data:RecordModel):

    try:
        cur.execute("""
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

    except Exception as e:
        return {"msg":str(e)}


# ================= 获取个人记录 =================
@app.get("/get_records")
def get_records(username:str):

    cur.execute("""
    SELECT * FROM records
    WHERE username=?
    ORDER BY id DESC
    """,(username,))

    rows = cur.fetchall()

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


# ================= 管理员：全部用户 =================
@app.get("/admin_users")
def admin_users():

    cur.execute("""
    SELECT id,username,phone,status,role
    FROM users
    ORDER BY id DESC
    """)

    rows = cur.fetchall()

    arr = []

    for row in rows:
        arr.append({
            "id":row[0],
            "username":row[1],
            "phone":row[2],
            "status":row[3],
            "role":row[4]
        })

    return arr


# ================= 管理员：禁用用户 =================
@app.get("/ban_user")
def ban_user(username:str):

    cur.execute("""
    UPDATE users
    SET status='禁用'
    WHERE username=?
    AND role!='admin'
    """,(username,))

    conn.commit()

    return {"msg":"已禁用"}


# ================= 管理员：恢复用户 =================
@app.get("/open_user")
def open_user(username:str):

    cur.execute("""
    UPDATE users
    SET status='正常'
    WHERE username=?
    """,(username,))

    conn.commit()

    return {"msg":"已恢复"}


# ================= 管理员：删除记录 =================
@app.get("/delete_record")
def delete_record(id:int):

    cur.execute("""
    DELETE FROM records
    WHERE id=?
    """,(id,))

    conn.commit()

    return {"msg":"删除成功"}
