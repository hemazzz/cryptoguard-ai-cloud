from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

app = FastAPI()

# CORS
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
    return {"msg": "CryptoGuard AI Backend Running"}

@app.post("/check-address")
def check_address(payload: Address):

    address = payload.address.strip()

    # 🔥 BLOCKCHAIN.INFO API (NO CACHE)
    url = f"https://blockchain.info/rawaddr/{address}?limit=0"

    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            return {"valid": False, "error": "Invalid address"}

        data = res.json()
    except Exception as e:
        return {"valid": False, "error": str(e)}

    # BASIC DATA
    balance = data.get("final_balance", 0) / 1e8
    total_received = data.get("total_received", 0) / 1e8
    total_tx = data.get("n_tx", 0)

    txs = data.get("txs", [])

    # MAX SINGLE TRANSACTION
    max_single_tx = 0
    for tx in txs:
        for out in tx.get("out", []):
            val = out.get("value", 0) / 1e8
            if val > max_single_tx:
                max_single_tx = val

    # 🐳 WHALE LOGIC (REAL WORLD)
    whale = "NO"
    if total_received >= 100:
        whale = "YES"
    elif max_single_tx >= 10:
        whale = "YES"
    elif total_tx >= 500 and total_received >= 50:
        whale = "YES"

    # MARKET LOGIC
    if balance == 0 and total_tx > 100:
        market = "DUMP"
    elif balance > 10:
        market = "HOLD"
    else:
        market = "NORMAL"

    # SCAM LOGIC
    if balance == 0 and total_tx > 500:
        scam = "POSSIBLE SCAM"
        reason = "High transaction activity with zero balance"
    else:
        scam = "LOW RISK"
        reason = "Normal transaction behavior"

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
