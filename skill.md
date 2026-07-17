---
name: vulcx-swap
description: Integrate Vulcx swap API on Fogo. Use for getting quotes, building swap transactions, getting raw instructions, redeeming firm quotes (quoteId, price-or-fail), and handling errors across Vortex, Fluxbeam, and Moonit bonding curves.
version: "1.4.0"
tags:
  - vulcx
  - fogo
  - swap
  - aggregator
  - defi
  - quote
  - routing
  - multi-hop
---

# Vulcx Swap API

**Base URL**: `https://api.vulcx.xyz`
**OpenAPI spec**: `https://docs.vulcx.xyz/api-reference/openapi.json`
**Full reference**: `https://docs.vulcx.xyz/llms-full.txt`

## Authentication

Every endpoint requires an API key **except** `GET /health` and `GET /api/v1/tokens`. Send it as:

- `Authorization: Bearer vulcx_your_key_here` on REST calls, or
- `?key=vulcx_your_key_here` query parameter — **required** for the WebSocket stream
  (`GET /api/v1/stream`), since a browser WS handshake can't carry custom headers.

```bash
curl "https://api.vulcx.xyz/api/v1/quote?inputMint=...&outputMint=...&amount=...&swapMode=ExactIn" \
  -H "Authorization: Bearer $VULCX_KEY"
```

Missing/invalid keys return `401 Unauthorized` (no key) or `403 Forbidden` (invalid/disabled/revoked
key). Keys are free during beta — see [Authentication](https://docs.vulcx.xyz/get-started/authentication) for how to get one.

## Chain Support

**Fogo** (5 max hops, Vortex/Fluxbeam/Moonit DEXs).

## Use / Do Not Use

Use when:
- The task involves swapping tokens on Fogo via Vulcx.
- The user needs a quote, swap transaction, or raw instructions.
- The user needs help debugging Vulcx API errors.

Do not use when:
- The task is generic blockchain development with no Vulcx API usage.
- The task involves other aggregators (Jupiter, etc.).

**Triggers**: `swap`, `quote`, `best route`, `token swap`, `vulcx`, `multi-hop`, `price impact`, `slippage`, `build transaction`, `raw instructions`, `firm quote`, `quoteId`, `price-or-fail`, `fogo`

## Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|:---:|---------|
| `/api/v1/quote` | GET | required | Get best route and estimated output |
| `/api/v1/swap` | POST | required | Build unsigned swap transaction |
| `/api/v1/instructions` | POST | required | Get raw instructions for custom tx |
| `/api/v1/cpi/route-accounts` | POST | required | Build the `route` instruction for on-chain CPI (PDA-signed) — Beta |
| `/api/v1/stream` | GET (WS) | required (`?key=`) | Live-updating quotes over WebSocket |
| `/api/v1/tokens` | GET | — | Curated list of well-known token mints |
| `/health` | GET | — | Service health check |

## Intent → Endpoint Decision Tree

### "I want to swap Token A for Token B"

```
1. GET /api/v1/quote
   params: inputMint, outputMint, amount, swapMode=ExactIn, slippageBps=50
   
2. Check response:
   - success=false → handle error (see Error Recovery)
   - priceImpactSeverity=high|extreme → warn user
   
3. POST /api/v1/swap
   body: { userWallet, inputMint, outputMint, amount, swapMode, slippageBps, quoteId (from step 1) }
   quoteId pins the exact quoted route + price (410 expired / 409 stale → re-quote, retry)
   
4. Check simulation:
   - simulation.insufficientFunds=true → show balance error
   - simulation.slippageExceeded=true → retry with fresh quote
   
5. Sign transaction (base64 decode → VersionedTransaction.deserialize → sign)
6. Submit (sendRawTransaction → confirmTransaction)
```

### "I want to get a price quote only"

```
1. GET /api/v1/quote
   params: inputMint, outputMint, amount, swapMode=ExactIn
   
2. Use response fields:
   - amountOut: estimated output
   - priceImpactPercent: price impact
   - feeBps: total fees
   - hopCount: number of hops (up to 5)
   - routes[]: detailed route info per hop
```

### "I want to compose swap with other instructions"

```
1. POST /api/v1/instructions
   body: { userWallet, inputMint, outputMint, amount, swapMode, slippageBps }
   
2. Build v0 transaction:
   - Fetch addressLookupTableAddresses via getAddressLookupTable()
   - Convert instructions[] to TransactionInstruction[]
   - Add your custom instructions before/after
   - Compile to V0Message with ALTs
   - Sign and submit
```

### "I want to call the swap from my own on-chain program (CPI)" — Beta

```
Use when ANOTHER on-chain program must swap atomically, signed by its PDA
(not a user wallet). See guide: /guides/onchain-cpi

1. POST /api/v1/cpi/route-accounts
   body: { authority (your program PDA), inputMint, outputMint, amount, swapMode, slippageBps,
           allowedIntermediateMints? (corridor, max 16), maxHops? (1 = direct only),
           excludeDexes? (["vortex"|"fluxbeam"|"moonit"]; excluding moonit lifts the
           authority-writable requirement), referrer? }
   → data.routeInstruction (forward its accounts into your `route` CPI)
   → data.requiredTokenAccounts (ATAs your PDA must own + fund first; no wrap/unwrap emitted)
   → data.referrerAta (when referrer set — must pre-exist)
   → data.addressLookupTableAddresses
   Constrained requests bypass caches, never split; no route inside constraints → 404.
   Multi-hop ExactOut → 400 (use ExactIn-with-buffer).

2. On-chain: invoke_signed into `route` with your PDA seeds via the `vulcx-cpi` crate
   (RouteAccounts, RouteArgs, invoke_route_signed; `api` feature parses the endpoint JSON).
   Split routes are not supported (400).

3. Optional: stream templates instead of polling — WS op
   {"op":"subscribe_route","routes":[{authority,inputMint,outputMint,amount,...constraints}]}
   pushes {"type":"route","seq","slot","route":{...}} only when the template changes (max 32/conn).
```

### "I want to buy exactly X amount of a token"

```
Same as swap flow, but use swapMode=ExactOut:
- amount = desired output amount in smallest units
- Response amountIn = calculated input needed
- Response maxAmountIn = maximum you'll spend (slippage-adjusted)
```

### "I want the price I quoted, or nothing" (firm quotes)

```
1. GET /api/v1/quote → data.quoteId, data.validForMs (~3000), data.firmForMs (~400)

2. Within validForMs: POST /swap or /instructions with quoteId
   → replays the EXACT quoted route; min-out anchors to the quoted price (user slippage applies)

3. Within firmForMs: add "firm": true
   → slippage collapses to the server firm margin (~10 bps); price-or-fail
   → 409 = price drifted past margin (no tx built, no fee spent) → re-quote, retry immediately

Errors: 410 quote expired · 409 route gone/drifted · 403 quoteId from another key ·
400 pair/amount/swapMode mismatch or firm without quoteId.
WS stream pushes {"type":"invalidate","quoteId"} when a broadcast quote drifts past the margin.
Firm is price-or-fail, NOT a fill guarantee. The firm window is sub-second — machine flows only.
```

## Parameter Reference

### GET /api/v1/quote

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| inputMint | string | yes | — | Input token mint (base58) |
| outputMint | string | yes | — | Output token mint (base58) |
| amount | string | yes | — | Amount in smallest units |
| swapMode | string | yes | — | `ExactIn` or `ExactOut` |
| slippageBps | integer | no | 50 | Slippage tolerance (1 bps = 0.01%) |

### POST /api/v1/swap

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| userWallet | string | yes | — | Signer wallet address (base58) |
| inputMint | string | yes | — | Input token mint |
| outputMint | string | yes | — | Output token mint |
| amount | string | yes | — | Amount in smallest units |
| swapMode | string | yes | — | `ExactIn` or `ExactOut` |
| slippageBps | integer | no | 50 | Slippage tolerance |
| skipSimulation | boolean | no | false | Skip pre-flight simulation |
| quoteId | string | no | — | Firm-quote ID from /quote — replays the exact quoted route at the quoted price |
| firm | boolean | no | false | Price-or-fail redemption (requires quoteId, within firmForMs) |

### POST /api/v1/instructions

Same as `/swap` without `skipSimulation` (`quoteId` and `firm` included), plus:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| referrer | string | no | -- | Referrer wallet — earns the on-chain referral fee share (also on /swap) |
| sessionAccount | string | no | -- | Fogo session account: returns ONE session-shaped route ix, no ATA-create/wrap ixs; response gains requiredTokenAccounts; Vortex-V1-only |

## Response Schemas

### QuoteResponse (GET /quote → data)

```json
{
  "inputMint": "string",
  "outputMint": "string",
  "amountIn": "string",
  "amountOut": "string",
  "priceImpactBps": 0,
  "priceImpactPercent": "string",
  "priceImpactSeverity": "none|low|moderate|high|extreme",
  "priceImpactWarning": "string",
  "feeBps": 0,
  "routes": [{ "poolAddress": "string", "poolType": "string", "percent": 0, "inputMint": "string", "outputMint": "string" }],
  "routePath": ["string"],
  "hopCount": 0,
  "otherAmountThreshold": "string",
  "quoteId": "q_hex (omitted when unpinnable, e.g. split routes)",
  "validForMs": 3000,
  "firmForMs": 400,
  "quoteSignature": "base58 Ed25519 over vulcx-quote-v1|quoteId|inputMint|outputMint|amountIn|amountOut|exactIn|expiresAtUnixMs (when signing enabled; key at GET /.well-known/vulcx-quote-signer)",
  "quoteExpiresAtMs": 0
}
```

### SwapResponse (POST /swap → data)

```json
{
  "transaction": "base64-string",
  "lastValidBlockHeight": 0,
  "amountIn": "string",
  "amountOut": "string",
  "minAmountOut": "string (ExactIn only)",
  "maxAmountIn": "string (ExactOut only)",
  "feeAmount": "string",
  "simulation": { "success": true, "logs": [], "computeUnitsConsumed": 0, "error": "", "insufficientFunds": false, "slippageExceeded": false },
  "computeUnitsEstimate": 0,
  "route": ["string"],
  "hopCount": 0,
  "pools": ["string"],
  "isSplitRoute": false,
  "splitPercents": [0]
}
```

### InstructionsResponse (POST /instructions → data)

```json
{
  "amountIn": "string",
  "amountOut": "string",
  "otherAmountThreshold": "string",
  "feeAmount": "string",
  "route": ["string"],
  "hopCount": 0,
  "pools": ["string"],
  "instructions": [{ "programId": "base58", "data": "base64", "accounts": [{ "publicKey": "base58", "isSigner": false, "isWritable": false }] }],
  "addressLookupTableAddresses": ["string"],
  "requiredTokenAccounts": ["session mode only: userWallet ATAs that must pre-exist, [input, ...intermediates, output]"]
}
```

## Error Recovery

| Error | HTTP | Recovery |
|-------|------|----------|
| `missing api key` | 401 | Add `Authorization: Bearer <key>` (or `?key=` for the WS stream) |
| `invalid api key` | 403 | Key is invalid, disabled, or revoked — request/rotate a key |
| `no route found` | 404 | Try smaller amount, different slippage, or check token support |
| `no pool found` | 404 | Token may not have listed pools |
| `insufficient liquidity` | 400 | Reduce swap amount |
| `invalid inputMint` | 400 | Verify base58 public key format |
| `invalid user wallet` | 400 | Verify wallet address |
| `simulation failed` | 500 | Check simulation.logs, verify balance |
| `rate limit exceeded` | 429 | Exponential backoff: 1s, 2s, 4s. Max 3 retries |
| `quote expired: request a fresh quote` | 410 | quoteId past its TTL — re-quote, retry with the new quoteId |
| `quoted route is no longer available: request a fresh quote` | 409 | Route gone, or firm price drifted past margin — re-quote |
| `quoteId was issued to a different api key` | 403 | Re-quote with your own key |
| `firm redemption requires a quoteId` | 400 | Include quoteId when sending firm: true |
| `SlippageExceeded` (on-chain) | — | Get fresh quote, rebuild transaction |
| `BlockhashExpired` (on-chain) | — | Rebuild transaction from scratch |

## Common Token Mints

| Token | Mint | Decimals |
|-------|------|----------|
| FOGO | `So11111111111111111111111111111111111111112` | 9 |
| USDC | `uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG` | 6 |

## Rate Limits

Limits are per API key by plan — free: 5 requests/second sustained, burst 10 (all beta keys); pro: 50 rps; scale: 150 rps; enterprise: 500 rps.
