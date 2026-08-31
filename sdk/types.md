---
title: "SDK types reference"
description: "Every type exported from @vulcx/sdk — unions, config, quote, swap, and instructions."
llmDescription: "TypeScript types exported from @vulcx/sdk. Unions: SwapMode (ExactIn or ExactOut), PriceImpactSeverity (none/low/moderate/high/extreme). Config: SDKConfig. Quote: QuoteRequest, QuoteResponse, RouteInfo. Swap: SwapRequest, SwapResponse, SimulationResult. Plus instruction types."
---

All types exported from `@vulcx/sdk`.

---

## Unions

### `SwapMode`

```typescript
type SwapMode = "ExactIn" | "ExactOut";
```

### `PriceImpactSeverity`

```typescript
type PriceImpactSeverity = "none" | "low" | "moderate" | "high" | "extreme";
```

---

## Configuration

### `SDKConfig`

```typescript
interface SDKConfig {
  apiKey: string;
  baseUrl?: string;
  timeout?: number;
  retries?: number;
}
```

---

## Quote

### `QuoteRequest`

```typescript
interface QuoteRequest {
  inputMint: string;
  outputMint: string;
  amount: string;
  swapMode: SwapMode;
  slippageBps?: number;
}
```

### `QuoteResponse`

```typescript
interface QuoteResponse {
  inputMint: string;
  outputMint: string;
  amountIn: string;
  amountOut: string;
  priceImpactBps: number;
  priceImpactPercent: string;
  priceImpactSeverity: PriceImpactSeverity;
  priceImpactWarning: string;
  feeBps: number;
  routes: RouteInfo[];
  routePath: string[];
  hopCount: number;
  otherAmountThreshold: string;
  /** Firm-quote commitment ID — pass to swap()/instructions() to replay this
   * exact route at this price. Omitted when the quote can't be pinned. */
  quoteId?: string;
  /** How long quoteId stays redeemable, in ms. */
  validForMs?: number;
  /** How long quoteId stays redeemable with firm: true, in ms. */
  firmForMs?: number;
}
```

### `RouteInfo`

```typescript
interface RouteInfo {
  poolAddress: string;
  poolType: string;
  percent: number;
  inputMint: string;
  outputMint: string;
}
```

---

## Swap

### `SwapRequest`

```typescript
interface SwapRequest {
  userWallet: string;
  inputMint: string;
  outputMint: string;
  amount: string;
  swapMode: SwapMode;
  slippageBps?: number;
  skipSimulation?: boolean;
  /** Firm-quote ID from quote() — replays the exact quoted route. */
  quoteId?: string;
  /** Price-or-fail redemption (requires quoteId, within firmForMs). */
  firm?: boolean;
}
```

### `SwapResponse`

```typescript
interface SwapResponse {
  transaction: string;
  lastValidBlockHeight: number;
  amountIn: string;
  amountOut: string;
  minAmountOut?: string;
  maxAmountIn?: string;
  feeAmount: string;
  simulation?: SimulationResult;
  computeUnitsEstimate: number;
  route: string[];
  hopCount: number;
  pools: string[];
  isSplitRoute: boolean;
  splitPercents?: number[];
}
```

### `SimulationResult`

```typescript
interface SimulationResult {
  success: boolean;
  computeUnitsConsumed: number;
  computeUnitsTotal: number;
  logs: string[];
  error: string;
  slippageExceeded: boolean;
  insufficientFunds: boolean;
  accountsNeeded: string[];
}
```

---

## Instructions

### `InstructionsRequest`

```typescript
interface InstructionsRequest {
  userWallet: string;
  inputMint: string;
  outputMint: string;
  amount: string;
  swapMode: SwapMode;
  slippageBps?: number;
  /** Firm-quote ID from quote() — replays the exact quoted route. */
  quoteId?: string;
  /** Price-or-fail redemption (requires quoteId, within firmForMs). */
  firm?: boolean;
}
```

### `InstructionsResponse`

```typescript
interface InstructionsResponse {
  instructions: RawInstruction[];
  addressLookupTableAddresses: string[];
  amountIn: string;
  amountOut: string;
  otherAmountThreshold: string;
  feeAmount: string;
  hopCount: number;
  route: string[];
  pools: string[];
}
```

### `RawInstruction`

```typescript
interface RawInstruction {
  programId: string;
  accounts: RawAccountMeta[];
  data: string;
}
```

### `RawAccountMeta`

```typescript
interface RawAccountMeta {
  publicKey: string;
  isSigner: boolean;
  isWritable: boolean;
}
```

---

## Errors

### `VulcxError`

```typescript
class VulcxError extends Error {
  readonly statusCode: number;
  readonly body?: unknown;
}
```

### `BadRequestError`

```typescript
class BadRequestError extends VulcxError {} // statusCode: 400
```

### `AuthError`

```typescript
class AuthError extends VulcxError {} // statusCode: 401
```

### `NoRouteError`

```typescript
class NoRouteError extends VulcxError {} // statusCode: 404
```

### `RateLimitError`

```typescript
class RateLimitError extends VulcxError {} // statusCode: 429
```

### `QuoteStaleError`

```typescript
class QuoteStaleError extends VulcxError {} // statusCode: 409 — pinned route gone or firm price drifted
```

### `QuoteExpiredError`

```typescript
class QuoteExpiredError extends VulcxError {} // statusCode: 410 — quoteId past its TTL
```

### `ServerError`

```typescript
class ServerError extends VulcxError {} // statusCode: 500
```
