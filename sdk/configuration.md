---
title: "SDK configuration"
description: "Configure the VulcxSDK client: pass your API key and base URL, tune timeout and retry/backoff behavior, and point it at a self-hosted Vulcx instance."
llmDescription: "Configuration reference for the Vulcx TypeScript SDK. Documents the SDKConfig object passed to the VulcxSDK constructor: apiKey, baseUrl, and retry behavior (retries, backoff). Includes a self-hosted API base URL override."
---

## `SDKConfig`

Pass a config object to the `VulcxSDK` constructor:

```typescript
import { VulcxSDK } from "@vulcx/sdk";

const sdk = new VulcxSDK({
  apiKey: "vulcx_your_api_key",
  baseUrl: "https://api.vulcx.xyz",
  timeout: 30000,
  retries: 2,
});
```

---

## Options

| Option | Type | Default | Required | Description |
|--------|------|---------|----------|-------------|
| `apiKey` | `string` | -- | yes | Your Vulcx API key. Sent as `Authorization: Bearer <apiKey>`. |
| `baseUrl` | `string` | `"https://api.vulcx.xyz"` | no | API base URL. Trailing slashes are stripped automatically. |
| `timeout` | `number` | `30000` | no | Per-request timeout in milliseconds. Uses `AbortController`. |
| `retries` | `number` | `2` | no | Number of retry attempts for retryable errors (429, 5xx, network failures). Total attempts = `retries + 1`. |

---

## Retry Behavior

The SDK retries automatically on transient failures:

| Condition | Retried | Backoff |
|-----------|---------|---------|
| HTTP 429 (rate limit) | yes | Exponential: 1s, 2s, 4s, ... (max 8s) |
| HTTP 5xx (server error) | yes | Exponential: 1s, 2s, 4s, ... (max 8s) |
| Network error / timeout | yes | Exponential: 1s, 2s, 4s, ... (max 8s) |
| HTTP 400 (bad request) | no | -- |
| HTTP 401/403 (auth) | no | -- |
| HTTP 404 (no route) | no | -- |

With the default `retries: 2`, the SDK makes up to 3 attempts before throwing.

---

## Self-Hosted API

If you run your own route-engine instance, point the SDK at it:

```typescript
const sdk = new VulcxSDK({
  apiKey: "any-value",
  baseUrl: "http://localhost:8080",
});
```
