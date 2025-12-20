import discord
from discord.ext import commands
import requests
import os
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
BOT_PREFIX = "!"
BLOCKSTREAM_API = "https://blockstream.info/api"
WHALE_THRESHOLD_BTC = 300  # BTC

# =========================
# DISCORD BOT SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# =========================
# UTILS
# =========================
def clean_address(addr: str) -> str:
    return (
        addr.replace("`", "")
        .replace("\n", "")
        .replace("\u200b", "")
        .strip()
    )

def is_valid_btc_address(addr: str) -> bool:
    addr = addr.lower()
    if addr.startswith("1") and 26 <= len(addr) <= 35:
        return True
    if addr.startswith("3") and 26 <= len(addr) <= 35:
        return True
    if addr.startswith("bc1") and len(addr) >= 42:
        return True
    return False

# =========================
# BLOCKSTREAM API
# =========================
def get_address_info(address):
    r = requests.get(f"{BLOCKSTREAM_API}/address/{address}", timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

def get_address_txs(address):
    r = requests.get(f"{BLOCKSTREAM_API}/address/{address}/txs", timeout=10)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json()

# =========================
# WHALE DETECTION
# =========================
def detect_whale(txs):
    whale = False
    max_tx = 0.0

    for tx in txs:
        for vout in tx.get("vout", []):
            btc = vout.get("value", 0) / 1e8
            if btc > max_tx:
                max_tx = btc
            if btc >= WHALE_THRESHOLD_BTC:
                whale = True

    return whale, round(max_tx, 2)

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} is ONLINE 🚀")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! CryptoGuard AI is live 🚀")

# =========================
# MAIN COMMAND
# =========================
@bot.command()
async def btcplus(ctx, *, address: str):
    address = clean_address(address)

    await ctx.send(f"🔍 Analyzing Bitcoin address...\n`{address}`")

    # Local validation
    if not is_valid_btc_address(address):
        await ctx.send("❌ Invalid Bitcoin address format.")
        return

    # API call
    try:
        info = get_address_info(address)
        txs = get_address_txs(address)
    except Exception as e:
        print("API error:", e)
        await ctx.send("⚠️ Blockchain API temporarily unavailable.")
        return

    if info is None:
        await ctx.send("⚠️ Valid Bitcoin address but no transactions found.")
        return

    # Stats
    funded = info["chain_stats"]["funded_txo_sum"]
    spent = info["chain_stats"]["spent_txo_sum"]

    balance = (funded - spent) / 1e8
    total_received = funded / 1e8
    tx_count = info["chain_stats"]["tx_count"]

    # Address age
    age_days = 0
    if txs and txs[-1]["status"].get("block_time"):
        first_seen = txs[-1]["status"]["block_time"]
        first_date = datetime.fromtimestamp(first_seen, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - first_date).days

    # Whale detection
    whale, max_tx = detect_whale(txs)

    whale_msg = (
        f"🐋 **Whale Transaction Detected (~{max_tx} BTC)**"
        if whale
        else f"❌ **Whale Not Detected** (Max Tx: {max_tx} BTC)"
    )

    # Output
    await ctx.send(
        f"🧠 **CryptoGuard AI – Bitcoin Analysis**\n"
        f"• Balance: `{balance:.4f} BTC`\n"
        f"• Total Received: `{total_received:.4f} BTC`\n"
        f"• Transactions: `{tx_count}`\n"
        f"• Address Age: `{age_days} days`\n"
        f"• Max Tx: `{max_tx} BTC`\n\n"
        f"{whale_msg}"
    )

# =========================
# RUN BOT (FINAL – RAILWAY SAFE)
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

bot.run(TOKEN)
