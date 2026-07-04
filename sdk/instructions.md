---
title: "sdk.instructions()"
description: "Get raw swap instructions to compose custom transactions — add tips, memos, or batch multiple swaps."
llmDescription: "Reference for sdk.instructions() in the Vulcx TypeScript SDK. Returns InstructionsResponse (RawInstruction array, RawAccountMeta, addressLookupTableAddresses) for composing custom transactions when you need memos/tips, account creation, or batched swaps. Includes a full example building a v0 VersionedTransaction with Address Lookup Tables, plus guidance on instructions() vs swap()."
---

Get raw swap instructions for composing custom transactions. Use this when you need to add custom instructions (tips, memos, etc.) or batch multiple swaps.

```typescript
const ixs = await sdk.instructions(params: InstructionsRequest): Promise<InstructionsResponse>
```

---

## Parameters (`InstructionsRequest`)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `userWallet` | `string` | yes | -- | User's wallet address (base58) |
| `inputMint` | `string` | yes | -- | Input token mint address |
| `outputMint` | `string` | yes | -- | Output token mint address |
| `amount` | `string` | yes | -- | Amount in smallest token units |
| `swapMode` | `"ExactIn" \| "ExactOut"` | yes | -- | Swap direction |
| `slippageBps` | `number` | no | `50` | Slippage tolerance in basis points |

---

## Response (`InstructionsResponse`)

```json
{
  "instructions": [
    {
      "programId": "ComputeBudget111111111111111111111111111111",
      "accounts": [],
      "data": "AgAAANCWAwA="
    },
    {
      "programId": "ArgyFuvk4S2vjC5XWuCWbcozjKwNrRzopLBJjCcTTWTH",
      "accounts": [
        { "publicKey": "...", "isSigner": true, "isWritable": true },
        { "publicKey": "...", "isSigner": false, "isWritable": false }
      ],
      "data": "base64-encoded-instruction-data"
    }
  ],
  "addressLookupTableAddresses": ["ALTaddress1...", "ALTaddress2..."],
  "amountIn": "1000000000",
  "amountOut": "145320000",
  "otherAmountThreshold": "144593400",
  "feeAmount": "100005",
  "hopCount": 1,
  "route": [
    "So11111111111111111111111111111111111111112",
    "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
  ],
  "pools": ["HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ"]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `instructions` | `RawInstruction[]` | Ordered list of Solana instructions |
| `addressLookupTableAddresses` | `string[]` | ALT addresses to include in the v0 transaction |
| `amountIn` | `string` | Input amount |
| `amountOut` | `string` | Estimated output amount |
| `otherAmountThreshold` | `string` | Slippage-adjusted threshold |
| `feeAmount` | `string` | Aggregator fee in output token units |
| `hopCount` | `number` | Number of swap hops |
| `route` | `string[]` | Token mint path |
| `pools` | `string[]` | Pool addresses used |

### `RawInstruction`

| Field | Type | Description |
|-------|------|-------------|
| `programId` | `string` | Program ID (base58) |
| `accounts` | `RawAccountMeta[]` | Account metas |
| `data` | `string` | Base64-encoded instruction data |

### `RawAccountMeta`

| Field | Type | Description |
|-------|------|-------------|
| `publicKey` | `string` | Account public key (base58) |
| `isSigner` | `boolean` | Whether the account must sign |
| `isWritable` | `boolean` | Whether the account is writable |

---

## Building a Transaction

After receiving the instructions, you build the transaction yourself:

```typescript
import {
  Connection,
  PublicKey,
  TransactionMessage,
  VersionedTransaction,
} from "@solana/web3.js";

const connection = new Connection("https://mainnet.fogo.io");

const ixs = await sdk.instructions({
  userWallet: wallet.publicKey.toBase58(),
  inputMint: "So11111111111111111111111111111111111111112",
  outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  amount: "1000000000",
  swapMode: "ExactIn",
});

// Fetch blockhash
const { blockhash, lastValidBlockHeight } =
  await connection.getLatestBlockhash();

// Resolve Address Lookup Tables
const altAccounts = await Promise.all(
  ixs.addressLookupTableAddresses.map((addr) =>
    connection.getAddressLookupTable(new PublicKey(addr))
  )
);
const lookupTables = altAccounts
  .map((a) => a.value)
  .filter((v) => v !== null);

// Convert to web3.js instruction format
const instructions = ixs.instructions.map((ix) => ({
  programId: new PublicKey(ix.programId),
  keys: ix.accounts.map((acc) => ({
    pubkey: new PublicKey(acc.publicKey),
    isSigner: acc.isSigner,
    isWritable: acc.isWritable,
  })),
  data: Buffer.from(ix.data, "base64"),
}));

// Build v0 transaction
const messageV0 = new TransactionMessage({
  payerKey: wallet.publicKey,
  recentBlockhash: blockhash,
  instructions,
}).compileToV0Message(lookupTables);

const tx = new VersionedTransaction(messageV0);
tx.sign([wallet]);

const sig = await connection.sendTransaction(tx);
```

---

## When to Use `instructions()` vs `swap()`

| Use case | Endpoint |
|----------|----------|
| Simple swap, let the API handle everything | `sdk.swap()` |
| Add custom instructions (tip, memo, etc.) | `sdk.instructions()` |
| Batch multiple swaps in one transaction | `sdk.instructions()` |
| Inspect accounts and data before signing | `sdk.instructions()` |
| Need lower latency (no blockhash fetch server-side) | `sdk.instructions()` |
