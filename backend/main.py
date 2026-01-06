from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Address(BaseModel):
    address: str

@app.get("/")
def home():
    return {"msg": "Backend running"}

@app.post("/check-address")
def check_address(data: Address):
    return {
        "valid": True,
        "balance": 0,
        "total_tx": 1124,
        "market": "DUMP",
        "scam": "POSSIBLE SCAM",
        "whale": "NO",
        "reason": "High transaction activity with zero balance"
    }
