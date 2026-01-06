from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# CORS (frontend connect aagarthuku)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------- INPUT MODEL -----------
class Address(BaseModel):
    address: str


# ----------- HOME ROUTE -----------
@app.get("/")
def home():
    return {"msg": "CryptoGuard AI Backend Running"}


# ----------- MAIN API -----------
@app.post("/check-address")
def check_address(data: Address):

    address = data.address.strip()

    # 🔑 BlockCypher API (free, no key also works)
    url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"

    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return {"valid": False, "error": "Invalid address or API error"}

        data = res.json()

    except Exception as e:
        return {"valid": False, "error": str(e)}

    # -------- BASIC DATA --------
    balance = data.get("balance", 0) / 1e8
    total_tx = data.get("n_tx", 0)
    total_received = data.get("total_received", 0) / 1e8

    txrefs = data.get("txrefs", []) or []

    # -------- MAX SINGLE TRANSACTION --------
    max_single_tx = 0
    for tx in txrefs:
        value_btc = tx.get("value", 0) / 1e8
        if value_btc > max_single_tx:
            max_single_tx = value_btc

    # -------- MARKET LOGIC --------
    if balance == 0 and total_tx > 100:
        market = "DUMP"
    elif balance > 10 and total_tx < 50:
        market = "HOLD"
    else:
        market = "NORMAL"

    # -------- SCAM LOGIC --------
    if balance == 0 and total_tx > 500:
        scam = "POSSIBLE SCAM"
        reason = "High transaction activity with zero balance"
    elif max_single_tx > 50 and balance == 0:
        scam = "HIGH RISK"
        reason = "Large fund movement with no retained balance"
    else:
        scam = "LOW RISK"
        reason = "Normal transaction behavior"

    # -------- 🐳 WHALE DETECTION (REAL LOGIC) --------
    whale = "NO"

    if total_received >= 100:
        whale = "YES"
    elif max_single_tx >= 10:
        whale = "YES"
    elif total_tx >= 500 and total_received >= 50:
        whale = "YES"

    # -------- FINAL RESPONSE --------
    return {
        "valid": True,
        "balance": round(balance, 8),
        "total_tx": total_tx,
        "total_received": round(total_received, 8),
        "largest_tx": round(max_single_tx, 8),
        "market": market,
        "scam": scam,
        "whale": whale,
        "reason": reason
    }
