async function verify() {
  const address = document.getElementById("address").value;
  const chain = document.getElementById("chain").value;

  const res = await fetch("http://127.0.0.1:8000/verify", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      address: address,
      chain: chain
    })
  });

  const data = await res.json();

  document.getElementById("result").innerHTML = `
    <b>Chain:</b> ${data.chain}<br>
    <b>Balance:</b> ${data.balance}<br>
    <b>Transactions:</b> ${data.transactions ?? "-"}<br>
    <b>Status:</b> ${data.result}
  `;
}
