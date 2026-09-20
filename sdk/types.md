---
title: "SDK types reference"
description: "Every type exported from @vulcx/sdk — unions, config, quote, swap, and instructions."
llmDescription: "TypeScript types exported from @vulcx/sdk (0.7.1). Unions: SwapMode (ExactIn or ExactOut), PriceImpactSeverity (none/low/moderate/high/extreme). Config: SDKConfig, whose apiKey is OPTIONAL — keyless calls are served on the anonymous per-IP tier. Quote: QuoteRequest, QuoteResponse (amountIn is the amount actually routed and can be a partial fill; quoteId/validForMs/firmForMs/quoteExpiresAtMs/quoteSignature/contextSlot/dataAgeMs), RouteInfo. Swap: SwapRequest (integratorFeeBps + referrer for the caller's own fee, sessionAccount for Fogo Sessions), SwapResponse (platformFeeBps/Amount and integratorFeeBps/Amount alongside the pools' feeAmount; splitPercents is a base64 string), SimulationResult. Instructions: InstructionsRequest, InstructionsResponse (requiredTokenAccounts in session mode, including the fee accounts), RawInstruction. Errors: APIErrorBody, whose code is the stable contract and error is prose."
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
  /** Optional: keyless calls are served on the anonymous per-IP tier. */
  apiKey?: string;
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
  /** The amount actually routed — smaller than the one you asked for when
   * the pools cannot absorb the full size (a partial fill). */
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
  /** Wall-clock expiry of quoteId, epoch ms. */
  quoteExpiresAtMs?: number;
  /** Ed25519 signature over the quote, for callers that verify it. */
  quoteSignature?: string;
  /** Slot the pool state was read at, and how old it was when priced. */
  contextSlot?: number;
  dataAgeMs?: number;
  isSplitRoute?: boolean;
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
  /** Your own fee in bps, kept in full. Needs `referrer`, and adds to the
   * protocol rate rather than sharing it. Omit to use the key's default. */
  integratorFeeBps?: number;
  /** Wallet the integrator fee is paid to. */
  referrer?: string;
  /** Fogo Sessions: the session account signs the route instead of the
   * wallet. The build then ships no ATA-create or wrap instructions. */
  sessionAccount?: string;
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
  /** The DEX pools' own fee, in INPUT token units — not Vulcx's cut. */
  feeAmount: string;
  /** The protocol's rate and what it took, in output units. */
  platformFeeBps: number;
  platformFeeAmount: string;
  /** Your rate and what it paid you, in output units. */
  integratorFeeBps: number;
  integratorFeeAmount: string;
  simulation?: SimulationResult;
  computeUnitsEstimate: number;
  route: string[];
  hopCount: number;
  pools: string[];
  isSplitRoute: boolean;
  /** Base64 split-percent blob, not an array. */
  splitPercents?: string;
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
  /** The DEX pools' own fee. Vulcx's cut is platformFeeAmount. */
  feeAmount: string;
  platformFeeBps: number;
  platformFeeAmount: string;
  integratorFeeBps: number;
  integratorFeeAmount: string;
  hopCount: number;
  route: string[];
  pools: string[];
  /** Session mode: accounts that must already exist, because a session
   * build emits no create instructions — the route ATAs and the fee
   * accounts the swap pays into. */
  requiredTokenAccounts?: string[];
  contextSlot?: number;
  dataAgeMs?: number;
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
