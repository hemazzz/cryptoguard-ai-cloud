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
    chain: str   # BTC or ETH


# ---------------- BTC (mempool.space – NO API) ----------------
def get_btc_data(address):
    url = f"https://mempool.space/api/address/{address}"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return {"error": "Invalid BTC address"}

    data = r.json()

    balance = (
        data["chain_stats"]["funded_txo_sum"]
        - data["chain_stats"]["spent_txo_sum"]
    ) / 1e8

    tx_count = data["chain_stats"]["tx_count"]

    whale = "🐋 Whale detected" if balance >= 100 else "No whale activity"

    return {
        "chain": "BTC",
        "balance": balance,
        "transactions": tx_count,
        "result": whale
    }


# ---------------- ETH (Public RPC – NO API) ----------------
def get_eth_data(address):
    rpc_url = "https://rpc.ankr.com/eth"

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }

    r = requests.post(rpc_url, json=payload, timeout=10).json()

    if "result" not in r:
        return {"error": "Invalid ETH address"}

    balance_wei = int(r["result"], 16)
    balance_eth = balance_wei / 1e18

    whale = "🐋 Whale detected" if balance_eth >= 1000 else "No whale activity"

    return {
        "chain": "ETH",
        "balance": balance_eth,
        "result": whale
    }


# ---------------- MAIN API ----------------
@app.post("/verify")
def verify_address(data: Address):

    if data.chain.upper() == "BTC":
        return get_btc_data(data.address)

    elif data.chain.upper() == "ETH":
        return get_eth_data(data.address)

    else:
        return {"error": "Unsupported chain"}
