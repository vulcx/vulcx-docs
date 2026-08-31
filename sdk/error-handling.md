---
title: "SDK error handling"
description: "Typed SDK errors — BadRequestError, AuthError, NoRouteError, RateLimitError, ServerError — and retry behavior."
llmDescription: "Error handling for the Vulcx TypeScript SDK. All errors extend VulcxError. Documents typed subclasses by HTTP status: BadRequestError (400), AuthError (401/403), NoRouteError (404), RateLimitError (429), ServerError (5xx), with fields and when each is thrown. Covers automatic retry/backoff behavior and a catch-all pattern."
---

The SDK throws typed errors for different failure conditions. All errors extend `VulcxError`.

---

## Error Hierarchy

```
VulcxError (base)
├── BadRequestError    (400)
├── AuthError          (401/403)
├── NoRouteError       (404)
├── RateLimitError     (429)
└── ServerError        (5xx)
```

---

## Error Classes

### `VulcxError`

Base class for all SDK errors.

| Property | Type | Description |
|----------|------|-------------|
| `message` | `string` | Error message |
| `statusCode` | `number` | HTTP status code |
| `body` | `unknown` | Raw response body from the API |

### `BadRequestError` (400)

Thrown for invalid parameters: bad mint address, invalid amount, unsupported swap mode.

```typescript
import { BadRequestError } from "@vulcx/sdk";

try {
  await sdk.quote({ inputMint: "invalid", ... });
} catch (err) {
  if (err instanceof BadRequestError) {
    console.log(err.message); // "invalid inputMint address"
  }
}
```

### `AuthError` (401/403)

Thrown when the API key is invalid, missing, or revoked.

```typescript
import { AuthError } from "@vulcx/sdk";

try {
  await sdk.quote({ ... });
} catch (err) {
  if (err instanceof AuthError) {
    console.log(err.message); // "Invalid or missing API key"
  }
}
```

### `NoRouteError` (404)

Thrown when no liquidity path exists between the input and output tokens.

```typescript
import { NoRouteError } from "@vulcx/sdk";

try {
  await sdk.quote({ ... });
} catch (err) {
  if (err instanceof NoRouteError) {
    console.log("No route found -- try a different token pair");
  }
}
```

### `RateLimitError` (429)

Thrown after all retry attempts are exhausted on rate-limited requests.

```typescript
import { RateLimitError } from "@vulcx/sdk";

try {
  await sdk.quote({ ... });
} catch (err) {
  if (err instanceof RateLimitError) {
    console.log("Rate limited -- back off and retry later");
  }
}
```

### `ServerError` (5xx)

Thrown after all retry attempts are exhausted on server errors.

```typescript
import { ServerError } from "@vulcx/sdk";

try {
  await sdk.quote({ ... });
} catch (err) {
  if (err instanceof ServerError) {
    console.log("Server error -- retry later");
  }
}
```

---

### `QuoteExpiredError` (410)

Thrown when a `quoteId` passed to `swap()`/`instructions()` is past its TTL (or past the firm
window with `firm: true`). Not retried automatically — fetch a fresh quote and retry with the new
`quoteId`.

### `QuoteStaleError` (409)

Thrown when the pinned route no longer exists, or — with `firm: true` — the price drifted past the
firm margin. Not retried automatically; re-quote and retry.

```typescript
import { QuoteExpiredError, QuoteStaleError } from "@vulcx/sdk";

try {
  await sdk.swap({ ...req, quoteId: quote.quoteId });
} catch (err) {
  if (err instanceof QuoteExpiredError || err instanceof QuoteStaleError) {
    const fresh = await sdk.quote(quoteReq);          // one re-quote
    await sdk.swap({ ...req, quoteId: fresh.quoteId }); // retry at the fresh price
  } else throw err;
}
```

## Retry Behavior

The SDK automatically retries on transient failures before throwing:

| Status | Retried | Error thrown after exhaustion |
|--------|---------|------------------------------|
| 400 | no | `BadRequestError` (immediate) |
| 401/403 | no | `AuthError` (immediate) |
| 404 | no | `NoRouteError` (immediate) |
| 429 | yes | `RateLimitError` |
| 5xx | yes | `ServerError` |
| Network error / timeout | yes | `Error` |

Backoff is exponential: 1s, 2s, 4s, ... capped at 8s. With the default `retries: 2`, the SDK makes up to 3 attempts.

---

## Catching All Errors

```typescript
import {
  VulcxSDK,
  VulcxError,
  NoRouteError,
  RateLimitError,
  AuthError,
  BadRequestError,
  ServerError,
} from "@vulcx/sdk";

try {
  const quote = await sdk.quote({ ... });
} catch (err) {
  if (err instanceof NoRouteError) {
    // No liquidity path
  } else if (err instanceof BadRequestError) {
    // Invalid parameters
  } else if (err instanceof AuthError) {
    // Bad API key
  } else if (err instanceof RateLimitError) {
    // Rate limited after retries
  } else if (err instanceof ServerError) {
    // Server error after retries
  } else if (err instanceof VulcxError) {
    // Other API error
    console.log(err.statusCode, err.message);
  } else {
    // Network error, timeout, etc.
  }
}
```
