---
title: "sdk.swap()"
description: "Build an unsigned, ready-to-sign swap transaction with the Vulcx SDK, then sign and submit it."
llmDescription: "Reference for sdk.swap() in the Vulcx TypeScript SDK. Documents SwapRequest params and SwapResponse (base64 transaction, lastValidBlockHeight, amountIn/amountOut, SimulationResult). Shows signing and submitting with @solana/web3.js VersionedTransaction and with a React wallet adapter. Fogo."
---

Build an unsigned swap transaction ready to be signed and submitted to the network.

```typescript
const swap = await sdk.swap(params: SwapRequest): Promise<SwapResponse>
```

---

## Parameters (`SwapRequest`)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `userWallet` | `string` | yes | -- | User's wallet address (base58). Must have sufficient balance. |
| `inputMint` | `string` | yes | -- | Input token mint address |
| `outputMint` | `string` | yes | -- | Output token mint address |
| `amount` | `string` | yes | -- | Amount in smallest token units |
| `swapMode` | `"ExactIn" \| "ExactOut"` | yes | -- | Swap direction |
| `slippageBps` | `number` | no | `50` | Slippage tolerance in basis points |
| `skipSimulation` | `boolean` | no | `false` | Skip pre-flight simulation. Faster but no validation. |

---

## Response (`SwapResponse`)

```json
{
  "transaction": "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAHEAo...",
  "lastValidBlockHeight": 245832190,
  "amountIn": "1000000000",
  "amountOut": "145320000",
  "minAmountOut": "144593400",
  "feeAmount": "0",
  "simulation": {
    "success": true,
    "computeUnitsConsumed": 85000,
    "computeUnitsTotal": 200000,
    "logs": ["Program ... invoke", "..."],
    "error": "",
    "slippageExceeded": false,
    "insufficientFunds": false,
    "accountsNeeded": []
  },
  "computeUnitsEstimate": 85000,
  "route": [
    "So11111111111111111111111111111111111111112",
    "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
  ],
  "hopCount": 1,
  "pools": ["HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"],
  "isSplitRoute": false
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `transaction` | `string` | Base64-encoded unsigned v0 transaction |
| `lastValidBlockHeight` | `number` | Transaction expires after this block height (~60 seconds) |
| `amountIn` | `string` | Input amount |
| `amountOut` | `string` | Estimated output amount |
| `minAmountOut` | `string?` | Minimum output after slippage (ExactIn). Transaction reverts if actual output is less. |
| `maxAmountIn` | `string?` | Maximum input after slippage (ExactOut). Transaction reverts if actual input exceeds this. |
| `feeAmount` | `string` | Aggregator fee in output token units |
| `simulation` | `SimulationResult?` | Simulation result (`null` if `skipSimulation=true`) |
| `computeUnitsEstimate` | `number?` | Estimated compute units |
| `route` | `string[]` | Token mint path in execution order |
| `hopCount` | `number` | Number of swap hops |
| `pools` | `string[]` | Pool addresses used, in execution order |
| `isSplitRoute` | `boolean?` | Whether liquidity is split across pools |
| `splitPercents` | `number[]?` | Per-pool percentage split (only if `isSplitRoute=true`) |

### `SimulationResult`

| Field | Type | Description |
|-------|------|-------------|
| `success` | `boolean` | Whether simulation passed |
| `computeUnitsConsumed` | `number` | CU consumed |
| `computeUnitsTotal` | `number` | CU limit |
| `logs` | `string[]` | Transaction logs |
| `error` | `string` | Error message if simulation failed |
| `slippageExceeded` | `boolean` | Whether slippage check failed |
| `insufficientFunds` | `boolean` | Whether wallet has insufficient balance |
| `accountsNeeded` | `string[]` | Missing accounts (e.g. ATAs that need creation) |

---

## Sign and Submit

After receiving the `SwapResponse`, deserialize, sign, and submit the transaction.

### With `@solana/web3.js`

```typescript
import { Connection, VersionedTransaction, Keypair } from "@solana/web3.js";

const connection = new Connection("https://mainnet.fogo.io");
const wallet = Keypair.fromSecretKey(/* ... */);

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
const confirmation = await connection.confirmTransaction({
  signature: sig,
  lastValidBlockHeight: swap.lastValidBlockHeight,
  blockhash: tx.message.recentBlockhash,
});

if (confirmation.value.err) {
  console.error("Transaction failed:", confirmation.value.err);
} else {
  console.log("Swap confirmed:", sig);
}
```

### With Wallet Adapter (React)

```typescript
import { useWallet, useConnection } from "@solana/wallet-adapter-react";
import { VersionedTransaction } from "@solana/web3.js";

const { publicKey, signTransaction } = useWallet();
const { connection } = useConnection();

const swap = await sdk.swap({
  userWallet: publicKey.toBase58(),
  inputMint: "So11111111111111111111111111111111111111112",
  outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  amount: "1000000000",
  swapMode: "ExactIn",
});

const tx = VersionedTransaction.deserialize(
  Buffer.from(swap.transaction, "base64")
);
const signed = await signTransaction(tx);
const sig = await connection.sendRawTransaction(signed.serialize());
```

---

## Notes

- The transaction includes automatic ATA (Associated Token Account) creation if the user doesn't have token accounts for the swap tokens.
- Compute budget is set based on hop count and DEX complexity.
- Address Lookup Tables are used to keep the transaction within the network's size limits.
- Submit the transaction quickly -- it expires after `lastValidBlockHeight` (~60 seconds).
