import os
import uuid
import uvicorn
import datetime
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, Response
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST


from models.session import Session, SessionRequest

app = FastAPI(docs_url="/session/docs", openapi_url="/session/openapi.json")

# --- MongoDB Setup ---
# Use the MONGO_URL from environment or default to a Docker Compose host name.
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb:27017")
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.fastapi_db  # Database name: fastapi_db
sessions_collection = db.sessions  # Collection name: sessions

# --- In-memory storage for active WebSocket connections ---
# Keys are session IDs; values are lists of active WebSocket connections.
active_connections = {}

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


@app.get("/session/status")
async def status():
    return JSONResponse(content={"message": "healthy"}, status_code=200)


@app.get("/session")
async def list_sessions(
    session_id: Optional[str] = None,
    active: Optional[bool] = False,
):
    if session_id and active:
        return JSONResponse(
            content={"message": "Can't filter by both params.", "sessions": {}},
            status_code=400,
        )
    if session_id:
        session = await sessions_collection.find_one({"session_id": session_id})
        if session:
            session.pop("_id", None)
        return JSONResponse(
            content={"sessions": [session.model_dump()] if session else []},
            status_code=200,
        )
    if active:
        # Filter sessions that have active connections (based on our in-memory store)
        active_ids = list(active_connections.keys())
        cursor = sessions_collection.find({"session_id": {"$in": active_ids}})
        sessions_list = await cursor.to_list(length=None)
        for doc in sessions_list:
            doc.pop("_id", None)
        return JSONResponse(content={"sessions": sessions_list}, status_code=200)
    # Return all sessions from the database.
    cursor = sessions_collection.find({})
    sessions_list = await cursor.to_list(length=None)
    for doc in sessions_list:
        doc.pop("_id", None)
    return JSONResponse(content={"sessions": sessions_list}, status_code=200)

    # if session_id and active:
    #     return JSONResponse(
    #         content={"message": "Can't filter by both params.", "sessions": dict()},
    #         status_code=400,
    #     )
    # if session_id:
    #     return JSONResponse(
    #         content={"sessions": [sessions[session_id]]}, status_code=200
    #     )
    # if active:
    #     return JSONResponse(
    #         content={
    #             "sessions": {
    #                 key: session.model_dump()
    #                 for key, session in sessions.items()
    #                 if session.active_users
    #             }
    #         },
    #         status_code=200,
    #     )
    # return JSONResponse(
    #     content={
    #         "sessions": {key: session.model_dump() for key, session in sessions.items()}
    #     },
    #     status_code=200,
    # )


@app.post("/session")
async def create_session():
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "created_at": datetime.datetime.now().timestamp(),
        "allowed_users": [],
        "active_users": [],
    }
    await sessions_collection.insert_one(session_data)
    # Initialize the in-memory active connections for this session.
    active_connections[session_id] = []
    return JSONResponse(
        content={"message": "Session created.", "session_id": session_id},
        status_code=201,
    )

    # session_id = str(uuid.uuid4())
    # sessions[session_id] = Session(
    #     session_id=session_id,
    #     created_at=datetime.datetime.now().timestamp(),
    # )
    # return JSONResponse(content={"message": "Session created."}, status_code=201)


@app.put("/session")
async def update_session(session: Session):
    existing = await sessions_collection.find_one({"session_id": session.session_id})
    if not existing:
        status_code_resp = 400
        message = "Session didn't exist, so it was created."
    else:
        status_code_resp = 200
        message = "Session updated."
    # Upsert the session document (update if exists, insert otherwise)
    await sessions_collection.update_one(
        {"session_id": session.session_id},
        {"$set": session.model_dump()},
        upsert=True,
    )
    return JSONResponse(content={"message": message}, status_code=status_code_resp)

    # response = {}
    # if session.session_id not in sessions.keys():
    #     response = JSONResponse(
    #         content={"message": "Session didn't exist, so it was created."},
    #         status_code=400,
    #     )
    # else:
    #     response = JSONResponse(
    #         content={"message": "Session updated."}, status_code=200
    #     )
    # sessions[session.session_id] = session
    # return response


@app.delete("/session")
async def delete_session(request: SessionRequest):
    result = await sessions_collection.delete_one({"session_id": request.session_id})
    if result.deleted_count == 0:
        return JSONResponse(
            content={"message": "Session wasn't found."}, status_code=400
        )
    # Remove from active connections if present.
    active_connections.pop(request.session_id, None)
    return JSONResponse(content={"message": "Session was deleted."}, status_code=200)

    # if request.session_id not in sessions.keys():
    #     return JSONResponse(
    #         content={"message": "Session wasn't found."}, status_code=400
    #     )
    # else:
    #     del sessions[request.session_id]
    #     return JSONResponse(
    #         content={"message": "Session was deleted."}, status_code=200
    #     )


@app.post("/session/{session_id}/invite")
async def create_invite(session_id: str):
    return JSONResponse(
        content={
            "message": "Invite link created",
            "link": f"ws://0.0.0.0:8001/session/{session_id}",
        },
        status_code=201,
    )


@app.websocket("/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # Check if the session exists in the database.
    session = await sessions_collection.find_one({"session_id": session_id})
    if not session:
        await websocket.send_text("Session does not exist. Please create it first.")
        await websocket.close()
        return

    name = await websocket.receive_text()
    if name not in session["allowed_users"]:
        await websocket.send_text("You are not allowed in this session.")
        await websocket.close()
        return
    else:
        await websocket.send_text("server:: You've joined.")

    # Add this WebSocket connection to the in-memory active connections.
    if session_id not in active_connections:
        active_connections[session_id] = []
    active_connections[session_id].append(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            # Broadcast the message to all other active connections in this session.
            for client in active_connections[session_id]:
                if client != websocket:
                    await client.send_text(f"{name}::  {message}")
    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")
    finally:
        active_connections[session_id].remove(websocket)
        # Optionally, if no active connections remain, you might update the session document,
        # for example, setting a deletion timestamp or handling cleanup.
        if not active_connections[session_id]:
            # Here we choose to keep the persistent session intact.
            pass

    # await websocket.accept()

    # # Ensure session exists
    # if session_id not in sessions.keys():
    #     await websocket.send_text("Session does not exist. Please create it first.")
    #     await websocket.close()
    #     return

    # sessions[session_id].active_users.append(websocket)

    # try:
    #     while True:
    #         message = await websocket.receive_text()
    #         for client in sessions[session_id].active_users:
    #             if client != websocket:
    #                 await client.send_text(message)
    # except WebSocketDisconnect:
    #     print(f"Client disconnected from session {session_id}")
    # finally:
    #     sessions[session_id].active_users.remove(websocket)
    #     if not sessions[session_id]:  # Remove session if empty
    #         del sessions[session_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 8001))
