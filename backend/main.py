from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import re

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== CONFIG =====
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY")
ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"

# ===== VALIDATION =====
def is_valid_btc(address: str) -> bool:
    return isinstance(address, str) and len(address) >= 26

def is_valid_eth(address: str) -> bool:
    return bool(re.fullmatch(r"0x[a-fA-F0-9]{40}", address))

# ===== API =====
@app.post("/verify")
def verify_address(data: dict):
    address = data.get("address")
    chain = data.get("chain")

    # ================= BTC =================
    if chain == "BTC":
        if not is_valid_btc(address):
            return {
                "chain": "BTC",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid BTC address"
            }

        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}"
        r = requests.get(url, timeout=10).json()

        balance_btc = r.get("balance", 0) / 1e8
        txs = r.get("n_tx", 0)

        whale = "Whale activity detected" if balance_btc >= 100 else "No whale activity"

        return {
            "chain": "BTC",
            "balance": round(balance_btc, 8),
            "transactions": txs,
            "result": whale
        }

    # ================= ETH =================
    elif chain == "ETH":
        if not is_valid_eth(address):
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid ETH address"
            }

        if not ALCHEMY_API_KEY:
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Alchemy API key missing"
            }

        # --- Balance ---
        balance_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getBalance",
            "params": [address, "latest"]
        }

        balance_res = requests.post(ALCHEMY_URL, json=balance_payload, timeout=10).json()
        balance_wei = int(balance_res.get("result", "0"), 16)
        balance_eth = balance_wei / 1e18

        # --- Transaction Count ---
        tx_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "eth_getTransactionCount",
            "params": [address, "latest"]
        }

        tx_res = requests.post(ALCHEMY_URL, json=tx_payload, timeout=10).json()
        tx_count = int(tx_res.get("result", "0"), 16)

        whale = "Whale activity detected" if balance_eth >= 1000 else "No whale activity"

        return {
            "chain": "ETH",
            "balance": round(balance_eth, 6),
            "transactions": tx_count,
            "result": whale
        }

    return {"error": "Unsupported chain"}
