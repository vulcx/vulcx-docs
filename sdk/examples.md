---
title: "SDK examples"
description: "Complete @vulcx/sdk integration examples for React, Next.js, Node.js, browser/CDN, and ExactOut mode."
llmDescription: "End-to-end Vulcx TypeScript SDK examples for React, Next.js (App Router), Node.js, and browser/CDN, plus an ExactOut-mode example. Each shows initializing VulcxSDK, quoting, building a transaction, and signing/submitting on Fogo."
---

Complete integration examples for different environments.

---

## React

```tsx
import { VulcxSDK, NoRouteError } from "@vulcx/sdk";
import type { QuoteResponse } from "@vulcx/sdk";
import { useEffect, useState } from "react";

const sdk = new VulcxSDK({ apiKey: "argy_your_api_key" });

function SwapPage() {
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [error, setError] = useState("");

  async function fetchQuote(amount: string) {
    setError("");
    try {
      const q = await sdk.quote({
        inputMint: "So11111111111111111111111111111111111111112",
        outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
        amount,
        swapMode: "ExactIn",
        slippageBps: 50,
      });
      setQuote(q);
    } catch (err) {
      if (err instanceof NoRouteError) {
        setError("No route found");
      } else {
        setError("Quote failed");
      }
    }
  }

  return (
    <div>
      <input
        type="text"
        placeholder="Amount in lamports"
        onChange={(e) => fetchQuote(e.target.value)}
      />
      {quote && (
        <p>
          Output: {quote.amountOut} | Impact: {quote.priceImpactPercent}
        </p>
      )}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}
```

---

## Next.js (App Router)

```tsx
"use client";

import { VulcxSDK } from "@vulcx/sdk";
import type { SwapResponse } from "@vulcx/sdk";
import { useWallet, useConnection } from "@solana/wallet-adapter-react";
import { VersionedTransaction } from "@solana/web3.js";
import { useState } from "react";

const sdk = new VulcxSDK({ apiKey: process.env.NEXT_PUBLIC_VULCX_KEY! });

export default function SwapButton() {
  const { publicKey, signTransaction } = useWallet();
  const { connection } = useConnection();
  const [loading, setLoading] = useState(false);

  async function handleSwap() {
    if (!publicKey || !signTransaction) return;
    setLoading(true);

    try {
      const swap = await sdk.swap({
        userWallet: publicKey.toBase58(),
        inputMint: "So11111111111111111111111111111111111111112",
        outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
        amount: "1000000000",
        swapMode: "ExactIn",
        slippageBps: 50,
      });

      const tx = VersionedTransaction.deserialize(
        Buffer.from(swap.transaction, "base64")
      );
      const signed = await signTransaction(tx);
      const sig = await connection.sendRawTransaction(signed.serialize());

      await connection.confirmTransaction({
        signature: sig,
        lastValidBlockHeight: swap.lastValidBlockHeight,
        blockhash: tx.message.recentBlockhash,
      });

      console.log("Swap confirmed:", sig);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button onClick={handleSwap} disabled={loading || !publicKey}>
      {loading ? "Swapping..." : "Swap 1 SOL → USDC"}
    </button>
  );
}
```

---

## Node.js

```javascript
const { VulcxSDK } = require("@vulcx/sdk");
const { Connection, VersionedTransaction, Keypair } = require("@solana/web3.js");
const bs58 = require("bs58");

async function main() {
  const sdk = new VulcxSDK({
    apiKey: process.env.VULCX_API_KEY,
  });

  const wallet = Keypair.fromSecretKey(bs58.decode(process.env.WALLET_KEY));
  const connection = new Connection(process.env.RPC_URL);

  // Quote
  const quote = await sdk.quote({
    inputMint: "So11111111111111111111111111111111111111112",
    outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
    amount: "1000000000",
    swapMode: "ExactIn",
  });
  console.log("Quote:", quote.amountOut, "USDC");

  // Swap
  const swap = await sdk.swap({
    userWallet: wallet.publicKey.toBase58(),
    inputMint: "So11111111111111111111111111111111111111112",
    outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
    amount: "1000000000",
    swapMode: "ExactIn",
    slippageBps: 50,
  });

  const tx = VersionedTransaction.deserialize(
    Buffer.from(swap.transaction, "base64")
  );
  tx.sign([wallet]);

  const sig = await connection.sendTransaction(tx, { maxRetries: 3 });
  console.log("Submitted:", sig);

  const confirmation = await connection.confirmTransaction({
    signature: sig,
    lastValidBlockHeight: swap.lastValidBlockHeight,
    blockhash: tx.message.recentBlockhash,
  });

  console.log(confirmation.value.err ? "Failed" : "Confirmed");
}

main().catch(console.error);
```

---

## Browser / CDN

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.vulcx.xyz/sdk.umd.js"></script>
</head>
<body>
  <button id="quote-btn">Get Quote</button>
  <pre id="result"></pre>

  <script>
    const sdk = new VulcxSDK({ apiKey: "argy_your_api_key" });

    document.getElementById("quote-btn").addEventListener("click", async () => {
      try {
        const quote = await sdk.quote({
          inputMint: "So11111111111111111111111111111111111111112",
          outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
          amount: "1000000000",
          swapMode: "ExactIn",
        });
        document.getElementById("result").textContent = JSON.stringify(quote, null, 2);
      } catch (err) {
        document.getElementById("result").textContent = err.message;
      }
    });
  </script>
</body>
</html>
```

---

## ExactOut Mode

```typescript
const quote = await sdk.quote({
  inputMint: "So11111111111111111111111111111111111111112",
  outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  amount: "100000000", // I want exactly 100 USDC
  swapMode: "ExactOut",
  slippageBps: 100,
});

console.log(`Need ${quote.amountIn} lamports of SOL to get 100 USDC`);
```
