---
title: "Widget attributes"
description: "Every HTML attribute on vulcx-swap: api-key, chain, base-url, default mints, theme, and dynamic updates."
llmDescription: "Attribute reference for the Vulcx vulcx-swap Web Component: api-key (required), chain (solana or fogo, default solana), base-url, default-input-mint, default-output-mint, theme (dark or light), rpc-url. Covers dynamically updating attributes and examples (minimal, pre-selected SOL to USDC, self-hosted with custom RPC, Fogo chain)."
---

All HTML attributes accepted by the `<vulcx-swap>` element.

---

## Reference

| Attribute | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `api-key` | `string` | -- | yes | Your Vulcx API key. Used to authenticate SDK requests. |
| `chain` | `"solana" \| "fogo"` | `"solana"` | no | Target chain. Determines which DEX markets are searched. |
| `base-url` | `string` | `"https://api.vulcx.xyz"` | no | API base URL override. Use for self-hosted instances. |
| `rpc-url` | `string` | `"https://mainnet.fogo.io/"` | no | Solana JSON-RPC endpoint for balance queries. The widget calls `getBalance` and `getTokenAccountsByOwner` against this URL. |
| `default-input-mint` | `string` | -- | no | Pre-selected input token mint address. |
| `default-output-mint` | `string` | -- | no | Pre-selected output token mint address. |
| `theme` | `"dark" \| "light"` | `"dark"` | no | Color theme. See [Theming](./theming.md) for CSS variable overrides. |

---

## Dynamic Updates

All attributes are reactive. Changing them after mount updates the widget:

```javascript
const widget = document.querySelector("vulcx-swap");

// Switch to Fogo chain
widget.setAttribute("chain", "fogo");

// Point to a different API
widget.setAttribute("base-url", "http://localhost:8080");

// Change RPC endpoint
widget.setAttribute("rpc-url", "https://mainnet.fogo.io");

// Switch theme
widget.setAttribute("theme", "light");
```

When `api-key`, `chain`, or `base-url` change, the widget re-creates the internal SDK client. When `rpc-url` changes, subsequent balance queries use the new endpoint.

---

## Examples

### Minimal

```html
<vulcx-swap api-key="argy_your_api_key"></vulcx-swap>
```

### Pre-selected tokens (SOL to USDC)

```html
<vulcx-swap
  api-key="argy_your_api_key"
  default-input-mint="So11111111111111111111111111111111111111112"
  default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
></vulcx-swap>
```

### Self-hosted with custom RPC

```html
<vulcx-swap
  api-key="any-value"
  base-url="http://localhost:8080"
  rpc-url="https://mainnet.fogo.io"
  chain="solana"
  theme="light"
></vulcx-swap>
```

### Fogo chain

```html
<vulcx-swap
  api-key="argy_your_api_key"
  chain="fogo"
></vulcx-swap>
```
