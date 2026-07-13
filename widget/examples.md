---
title: "Widget examples"
description: "Full vulcx-swap integration examples for HTML/CDN, React, Vue 3, Next.js, and Svelte."
llmDescription: "Complete Vulcx vulcx-swap Web Component examples for HTML/CDN, React with Wallet Adapter, Vue 3, Next.js (App Router), and Svelte, plus a light-theme custom-accent example."
---

Full integration examples for each framework.

---

## HTML / CDN

Complete standalone page with wallet connection:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Vulcx Swap</title>
  <script src="https://unpkg.com/@vulcx/widget/dist/vulcx-widget.umd.js"></script>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #0a0a0f;
    }
    .container { width: 440px; }
  </style>
</head>
<body>
  <div class="container">
    <vulcx-swap
      api-key="vulcx_your_api_key"
      default-input-mint="So11111111111111111111111111111111111111112"
      default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
      theme="dark"
    ></vulcx-swap>
  </div>

  <script>
    const widget = document.querySelector("vulcx-swap");

    widget.addEventListener("connect-wallet", async () => {
      if (!window.solana?.isPhantom) {
        alert("Please install Phantom wallet");
        return;
      }
      const resp = await window.solana.connect();
      widget.setWallet(resp.publicKey.toString());
    });

    widget.addEventListener("quote-update", (e) => {
      console.log("Quote:", e.detail.amountOut);
    });

    widget.addEventListener("swap-complete", (e) => {
      console.log("Swap built:", e.detail.transaction);
    });

    widget.addEventListener("swap-error", (e) => {
      console.error("Swap failed:", e.detail.error);
    });
  </script>
</body>
</html>
```

---

## React + Wallet Adapter

```tsx
"use client";

import { useEffect, useRef, useCallback } from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { useWalletModal } from "@solana/wallet-adapter-react-ui";
import "@vulcx/widget";
import type { VulcxSwapElement } from "@vulcx/widget";

export default function SwapPage() {
  const ref = useRef<VulcxSwapElement>(null);
  const { publicKey, connected } = useWallet();
  const { setVisible } = useWalletModal();

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.setWallet(connected && publicKey ? publicKey.toBase58() : "");
  }, [connected, publicKey]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const onConnect = () => setVisible(true);
    const onQuote = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      console.log("Quote:", detail.amountOut, "impact:", detail.priceImpactPercent);
    };
    const onSwap = (e: Event) => {
      console.log("Swap complete:", (e as CustomEvent).detail);
    };
    const onError = (e: Event) => {
      console.error("Swap error:", (e as CustomEvent).detail.error);
    };

    el.addEventListener("connect-wallet", onConnect);
    el.addEventListener("quote-update", onQuote);
    el.addEventListener("swap-complete", onSwap);
    el.addEventListener("swap-error", onError);

    return () => {
      el.removeEventListener("connect-wallet", onConnect);
      el.removeEventListener("quote-update", onQuote);
      el.removeEventListener("swap-complete", onSwap);
      el.removeEventListener("swap-error", onError);
    };
  }, [setVisible]);

  return (
    <div style={{ maxWidth: 460, margin: "0 auto", padding: 24 }}>
      <vulcx-swap
        ref={ref as any}
        api-key={process.env.NEXT_PUBLIC_VULCX_KEY}
        rpc-url="https://mainnet.fogo.io"
        theme="dark"
      />
    </div>
  );
}
```

TypeScript declaration (`global.d.ts`):

```typescript
declare namespace JSX {
  interface IntrinsicElements {
    "vulcx-swap": React.DetailedHTMLProps<
      React.HTMLAttributes<HTMLElement> & {
        "api-key"?: string;
        chain?: string;
        "base-url"?: string;
        "rpc-url"?: string;
        "default-input-mint"?: string;
        "default-output-mint"?: string;
        theme?: "dark" | "light";
      },
      HTMLElement
    >;
  }
}
```

---

## Vue 3

```vue
<template>
  <div class="swap-wrapper">
    <vulcx-swap
      ref="widgetRef"
      api-key="vulcx_your_api_key"
      default-input-mint="So11111111111111111111111111111111111111112"
      default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
      theme="dark"
      @connect-wallet="onConnectWallet"
      @quote-update="onQuoteUpdate"
      @swap-complete="onSwapComplete"
      @swap-error="onSwapError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import "@vulcx/widget";

const widgetRef = ref<HTMLElement | null>(null);

function onConnectWallet() {
  // Trigger your wallet adapter
  console.log("Connect wallet requested");
}

function onQuoteUpdate(e: CustomEvent) {
  console.log("Quote:", e.detail.amountOut);
}

function onSwapComplete(e: CustomEvent) {
  console.log("Swap:", e.detail);
}

function onSwapError(e: CustomEvent) {
  console.error("Error:", e.detail.error);
}

function setWallet(address: string) {
  (widgetRef.value as any)?.setWallet(address);
}
</script>

<style scoped>
.swap-wrapper {
  max-width: 460px;
  margin: 0 auto;
}
</style>
```

In `vite.config.ts`, tell Vue to treat `vulcx-swap` as a custom element:

```typescript
export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag === "vulcx-swap",
        },
      },
    }),
  ],
});
```

---

## Next.js (App Router)

```tsx
"use client";

import { useEffect, useRef } from "react";

export default function SwapWidget() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    import("@vulcx/widget");
  }, []);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const onConnect = () => {
      console.log("Connect wallet");
    };

    el.addEventListener("connect-wallet", onConnect);
    return () => el.removeEventListener("connect-wallet", onConnect);
  }, []);

  return (
    <vulcx-swap
      ref={ref}
      api-key="vulcx_your_api_key"
      theme="dark"
      default-input-mint="So11111111111111111111111111111111111111112"
      default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
    />
  );
}
```

---

## Svelte

```svelte
<script>
  import { onMount } from "svelte";

  let widgetEl;

  onMount(async () => {
    await import("@vulcx/widget");

    widgetEl.addEventListener("connect-wallet", () => {
      console.log("Connect wallet");
    });

    widgetEl.addEventListener("quote-update", (e) => {
      console.log("Quote:", e.detail);
    });
  });

  export function setWallet(address) {
    widgetEl?.setWallet(address);
  }
</script>

<vulcx-swap
  bind:this={widgetEl}
  api-key="vulcx_your_api_key"
  theme="dark"
/>
```

---

## Light Theme with Custom Accent

```html
<vulcx-swap
  api-key="vulcx_your_api_key"
  theme="light"
></vulcx-swap>

<style>
  vulcx-swap {
    --vulcx-accent: #6366f1;
    --vulcx-accent-hover: #818cf8;
    --vulcx-radius: 12px;
  }
</style>
```
