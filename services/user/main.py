import os
import datetime
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from utils.token import create_jwt, is_token_valid
from models.user import UserRegisterRequest, UserLoginRequest, UserTokenValidation
from models.db import Users, pwd_context
from repository.db import get_db, Base, engine

app = FastAPI(docs_url="/user/docs", openapi_url="/user/openapi.json")

# --- Prometheus Metrics ---
REQUEST_COUNT = Counter(
    "request_count",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
)


# --- Middleware for Request Counting ---
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    # Increment the counter with the method, path, and response status code.
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        http_status=response.status_code,
    ).inc()
    return response


# --- Metrics Endpoint for Prometheus ---
@app.get("/metrics")
async def metrics():
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


@app.get("/user/status")
async def status():
    return JSONResponse(content={"message": "healthy"}, status_code=200)


@app.post("/register")
async def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = db.query(Users).filter(Users.user_id == request.user_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    new_user = Users(
        user_id=request.user_id,
        name=request.user_name,
        password=request.user_password,
        bio=request.user_bio,
        archtype=request.user_archtype,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return JSONResponse(
        content={
            "message": "The user was successfully registered.",
            "user_id": new_user.user_id,
        },
        status_code=201,
    )
    # users[request.user_id] = User(
    #     user_id=request.user_id,
    #     name=request.user_name,
    #     password=request.user_password,
    #     bio=request.user_bio,
    #     archtype=request.user_archtype,
    # )
    # return JSONResponse(
    #     content={
    #         "message": "The user was successfully registered.",
    #         "user_id": request.user_id,
    #     },
    #     status_code=201,
    # )


@app.post("/login")
async def login_user(request: UserLoginRequest, db: Session = Depends(get_db)):
    # Find the user by name
    user = db.query(Users).filter(Users.name == request.user_name).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Verify the provided password against the stored hashed password
    if not pwd_context.verify(request.user_password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Create a JWT token (using a timestamp for 'iat')
    token = create_jwt(
        {
            "user_id": user.user_id,
            "name": user.name,
            "iat": datetime.datetime.now().timestamp(),
        }
    )
    return JSONResponse(
        content={
            "message": "User logged in.",
            "token": token,
        },
        status_code=200,
    )
    # for _, user in users.items():
    #     if user.name == request.user_name and user.password == request.user_password:
    #         return JSONResponse(
    #             content={
    #                 "message": "User logged in.",
    #                 "token": create_jwt(
    #                     {
    #                         "user_id": user.user_id,
    #                         "name": user.name,
    #                         "iat": datetime.datetime.now(),
    #                     }
    #                 ),
    #             },
    #             status_code=200,
    #         )
    # else:
    #     return JSONResponse(
    #         content={"message": "Couldn't log the user in."}, status_code=400
    #     )


@app.post("/validate")
async def validate_token(request: UserTokenValidation):
    token = request.user_token
    if is_token_valid(token):
        return JSONResponse(content={"message": "Token is valid."}, status_code=200)
    return JSONResponse(content={"message": "Token is invalid."}, status_code=200)


@app.get("/user/{user_id}")
async def get_user_info(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Manually convert the SQLAlchemy model to a dictionary (or use a Pydantic model)
    user_data = {
        "user_id": user.user_id,
        "name": user.name,
        "bio": user.bio,
        "archtype": user.archtype,
    }
    return JSONResponse(
        content={
            "message": "Successfully returned the user data.",
            "user": user_data,
        },
        status_code=200,
    )
    # return JSONResponse(
    #     content={
    #         "message": "Succsesfully returned the user data.",
    #         "user": users[user_id].model_dump(),
    #     },
    #     status_code=200,
    # )


@app.delete("/user/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return JSONResponse(
        content={"message": "User deleted successfully."},
        status_code=200,
    )
    # del users[user_id]
    # return JSONResponse(
    #     content={"message": "User deleted succsesfully."}, status_code=200
    # )


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 8002))
