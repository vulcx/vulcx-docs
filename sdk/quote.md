---
title: "sdk.quote()"
description: "Get the best swap rate for a token pair with the Vulcx SDK — parameters, response schema, and price impact."
llmDescription: "Reference for sdk.quote() in the Vulcx TypeScript SDK. Documents QuoteRequest params (inputMint, outputMint, amount in smallest units, swapMode ExactIn/ExactOut, slippageBps default 50) and QuoteResponse fields (amountIn, amountOut, priceImpactBps, priceImpactPercent, priceImpactSeverity none/low/moderate/high/extreme, feeBps, otherAmountThreshold, routes RouteInfo array). Includes a token-decimals table (FOGO 9, USDC 6, FISH 6) and error cases. Fogo."
---

Find the best swap rate for a token pair. The aggregator searches across all supported DEXs and returns the optimal route.

```typescript
const quote = await sdk.quote(params: QuoteRequest): Promise<QuoteResponse>
```

---

## Parameters (`QuoteRequest`)

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `inputMint` | `string` | yes | -- | Input token mint address (base58) |
| `outputMint` | `string` | yes | -- | Output token mint address (base58) |
| `amount` | `string` | yes | -- | Amount in smallest token units (lamports for FOGO, base units for SPL) |
| `swapMode` | `"ExactIn" \| "ExactOut"` | yes | -- | `ExactIn`: specify input, get estimated output. `ExactOut`: specify desired output, get required input. |
| `slippageBps` | `number` | no | `50` | Slippage tolerance in basis points (1 bps = 0.01%) |

### Token Amounts

All amounts use the smallest token unit (no decimals):

| Token | Decimals | 1 token = |
|-------|----------|-----------|
| FOGO | 9 | `1000000000` |
| USDC | 6 | `1000000` |
| FISH | 6 | `1000000` |

---

## Response (`QuoteResponse`)

```typescript
const quote = await sdk.quote({
  inputMint: "So11111111111111111111111111111111111111112",
  outputMint: "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  amount: "1000000000",
  swapMode: "ExactIn",
  slippageBps: 50,
});
```

```json
{
  "inputMint": "So11111111111111111111111111111111111111112",
  "outputMint": "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG",
  "amountIn": "1000000000",
  "amountOut": "145320000",
  "priceImpactBps": 25,
  "priceImpactPercent": "0.25%",
  "priceImpactSeverity": "low",
  "priceImpactWarning": "Price impact is low",
  "feeBps": 25,
  "otherAmountThreshold": "144593400",
  "routes": [
    {
      "poolAddress": "HJPjoWUrhoZzkNfRpHuieeFk9WcZWjwy6PBjZ81ngndJ",
      "poolType": "Vortex",
      "percent": 100,
      "inputMint": "So11111111111111111111111111111111111111112",
      "outputMint": "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
    }
  ],
  "routePath": [
    "So11111111111111111111111111111111111111112",
    "uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
  ],
  "hopCount": 1
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `inputMint` | `string` | Input token mint address |
| `outputMint` | `string` | Output token mint address |
| `amountIn` | `string` | Input amount. For ExactIn: same as request. For ExactOut: calculated. |
| `amountOut` | `string` | Output amount. For ExactIn: calculated. For ExactOut: same as request. |
| `priceImpactBps` | `number` | Price impact in basis points |
| `priceImpactPercent` | `string` | Human-readable price impact (e.g. `"0.25%"`) |
| `priceImpactSeverity` | `PriceImpactSeverity` | `"none"` (&lt;0.1%), `"low"` (0.1-1%), `"moderate"` (1-3%), `"high"` (3-5%), `"extreme"` (&gt;5%) |
| `priceImpactWarning` | `string` | Warning message (empty if negligible) |
| `feeBps` | `number` | Total fee across all hops in basis points |
| `otherAmountThreshold` | `string` | Slippage-adjusted threshold. ExactIn: minimum output. ExactOut: maximum input. |
| `routes` | `RouteInfo[]` | Per-hop route details |
| `routePath` | `string[]` | Token mint path from input to output |
| `hopCount` | `number` | Number of swap hops (1 = direct, 2+ = multi-hop) |

### `RouteInfo`

| Field | Type | Description |
|-------|------|-------------|
| `poolAddress` | `string` | Pool address for this hop |
| `poolType` | `string` | DEX type (e.g. `"Vortex"`, `"Fluxbeam"`, `"Moonit"`) |
| `percent` | `number` | Percentage routed through this pool (100 for single route) |
| `inputMint` | `string` | Input mint for this hop |
| `outputMint` | `string` | Output mint for this hop |

---

## Errors

| Error | Condition |
|-------|-----------|
| `BadRequestError` | Invalid mint address, bad amount, invalid swap mode |
| `NoRouteError` | No liquidity path between the tokens |
| `AuthError` | Invalid or missing API key |
| `RateLimitError` | Too many requests (retried automatically) |

See [Error Handling](./error-handling.md) for details.

---

## Notes

- The engine automatically selects direct swap, multi-hop, or split routing based on available liquidity.
- Multi-hop routes go through intermediate tokens (typically FOGO or USDC) when no direct pool exists.
- Split routes divide liquidity across multiple pools for the same hop to reduce price impact.
- `otherAmountThreshold` is calculated as:
  - ExactIn: `amountOut * (10000 - slippageBps) / 10000`
  - ExactOut: `amountIn * 10000 / (10000 - slippageBps)`
