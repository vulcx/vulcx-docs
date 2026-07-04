---
title: "Widget events"
description: "Custom events from vulcx-swap: quote-update, swap-initiated, swap-complete, swap-error, connect-wallet."
llmDescription: "Event reference for the Vulcx vulcx-swap Web Component. Documents quote-update (QuoteResponse), swap-initiated (inputMint, outputMint, amount), swap-complete (SwapResponse), swap-error (error string), and connect-wallet. All events bubble and are composed so they cross the shadow DOM. Includes React and Vue listener examples."
---

The `<vulcx-swap>` element dispatches custom events at key points in the swap lifecycle. All events have `bubbles: true` and `composed: true`, so they cross the shadow DOM boundary.

---

## Event Reference

| Event | Fired when | `detail` type |
|-------|-----------|---------------|
| `quote-update` | A new quote is fetched | `QuoteResponse` |
| `swap-initiated` | User clicks "Swap" and the request starts | `{ inputMint: string, outputMint: string, amount: string }` |
| `swap-complete` | Swap transaction is built successfully | `SwapResponse` |
| `swap-error` | Swap request fails | `{ error: string }` |
| `connect-wallet` | User clicks the button without a wallet connected | `{}` |

---

## `quote-update`

Fired every time a new quote loads (after the 400ms debounce).

```typescript
interface QuoteUpdateDetail {
  inputMint: string;
  outputMint: string;
  amountIn: string;
  amountOut: string;
  priceImpactBps: number;
  priceImpactPercent: string;
  priceImpactSeverity: "none" | "low" | "moderate" | "high" | "extreme";
  priceImpactWarning: string;
  feeBps: number;
  routes: Array<{
    poolAddress: string;
    poolType: string;
    percent: number;
    inputMint: string;
    outputMint: string;
  }>;
  routePath: string[];
  hopCount: number;
  otherAmountThreshold: string;
}
```

```javascript
widget.addEventListener("quote-update", (e) => {
  console.log("Output:", e.detail.amountOut);
  console.log("Impact:", e.detail.priceImpactPercent);
  console.log("Route:", e.detail.routes.map(r => r.poolType).join(" → "));
});
```

---

## `swap-initiated`

Fired when the user clicks "Swap" and the SDK request begins. Use this for analytics or loading states.

```typescript
interface SwapInitiatedDetail {
  inputMint: string;
  outputMint: string;
  amount: string;
}
```

```javascript
widget.addEventListener("swap-initiated", (e) => {
  console.log("Swapping", e.detail.amount, "from", e.detail.inputMint);
});
```

---

## `swap-complete`

Fired when the swap transaction is built successfully. The `detail` contains the full `SwapResponse` including the base64 transaction.

```typescript
interface SwapCompleteDetail {
  transaction: string;
  lastValidBlockHeight: number;
  amountIn: string;
  amountOut: string;
  minAmountOut?: string;
  feeAmount: string;
  route: string[];
  hopCount: number;
  pools: string[];
}
```

```javascript
widget.addEventListener("swap-complete", (e) => {
  console.log("Swap built:", e.detail.amountIn, "→", e.detail.amountOut);
  // Sign and submit e.detail.transaction with your wallet
});
```

---

## `swap-error`

Fired when the swap request fails.

```typescript
interface SwapErrorDetail {
  error: string;
}
```

```javascript
widget.addEventListener("swap-error", (e) => {
  console.error("Swap failed:", e.detail.error);
});
```

---

## `connect-wallet`

Fired when the user clicks the primary button but no wallet is connected. Use this to trigger your wallet adapter's connect flow.

```typescript
interface ConnectWalletDetail {} // empty
```

```javascript
widget.addEventListener("connect-wallet", async () => {
  const wallet = await connectWallet(); // your wallet adapter
  widget.setWallet(wallet.publicKey.toString());
});
```

See [Wallet Integration](./wallet-integration.md) for full patterns.

---

## Listening in Frameworks

### React

```tsx
import { useEffect, useRef } from "react";
import "@vulcx/widget";

function SwapWidget() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const onQuote = (e: Event) => {
      console.log("Quote:", (e as CustomEvent).detail);
    };
    el.addEventListener("quote-update", onQuote);
    return () => el.removeEventListener("quote-update", onQuote);
  }, []);

  return <vulcx-swap ref={ref} api-key="argy_..." />;
}
```

### Vue

```vue
<template>
  <vulcx-swap
    api-key="argy_..."
    @quote-update="onQuote"
    @swap-complete="onSwap"
    @connect-wallet="onConnect"
  />
</template>

<script setup>
import "@vulcx/widget";

function onQuote(e) { console.log(e.detail); }
function onSwap(e) { console.log(e.detail); }
function onConnect() { /* trigger wallet connect */ }
</script>
```
