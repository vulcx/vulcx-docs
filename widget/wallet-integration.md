---
title: "Widget wallet integration"
description: "Plug any wallet into vulcx-swap via setWallet() and the connect-wallet event — adapter, Phantom, balances."
llmDescription: "Wallet integration for the Vulcx vulcx-swap Web Component. The widget bundles no wallet adapter; it exposes setWallet(address) and a connect-wallet event. Covers wiring the Solana Wallet Adapter (React), Phantom in vanilla JS, and displaying balances."
---

The widget does not bundle a wallet adapter. Instead, it exposes a `setWallet()` method and a `connect-wallet` event so you can plug in any wallet solution.

---

## How It Works

1. User clicks "Swap" (or "Connect") with no wallet set
2. Widget fires `connect-wallet` event
3. Your app handles the event, connects the wallet, and calls `widget.setWallet(address)`
4. Widget loads balances and enables swapping

---

## `setWallet(address)`

Set the wallet address programmatically. When called with a non-empty address, the widget fetches native FOGO balance and SPL token balances via the configured `rpc-url`.

```javascript
const widget = document.querySelector("vulcx-swap");
widget.setWallet("9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM");
```

To disconnect:

```javascript
widget.setWallet("");
```

---

## `connect-wallet` Event

Fired when the user clicks the primary button but no wallet is connected. Listen for this to trigger your wallet adapter.

```javascript
const widget = document.querySelector("vulcx-swap");

widget.addEventListener("connect-wallet", async () => {
  const wallet = await connectWallet(); // your wallet adapter
  widget.setWallet(wallet.publicKey.toString());
});
```

---

## Solana Wallet Adapter (React)

```tsx
"use client";

import { useEffect, useRef } from "react";
import { useWallet } from "@solana/wallet-adapter-react";
import { useWalletModal } from "@solana/wallet-adapter-react-ui";
import "@vulcx/widget";

export default function SwapWidget() {
  const ref = useRef<HTMLElement>(null);
  const { publicKey, connected } = useWallet();
  const { setVisible } = useWalletModal();

  // Sync wallet state to widget
  useEffect(() => {
    const el = ref.current as any;
    if (!el) return;
    if (connected && publicKey) {
      el.setWallet(publicKey.toBase58());
    } else {
      el.setWallet("");
    }
  }, [connected, publicKey]);

  // Handle connect-wallet event
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const handler = () => setVisible(true);
    el.addEventListener("connect-wallet", handler);
    return () => el.removeEventListener("connect-wallet", handler);
  }, [setVisible]);

  return (
    <vulcx-swap
      ref={ref}
      api-key="vulcx_your_api_key"
      theme="dark"
    />
  );
}
```

---

## Phantom (Vanilla JS)

```html
<script src="https://cdn.vulcx.xyz/vulcx-widget.umd.js"></script>

<vulcx-swap
  api-key="vulcx_your_api_key"
  theme="dark"
></vulcx-swap>

<script>
  const widget = document.querySelector("vulcx-swap");

  widget.addEventListener("connect-wallet", async () => {
    if (!window.solana?.isPhantom) {
      window.open("https://phantom.app/", "_blank");
      return;
    }
    const resp = await window.solana.connect();
    widget.setWallet(resp.publicKey.toString());
  });

  // Auto-connect if already approved
  if (window.solana?.isPhantom) {
    window.solana.connect({ onlyIfTrusted: true })
      .then((resp) => widget.setWallet(resp.publicKey.toString()))
      .catch(() => {});
  }
</script>
```

---

## Balance Display

Once `setWallet()` is called with a valid address, the widget automatically:

1. Fetches native FOGO balance via `getBalance` RPC call
2. Fetches all SPL token balances via `getTokenAccountsByOwner`
3. Displays balances next to the selected input/output tokens
4. Enables HALF and MAX buttons for quick amount entry

The RPC endpoint used is configured via the `rpc-url` attribute (defaults to `https://mainnet.fogo.io/`).
