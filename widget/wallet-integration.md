---
title: "Widget wallet integration"
description: "Plug any wallet into vulcx-swap via setWallet() and the connect-wallet event — adapter, Phantom, balances."
llmDescription: "Wallet integration for the Vulcx vulcx-swap Web Component. The widget bundles no wallet adapter; it exposes setWallet(address) and a connect-wallet event. Covers wiring the Solana Wallet Adapter (React), Phantom in vanilla JS, and displaying balances. Also covers Fogo Sessions firm mode: setSession({sessionAccount, walletAddress, sendInstructions}) attaches a VulcxSessionAdapter — swaps then redeem the displayed quote firm (price-or-fail, POST /instructions with firm:true and sessionAccount), signed by the session key and paid by the paymaster with no wallet popup; swap-complete emits {signature, session:true, firm}; session routes are Vortex-V1-only and require pre-existing ATAs (requiredTokenAccounts)."
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
<script src="https://unpkg.com/@vulcx/widget/dist/vulcx-widget.umd.js"></script>

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

---

## Fogo Sessions — firm mode, no wallet popup

If your app has an established [Fogo session](https://docs.fogo.io) (e.g. via
`@fogo/sessions-sdk-react`), hand it to the widget with `setSession()` instead of `setWallet()`.
While a session is attached, swaps run in **firm (price-or-fail) mode**: the widget redeems the
displayed quote via `POST /instructions` with `firm: true`, your session sender signs with the
session key, and the paymaster pays — no wallet popup, price-locked to what the user saw.

```typescript
import type { VulcxSessionAdapter } from "@vulcx/widget";

const widget = document.querySelector("vulcx-swap")!;

widget.setSession({
  sessionAccount: session.sessionAccount.toBase58(), // the session key's account
  walletAddress: session.walletAddress.toBase58(),   // the real user (owns the ATAs)
  async sendInstructions(instructions, luts) {
    // Sign with the session key + submit through the paymaster; return the signature.
    return await session.sendTransaction(instructions, { lookupTables: luts });
  },
} satisfies VulcxSessionAdapter);

// Detach (falls back to normal wallet flow):
widget.setSession(null);
```

Details worth knowing:

- **Firm windows are sub-second** (~400 ms). Session sends make them reachable because there's no
  human signing step. If the window lapses mid-click, the widget re-quotes once and redeems the
  fresh quote immediately — the UI always shows the price that will execute.
- The `swap-complete` event's detail becomes `{ signature, session: true, firm, amountIn,
  amountOut, route, pools }` — the widget itself submitted the transaction, so there's nothing
  left for the host to sign.
- Session routes are currently **Vortex-V1-only**, and the API emits no ATA-create or SOL-wrap
  instructions in session mode — the user's ATAs must exist (the response's
  `requiredTokenAccounts` lists them).
