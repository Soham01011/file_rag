from fastapi import FastAPI
from app.api import auth, files
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FastAPI MongoDB Auth App")

# Allow all origins (Not recommended for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows requests from any domain
    allow_credentials=True,
    allow_methods=["*"],  # This allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # This allows all headers
)

app.include_router(auth.router)
app.include_router(files.router)

app.include_router(auth.router)
app.include_router(files.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Auth API"}
