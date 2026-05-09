# (사용자 생성, 사용자 목록조회, 사용자 수정, 사용자 삭제) 
# --> API서버를 FastAPI를 통해서 만들고자 함!

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="FastAPI 입문",
              description="Sveltekit 프론트엔드와 연결할 사용자 관리 API 서버 앱",
              version="0.1.0")

users_db = []
user_id_counter = 1

# uvicorn main:app --reload --host 127.0.0.1 --port 8000
# http://127.0.0.1:8000/docs
# 실행 취소하고 싶으면 ctrl+C

# http://127.0.0.1:8000/
# 위 요청이 왔을 때, 함수 실행
# 기본 응답
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!!!!"}

# 서버 상태 확인
@app.get("/health")
def health_check():
    return {"status": "ok"}

# API 정보 확인
@app.get("/info")
def get_info():
    return {
        "framework": "FastAPI",
        "version"  : "0.1.0",
        "docs_url" : "/docs"
    }

# API 요청에서 값을 전달하는 크게 두가지 방식이 있음!
# 1. Path Parameter: URL 경로 자체에 값이 들어가는 방식
# 2. Query Parameter: URL 뒤에 ? 다음 옵션처럼 값들이 붙는 방식

# 예) 
# user를 조회하는 API를 만들었다고 가정해 봅시다

# url 경로: /users

# path parameter: /users/3 -> 3번 user를 조회
# query parameter: /users?limit=3 -> 사용자 목록을 3개 가져와

# Path parameter
# @app.get("/users/{user_id}")
# def get_user(user_id: int):
#     return {
#         "id"   : user_id,
#         "name" : f"user_{user_id}",
#         "email": f"user{user_id}@example.com",
#         "age"  : user_id + 20
#     }

@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users_db:
        if user['id'] == user_id:
            return {
                'found': True,
                'user' : user
            }
        
    return {
        'found'  : False,
        'message': '사용자를 찾을 수 없습니다'
    }

# Query parameter
# 보통 목록조회, 검색, 필터링, 페이지네이션 등등
# Query(defaul값, ge=최소값, le=최대값)
# @app.get("/users")
# def get_users(
#     limit: int = Query(10, ge=1, le=100),
#     skip : int = Query(0, ge=0),
#     name : str | None = None
# ):
#     users = []

#     for i in range(1, 21):
#         users.append({
#             "id"   : i,
#             "name" : f"user_{i}",
#             "email": f"user{i}@example.com",
#             "age"  : 20 + i
#         })

#     if name:
#         users = [
#             user for user in users if name.lower() in user["name"].lower()
#         ]

#     return {
#         "users": users[skip : skip + limit],
#         "limit": limit,
#         "skip" : skip,
#         "total": len(users)
#     }


# POST 요청 / Pydantic
# 데이터 생성시에 보통 POST 요청을 사용함!
# POST 요청에서는 보통 Request Body에 JSON 데이터를 담아서 보냄

# pydantic 모델 추가
class UserCreate(BaseModel):
    name : str
    email: str
    age  : int | None = None

# 실제 User를 만드는 API를 만들어 보자 (POST)

# @app.post("/users")
# def create_user(user: UserCreate):
#     global user_id_counter

#     new_user = {
#         'id'   : user_id_counter,
#         'name' : user.name,
#         'email': user.email,
#         'age'  : user.age 
#     }

#     users_db.append(new_user)
#     user_id_counter += 1

#     return {
#         'message': '사용자 생성 완료',
#         'user'   : new_user
#     }


# database
# 회원정보등을 database에 저장하는 작업
# RAM (메모리)에 리스트로 회원정보를 넣는게 아니라, 
# sqlite로 db에 (파일로) 회원정보를 저장하고, 관리하는 방식

# CORS 추가
# CORS: 브라우저가 다른 출처(origin)의 서버에 함부로 요청 못 하게 막는 보안 규칙, 그리고 그걸 허용해주는 방법

app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ],
    allow_credentials = True,
    allow_methods     = ['*'],
    allow_headers     = ['*'],
)

# db 경로 지정 (파일)
DB_PATH = 'users.db'

# db 연결 함수
def get_db_connection():
    conn             = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # 조회 결과를 dict처럼 다룰 수 있게 해줌
    # 만약 위 설정이 없다면 결과가 tuple처럼 나옴
    return conn

# db 초기화 함수
def init_database():
    conn   = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER
        )
        '''
    )

    conn.commit()
    conn.close()

# 서버 시작시 db 초기화
@app.on_event('startup')
def start_up():
    init_database()
    print('db init complete')

@app.get('/users')
def get_all_users(
    limit: int = Query(10, ge=1, le=100),
    skip : int = Query(0, ge=0),
    name : str | None = None
):
    conn = get_db_connection()
    cursor = conn.cursor()

    if name:
        cursor.execute(
            '''
            SELECT * FROM users
            WHERE lower(name) LIKE ?
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            ''',
            (f"%{name.lower()}%", limit, skip)
        )
    else:
        cursor.execute(
            '''
            SELECT * FROM users
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            ''',
            (limit, skip)
        )

    users = [dict(row) for row in cursor.fetchall()]    # 검색결과를 모조리 가져와서 python list형태로 반환

    if name:
        cursor.execute(
            'SELECT COUNT(*) AS count FROM users WHERE lower(name) LIKE ?',
            (f"%{name.lower()}%")
        )
    else:
        cursor.execute('SELECT COUNT(*) AS count FROM users')

    total = cursor.fetchone()['count']

    conn.close()

    return {
        'count': total,
        'users': users
    }


# 사용자 생성 API
@app.post('/users')
def create_user(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
            (user.name, user.email, user.age)
        )
        conn.commit()
        user_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="이미 존재하는 이메일입니다."
        )

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    created_user = dict(cursor.fetchone())

    conn.close()

    return {
        "message": "사용자 생성 완료",
        "user": created_user
    }