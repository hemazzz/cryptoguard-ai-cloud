async function verify() {
    const addr = document.getElementById("address").value;
    const out = document.getElementById("result");

    if (addr.trim() === "") {
        out.innerText = "Please enter an address";
        return;
    }

    try {
        const res = await fetch("http://127.0.0.1:8000/check-address", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ address: addr })
        });

        const data = await res.json();

        out.innerText =
`Bitcoin Address ✅

Balance: ${data.balance} satoshi
Total Transactions: ${data.total_tx}

Market Behavior: ${data.market}
Scam Status: ${data.scam}
Whale Activity: ${data.whale}

Reason:
${data.reason}`;

    } catch (e) {
        out.innerText = "Backend not reachable";
    }
}
