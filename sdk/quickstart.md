---
title: "SDK quickstart"
description: "Install @vulcx/sdk and run your first Fogo swap — quote, build, sign, submit — in under five minutes."
llmDescription: "Quickstart for the @vulcx/sdk TypeScript SDK. Covers npm install, initializing VulcxSDK, calling sdk.quote() for a FOGO to USDC quote on Fogo, building an unsigned transaction with sdk.swap(), and signing/submitting with @solana/web3.js VersionedTransaction. Fogo."
---

Get a quote and execute a swap in under 5 minutes.

---

## Install

```bash
npm install @vulcx/sdk
```

Or via CDN (exposes `window.VulcxSDK`):

```html
<script src="https://unpkg.com/@vulcx/sdk/dist/index.umd.js"></script>
```

---

## 1. Initialize

```typescript
import { VulcxSDK } from "@vulcx/sdk";

const sdk = new VulcxSDK({
  apiKey: "vulcx_your_api_key",
});
```

---

## 2. Get a Quote

```typescript
const quote = await sdk.quote({
  inputMint: "So11111111111111111111111111111111111111112",
  outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  amount: "1000000000", // 1 FOGO
  swapMode: "ExactIn",
  slippageBps: 50,
});

console.log(`${quote.amountOut} USDC, impact: ${quote.priceImpactPercent}`);
```

---

## 3. Build a Swap Transaction

```typescript
const swap = await sdk.swap({
  userWallet: "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
  inputMint: "So11111111111111111111111111111111111111112",
  outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  amount: "1000000000",
  swapMode: "ExactIn",
  slippageBps: 50,
});
```

---

## 4. Sign and Submit

```typescript
import { Connection, VersionedTransaction } from "@solana/web3.js";

const connection = new Connection("https://mainnet.fogo.io");

const tx = VersionedTransaction.deserialize(
  Buffer.from(swap.transaction, "base64")
);
tx.sign([wallet]); // your Keypair or wallet adapter

const sig = await connection.sendTransaction(tx);
await connection.confirmTransaction({
  signature: sig,
  lastValidBlockHeight: swap.lastValidBlockHeight,
  blockhash: tx.message.recentBlockhash,
});

console.log("Swap confirmed:", sig);
```

---

## Next Steps

- [Configuration](./configuration.md) -- all `SDKConfig` options
- [Quote](./quote.md) -- full `quote()` reference
- [Swap](./swap.md) -- full `swap()` reference with sign+submit patterns
- [Error Handling](./error-handling.md) -- handling rate limits, auth errors, no routes
- [Examples](./examples.md) -- React, Next.js, Node.js, and CDN examples
