---
title: "Widget quickstart"
description: "Add the vulcx-swap Web Component swap UI to any app — HTML/CDN, React, Vue, or Next.js — in two minutes."
llmDescription: "Quickstart for the @vulcx/widget vulcx-swap Web Component. Shows installation via npm and CDN UMD, and embedding in plain HTML, React, Vue, and Next.js. Framework-agnostic swap UI for Fogo."
---

Add a swap UI to your app in 2 minutes. The `<vulcx-swap>` Web Component works in any framework or plain HTML.

---

## Install

```bash
npm install @vulcx/widget
```

Or via CDN (no build step):

```html
<script src="https://cdn.vulcx.xyz/vulcx-widget.umd.js"></script>
```

---

## HTML / CDN

```html
<script src="https://cdn.vulcx.xyz/vulcx-widget.umd.js"></script>

<vulcx-swap
  api-key="vulcx_your_api_key"
  default-input-mint="So11111111111111111111111111111111111111112"
  default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
  theme="dark"
></vulcx-swap>
```

That's it. The widget handles token selection, quoting, and swap execution.

---

## React

```tsx
import "@vulcx/widget";

function App() {
  return (
    <vulcx-swap
      api-key="vulcx_your_api_key"
      default-input-mint="So11111111111111111111111111111111111111112"
      default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
      theme="dark"
    />
  );
}
```

For TypeScript, add to your `global.d.ts`:

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

## Vue

```vue
<template>
  <vulcx-swap
    api-key="vulcx_your_api_key"
    default-input-mint="So11111111111111111111111111111111111111112"
    default-output-mint="uSd2czE61Evaf76RNbq4KPpXnkiL3irdzgLFUMe3NoG"
    theme="dark"
    @quote-update="onQuote"
    @swap-complete="onSwap"
  />
</template>

<script setup>
import "@vulcx/widget";

function onQuote(e) {
  console.log("Quote:", e.detail);
}
function onSwap(e) {
  console.log("Swap:", e.detail);
}
</script>
```

---

## Next.js

Web Components require client-side rendering. Use dynamic import:

```tsx
"use client";

import { useEffect, useRef } from "react";

export default function SwapWidget() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    import("@vulcx/widget");
  }, []);

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

## Next Steps

- [Attributes](./attributes.md) -- all configurable HTML attributes
- [Events](./events.md) -- listen for quotes, swaps, and errors
- [Wallet Integration](./wallet-integration.md) -- connect your wallet adapter
- [Theming](./theming.md) -- customize colors, radius, fonts
- [Examples](./examples.md) -- full integration examples per framework
