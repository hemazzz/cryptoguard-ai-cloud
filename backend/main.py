from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_valid_btc(address):
    return len(address) >= 26

def is_valid_eth(address):
    return re.fullmatch(r"0x[a-fA-F0-9]{40}", address)

@app.post("/verify")
def verify_address(data: dict):
    address = data.get("address")
    chain = data.get("chain")

    # ---------- BTC ----------
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

        balance = r.get("balance", 0) / 1e8
        txs = r.get("n_tx", 0)

        whale = "Whale activity detected" if balance >= 100 else "No whale activity"

        return {
            "chain": "BTC",
            "balance": balance,
            "transactions": txs,
            "result": whale
        }

    # ---------- ETH (SAFE & FIXED) ----------
    elif chain == "ETH":
        if not is_valid_eth(address):
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid ETH address"
            }

        rpc_url = "https://rpc.ankr.com/eth"

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1
        }

        try:
            res = requests.post(rpc_url, json=payload, timeout=10).json()
        except Exception:
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "ETH RPC not reachable"
            }

        # 🔥 KEY FIX: result check
        if "result" not in res:
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "ETH data temporarily unavailable"
            }

        balance_wei = int(res["result"], 16)
        balance_eth = balance_wei / 10**18

        whale = "Whale activity detected" if balance_eth >= 1000 else "No whale activity"

        return {
            "chain": "ETH",
            "balance": balance_eth,
            "transactions": "N/A",
            "result": whale
        }

    return {"error": "Unsupported chain"}

