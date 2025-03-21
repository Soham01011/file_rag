import uvicorn
from fastapi import FastAPI
from app.api import auth, files, chat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI MongoDB Auth App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(files.router)
app.include_router(chat.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Auth API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
