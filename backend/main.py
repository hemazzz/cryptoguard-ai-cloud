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

    if chain == "BTC":
        if not is_valid_btc(address):
            return {
                "chain": "BTC",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid BTC address"
            }

        url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}"
        r = requests.get(url).json()

        balance = r.get("balance", 0) / 1e8
        txs = r.get("n_tx", 0)

        whale = "Whale activity detected" if balance >= 100 else "No whale activity"

        return {
            "chain": "BTC",
            "balance": balance,
            "transactions": txs,
            "result": whale
        }

    elif chain == "ETH":
        if not is_valid_eth(address):
            return {
                "chain": "ETH",
                "balance": "N/A",
                "transactions": "N/A",
                "result": "Invalid ETH address"
            }

        url = f"https://api.blockcypher.com/v1/eth/main/addrs/{address}/balance"
        r = requests.get(url).json()

        balance = r.get("balance", 0) / 1e18
        txs = r.get("n_tx", 0)

        whale = "Whale activity detected" if balance >= 1000 else "No whale activity"

        return {
            "chain": "ETH",
            "balance": balance,
            "transactions": txs,
            "result": whale
        }

    return {"error": "Unsupported chain"}
