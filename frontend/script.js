function checkAddress() {
  const address = document.getElementById("address").value.trim();

  fetch("https://cryptoguard-ai-cloud.onrender.com/check-address", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      address: address   // 🔴 MUST MATCH backend
    })
  })
  .then(res => res.json())
  .then(data => {
    if (!data.valid) {
      document.getElementById("result").innerHTML = "Invalid Address";
      return;
    }

    document.getElementById("result").innerHTML = `
      <b>Bitcoin Address ✅</b><br><br>
      Balance: ${data.balance} BTC<br>
      Total Transactions: ${data.total_tx}<br><br>

      Market Behavior: ${data.market}<br>
      Scam Status: ${data.scam}<br>
      Whale Activity: ${data.whale}<br><br>

      Reason: ${data.reason}
    `;
  })
  .catch(err => {
    document.getElementById("result").innerHTML = "Error connecting to backend";
  });
}
