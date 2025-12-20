import discord
from discord.ext import commands
import requests
import os
from datetime import datetime, timezone

# =========================
# CONFIG
# =========================
BOT_PREFIX = "!"
BLOCKSTREAM_BASE = "https://blockstream.info/api"
WHALE_THRESHOLD_BTC = 300

# =========================
# BOT SETUP
# =========================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

# =========================
# SIMPLE BTC FORMAT CHECK
# (NO API, NO DISCORD PARSER)
# =========================
def looks_like_btc_address(addr: str) -> bool:
    addr = addr.lower()
    return (
        (addr.startswith("1") and 26 <= len(addr) <= 35) or
        (addr.startswith("3") and 26 <= len(addr) <= 35) or
        (addr.startswith("bc1") and len(addr) >= 42)
    )

# =========================
# BLOCKSTREAM HELPERS
# =========================
def get_address_info(address):
    r = requests.get(f"{BLOCKSTREAM_BASE}/address/{address}", timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()

def get_address_txs(address):
    r = requests.get(f"{BLOCKSTREAM_BASE}/address/{address}/txs", timeout=10)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json()

# =========================
# WHALE DETECTION
# =========================
def detect_whale(txs):
    max_btc = 0
    whale = False

    for tx in txs:
        for vout in tx.get("vout", []):
            btc = vout.get("value", 0) / 1e8
            max_btc = max(max_btc, btc)
            if btc >= WHALE_THRESHOLD_BTC:
                whale = True

    return whale, round(max_btc, 2)

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"{bot.user} is ONLINE 🚀")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! Bot is working 🚀")

# =========================
# MAIN COMMAND (RAW MESSAGE METHOD)
# =========================
@bot.command()
async def btcplus(ctx):
    # 🔥 RAW MESSAGE – DISCORD PARSER BYPASS
    msg = ctx.message.content

    parts = msg.split(maxsplit=1)
    if len(parts) < 2:
        await ctx.send("❌ Usage: `!btcplus <bitcoin_address>`")
        return

    address = parts[1]

    # HARD CLEAN (ALL DISCORD GARBAGE REMOVE)
    address = (
        address.replace("`", "")
        .replace("<", "")
        .replace(">", "")
        .replace("\n", "")
        .replace("\u200b", "")
        .strip()
    )

    await ctx.send(f"🔍 Analyzing Bitcoin address...\n`{address}`")

    # FORMAT CHECK
    if not looks_like_btc_address(address):
        await ctx.send("❌ Invalid Bitcoin address format.")
        return

    # BLOCKSTREAM CALL
    try:
        info = get_address_info(address)
        txs = get_address_txs(address)
    except requests.exceptions.RequestException:
        await ctx.send("⚠️ Blockchain API error. Try again later.")
        return

    # VALID BUT UNUSED
    if info is None:
        await ctx.send("⚠️ **Valid Bitcoin address but no transactions found yet.**")
        return

    funded = info["chain_stats"]["funded_txo_sum"]
    spent = info["chain_stats"]["spent_txo_sum"]

    balance = (funded - spent) / 1e8
    total_received = funded / 1e8
    tx_count = info["chain_stats"]["tx_count"]

    age_days = 0
    if txs and txs[-1]["status"].get("block_time"):
        first_seen = txs[-1]["status"]["block_time"]
        first_date = datetime.fromtimestamp(first_seen, tz=timezone.utc)
        age_days = (datetime.now(timezone.utc) - first_date).days

    whale, max_tx = detect_whale(txs)

    whale_text = (
        f"🐋 **Whale Activity Detected (~{max_tx} BTC)**"
        if whale else
        "❌ No Recent Whale Activity Detected"
    )

    await ctx.send(
        f"🧠 **CryptoGuard AI – Bitcoin Analysis**\n"
        f"• Balance: `{balance:.4f} BTC`\n"
        f"• Total Received: `{total_received:.4f} BTC`\n"
        f"• Transactions: `{tx_count}`\n"
        f"• Address Age: `{age_days} days`\n"
        f"• Max Tx: `{max_tx} BTC`\n\n"
        f"{whale_text}"
    )

# =========================
# RUN
# =========================
bot.run(os.getenv("DISCORD_TOKEN"))
