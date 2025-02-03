import datetime
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from collections import defaultdict

from utils.token import create_jwt, is_token_valid
from models.user import User, UserRegisterRequest, UserLoginRequest

app = FastAPI()

users = defaultdict(list)


# TODO: Add validation for the given data
@app.post("/register")
async def register_user(request: UserRegisterRequest):
    users[request.user_id] = User(
        user_id=request.user_id,
        name=request.user_name,
        password=request.user_password,
        bio=request.user_bio,
        archtype=request.user_archtype,
    )
    return JSONResponse(
        content={
            "message": "The user was successfully registered.",
            "user_id": request.user_id,
        },
        status_code=201,
    )


@app.post("/login")
async def login_user(request: UserLoginRequest):
    for _, user in users.items():
        if user.name == request.user_name and user.password == request.user_password:
            return JSONResponse(
                content={
                    "message": "User logged in.",
                    "token": create_jwt(
                        {
                            "user_id": user.user_id,
                            "name": user.name,
                            "iat": datetime.datetime.now(),
                        }
                    ),
                },
                status_code=200,
            )
    else:
        return JSONResponse(
            content={"message": "Couldn't log the user in."}, status_code=400
        )


@app.post("/validate")
async def validate_token(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[-1] if len(auth_header) else ""
    if is_token_valid(token):
        return JSONResponse(content={"message": "Token is valid."}, status_code=200)
    return JSONResponse(content={"message": "Token is invalid."}, status_code=200)


@app.get("/user/{user_id}")
async def get_user_info(user_id: str):
    pass


@app.delete("/user/{user_id}")
async def delete_user(user_id: str):
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
