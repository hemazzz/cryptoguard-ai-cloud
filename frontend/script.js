document.addEventListener("DOMContentLoaded", () => {
  const addressInput = document.getElementById("address");
  const chainSelect = document.getElementById("chain");
  const verifyBtn = document.getElementById("verifyBtn");
  const resultBox = document.getElementById("result");

  verifyBtn.addEventListener("click", async () => {
    const address = addressInput.value.trim();
    const chain = chainSelect.value; // BTC or ETH

    if (!address) {
      resultBox.style.color = "red";
      resultBox.innerText = "Please enter an address";
      return;
    }

    resultBox.style.color = "#00e0ff";
    resultBox.innerText = "Checking blockchain data...";

    try {
      const response = await fetch(
        "https://cryptoguard-ai-cloud-1.onrender.com/verify",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            address: address,
            chain: chain
          })
        }
      );

      if (!response.ok) {
        throw new Error("Server error");
      }

      const data = await response.json();

      // 🔥 GUARANTEED SAFE VALUES (no undefined)
      const txCount =
        data.transactions !== undefined ? data.transactions : "N/A";

      const balance =
        data.balance !== undefined ? data.balance : "N/A";

      const result =
        data.result !== undefined ? data.result : "N/A";

      const chainName =
        data.chain !== undefined ? data.chain : chain;

      resultBox.style.color = "#00ff9c";
      resultBox.innerText =
        "Chain: " + chainName + "\n" +
        "Balance: " + balance + "\n" +
        "Transactions: " + txCount + "\n" +
        "Status: " + result;

    } catch (error) {
      console.error(error);
      resultBox.style.color = "red";
      resultBox.innerText = "Error connecting to backend";
    }
  });
});
