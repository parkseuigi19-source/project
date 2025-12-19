from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .app.database import engine, Base
from .app.routers import todos, problems, goals, users, logs

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlowTask API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(todos.router)
app.include_router(logs.router)
app.include_router(problems.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Serve Frontend
from fastapi.staticfiles import StaticFiles
import os

# Ensure frontend directory exists to avoid errors if run from wrong CWD
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
else:
    print("Warning: 'frontend' directory not found. Static serving disabled.")
