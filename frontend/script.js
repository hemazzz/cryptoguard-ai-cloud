const API_URL = "https://cryptoguard-ai-cloud-1.onrender.com/verify";

async function verifyAddress() {
  const address = document.getElementById("address").value.trim();
  const chain = document.getElementById("chain").value;
  const resultBox = document.getElementById("result");

  resultBox.style.color = "#00ff9c";
  resultBox.innerText = "Checking address...";

  if (!address) {
    resultBox.style.color = "red";
    resultBox.innerText = "Address required";
    return;
  }

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        address: address,
        chain: chain
      })
    });

    const data = await response.json();

    // 🔥 SAFE FIELD MAPPING (BTC + ETH)
    const balance =
      data.balance !== undefined ? data.balance : "N/A";

    const transactions =
      data.transactions ??
      data.tx_count ??
      data.n_tx ??
      "N/A";

    const status =
      data.result ?? data.status ?? "N/A";

    resultBox.style.color = "#00ff9c";
    resultBox.innerText =
      "Chain: " + data.chain + "\n" +
      "Balance: " + balance + "\n" +
      "Transactions: " + transactions + "\n" +
      "Status: " + status;

  } catch (err) {
    resultBox.style.color = "red";
    resultBox.innerText = "Backend error / API down";
    console.error(err);
  }
}
