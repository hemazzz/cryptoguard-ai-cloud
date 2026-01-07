function isValidBTC(address) {
  return /^(1|3|bc1)[a-zA-Z0-9]{25,39}$/.test(address);
}

function isValidETH(address) {
  return /^0x[a-fA-F0-9]{40}$/.test(address);
}

document.getElementById("verifyBtn").addEventListener("click", async () => {
  const address = document.getElementById("address").value.trim();
  const chainRaw = document.getElementById("chain").value;
  const resultBox = document.getElementById("result");

  // normalize chain value
  const chain = chainRaw.toUpperCase().includes("ETH") ? "ETH" : "BTC";

  if (!address) {
    resultBox.innerText = "Please enter an address";
    return;
  }

  if (chain === "BTC" && !isValidBTC(address)) {
    resultBox.innerText = "Invalid Bitcoin address";
    return;
  }

  if (chain === "ETH" && !isValidETH(address)) {
    resultBox.innerText = "Invalid Ethereum address";
    return;
  }

  resultBox.innerText = "Checking...";

  try {
    const res = await fetch(
      "https://cryptoguard-ai-cloud-1.onrender.com/verify",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address, chain })
      }
    );

    const data = await res.json();

    resultBox.innerText =
      `Chain: ${data.chain}\n` +
      `Balance: ${data.balance}\n` +
      `Transactions: ${data.transactions}\n` +
      `Result: ${data.result}`;
  } catch (err) {
    resultBox.innerText = "Backend connection error";
  }
});
