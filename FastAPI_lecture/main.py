# (사용자 생성, 사용자 목록조회, 사용자 수정, 사용자 삭제) 
# --> API서버를 FastAPI를 통해서 만들고자 함!

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="FastAPI 입문",
              description="Sveltekit 프론트엔드와 연결할 사용자 관리 API 서버 앱",
              version="0.1.0")

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
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "id"   : user_id,
        "name" : f"user_{user_id}",
        "email": f"user{user_id}@example.com",
        "age"  : user_id + 20
    }

# Query parameter
# 보통 목록조회, 검색, 필터링, 페이지네이션 등등
# Query(defaul값, ge=최소값, le=최대값)
@app.get("/users")
def get_users(
    limit: int = Query(10, ge=1, le=100),
    skip : int = Query(0, ge=0),
    name : str | None = None
):
    users = []

    for i in range(1, 21):
        users.append({
            "id"   : i,
            "name" : f"user_{i}",
            "email": f"user{i}@example.com",
            "age"  : 20 + i
        })

    if name:
        users = [
            user for user in users if name.lower() in user["name"].lower()
        ]

    return {
        "users": users[skip : skip + limit],
        "limit": limit,
        "skip" : skip,
        "total": len(users)
    }


# POST 요청 / Pydantic
# 데이터 생성시에 보통 POST 요청을 사용함!
# POST 요청에서는 보통 Request Body에 JSON 데이터를 담아서 보냄

# pydantic 모델 추가
class UserCreate(BaseModel):
    name : str
    email: str
    age  : int | None = None

# 실제 User를 만드는 API를 만들어 보자 (POST)

users_db = []
user_id_counter = 1

@app.post("/users")
def create_user(user: UserCreate):
    global user_id_counter

    new_user = {
        'id'   : user_id_counter,
        'name' : user.name,
        'email': user.email,
        'age'  : user.age 
    }

    users_db.append(new_user)
    user_id_counter += 1

    return {
        'message': '사용자 생성 완료',
        'user'   : new_user
    }