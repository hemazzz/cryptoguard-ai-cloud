from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- VALIDATORS ----------------
def is_valid_btc(address: str) -> bool:
    return address is not None and len(address) >= 26

def is_valid_eth(address: str) -> bool:
    return re.fullmatch(r"0x[a-fA-F0-9]{40}", address) is not None

# ---------------- MAIN API ----------------
@app.post("/verify")
def verify_address(data: dict):
    address = data.get("address")
    chain = data.get("chain")

    # ---------------- BTC ----------------
    if chain == "BTC":
        if not is_valid_btc(address):
            return {
                "chain": "BTC",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid BTC address"
            }

        try:
            r = requests.get(
                f"https://api.blockcypher.com/v1/btc/main/addrs/{address}",
                timeout=10
            ).json()
        except Exception:
            return {
                "chain": "BTC",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "BTC API not reachable"
            }

        balance_btc = r.get("balance", 0) / 1e8
        txs = r.get("n_tx", 0)

        whale = "Whale activity detected" if balance_btc >= 100 else "No whale activity"

        return {
            "chain": "BTC",
            "balance": round(balance_btc, 8),
            "transactions": txs,
            "result": whale
        }

    # ---------------- ETH (CLOUDFLARE RPC) ----------------
    elif chain == "ETH":
        if not is_valid_eth(address):
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid ETH address"
            }

        payload = {
            "jsonrpc": "2.0",
            "method": "eth_getBalance",
            "params": [address, "latest"],
            "id": 1
        }

        try:
            res = requests.post(
                "https://cloudflare-eth.com",
                json=payload,
                timeout=10
            ).json()
        except Exception:
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "ETH RPC not reachable"
            }

        if "result" not in res:
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "ETH data temporarily unavailable"
            }

        try:
            balance_wei = int(res["result"], 16)
            balance_eth = balance_wei / 10**18
        except Exception:
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "ETH balance parse error"
            }

        whale = "Whale activity detected" if balance_eth >= 1000 else "No whale activity"

        return {
            "chain": "ETH",
            "balance": round(balance_eth, 6),
            "transactions": "N/A",
            "result": whale
        }

    # ---------------- UNSUPPORTED ----------------
    return {
        "chain": chain,
        "balance": "N/A",
        "transactions": "N/A",
        "result": "Unsupported chain"
    }
