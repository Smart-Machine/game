import uuid
import uvicorn
import datetime
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from collections import defaultdict

from models.session import Session, SessionRequest

app = FastAPI()

# Dictionary to manage multiple sessions {session_id: list_of_clients}
sessions = defaultdict(list)


@app.get("/status")
async def status():
    return JSONResponse(content={"message": "healthy"}, status_code=200)


@app.get("/session")
async def list_sessions(
    session_id: Optional[str] = None,
    active: Optional[bool] = False,
):
    if session_id and active:
        return JSONResponse(
            content={"message": "Can't filter by both params.", "sessions": dict()},
            status_code=400,
        )
    if session_id:
        return JSONResponse(
            content={"sessions": [sessions[session_id]]}, status_code=200
        )
    if active:
        return JSONResponse(
            content={
                "sessions": {
                    key: session.model_dump()
                    for key, session in sessions.items()
                    if session.active_users
                }
            },
            status_code=200,
        )
    return JSONResponse(
        content={
            "sessions": {key: session.model_dump() for key, session in sessions.items()}
        },
        status_code=200,
    )


@app.post("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = Session(
        session_id=session_id,
        created_at=datetime.datetime.now().timestamp(),
    )
    return JSONResponse(content={"message": "Session created."}, status_code=201)


@app.put("/session")
async def update_session(session: Session):
    response = {}
    if session.session_id not in sessions.keys():
        response = JSONResponse(
            content={"message": "Session didn't exist, so it was created."},
            status_code=400,
        )
    else:
        response = JSONResponse(
            content={"message": "Session updated."}, status_code=200
        )
    sessions[session.session_id] = session
    return response


@app.delete("/session")
async def delete_session(request: SessionRequest):
    if request.session_id not in sessions.keys():
        return JSONResponse(
            content={"message": "Session wasn't found."}, status_code=400
        )
    else:
        del sessions[request.session_id]
        return JSONResponse(
            content={"message": "Session was deleted."}, status_code=200
        )


@app.post("/session/{session_id}/invite")
async def create_invite(session_id: str):
    return JSONResponse(
        content={
            "message": "Invite link created",
            "link": f"ws://0.0.0.0:8081/session/{session_id}",
        },
        status_code=201,
    )


@app.websocket("/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Ensure session exists
    if session_id not in sessions.keys():
        await websocket.send_text("Session does not exist. Please create it first.")
        await websocket.close()
        return

    sessions[session_id].active_users.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            for client in sessions[session_id].active_users:
                if client != websocket:
                    await client.send_text(message)
    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")
    finally:
        sessions[session_id].active_users.remove(websocket)
        if not sessions[session_id]:  # Remove session if empty
            del sessions[session_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
