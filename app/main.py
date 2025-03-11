from fastapi import FastAPI
from app.api import auth, files
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI MongoDB Auth App")

origins = [
    "http://localhost",
    "http://localhost:3000",  # add your frontend domain if different
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Auth API"}
