# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Mintlify documentation site for **Vulcx** — a swap aggregator / routing engine on **Fogo Chain**. This is the public developer docs surface; it documents three sibling projects that live elsewhere in the `mono_vulcx` umbrella:

- **route-engine** — the REST API (`GET /api/v1/quote`, `POST /api/v1/swap`, `POST /api/v1/instructions`, `GET /health`). It is the source of truth for the API surface documented here.
- **sdk** (`@vulcx/sdk`) — TypeScript client wrapping the API.
- **widget** (`@vulcx/widget`) — the `vulcx-swap` Web Component.

There is no application code here — only Markdown/MDX content, the `docs.json` config, an OpenAPI spec, and assets.

## Commands

```bash
npm i -g mint        # install the Mintlify CLI (provides `mint`)
mint dev             # local preview at http://localhost:3000
mint broken-links    # validate internal links before pushing
```

There is no build step and no test suite. **Publishing is automatic**: pushing to the default branch deploys via the Mintlify GitHub app.

## How the site is wired together

**`docs.json` is the control plane.** It defines theme, colors, fonts, SEO/OG metadata, the OpenAPI source, and — most importantly — `navigation.tabs`. The site has top-level tabs (Get Started, Docs, SDK, Widget, API Reference, Guides, AI, Updates), each containing groups that list pages by path (no extension).

**A page file does not appear in the site until it is registered in `docs.json`.** When you add or rename an `.mdx`/`.md` file, you must add/update its path under the appropriate group in `navigation.tabs`, or it will be orphaned.

**Exception — the home page.** `index.mdx` is a hand-built landing page (`mode: "custom"` in its frontmatter) with full custom JSX/Tailwind markup. It is the site root and is intentionally *not* listed in `navigation.tabs`. Edit it as a bespoke layout, not as a normal content page.

**API Reference pages are driven by `api-reference/openapi.json`** (OpenAPI 3.1, registered via the top-level `"openapi"` key). The endpoint pages under `api-reference/*/index.mdx` render from that spec. Because route-engine owns the real API, keep `openapi.json` in sync with route-engine's handlers (`internal/http/`) — drift here means the published docs are wrong.

## Content conventions

- Pages are **MDX** under most tabs; the `sdk/` and `widget/` pages are plain **`.md`**. Both use YAML frontmatter.
- Frontmatter fields in use: `title`, `sidebarTitle` (optional), `description`, and a custom **`llmDescription`** — a long, keyword-rich summary written specifically for LLM/AI consumption. When adding a page, follow the existing pattern and write an `llmDescription` that fully summarizes the page's content and surfaces (endpoints, code examples, product caveats).
- `llms.txt` and `llms-full.txt` at the repo root are LLM-facing exports of the docs; treat them as generated/derived companions to the page content.
- `skill.md` (root) is a standalone **agent-skill definition** (`name: vulcx-swap`) that teaches an AI agent to call the Vulcx API. It duplicates the API surface in condensed form — when endpoints, params, or error behavior change, update it alongside the page content and `openapi.json`. `Assistant.md` is currently empty.
- `style.css` (root) is custom CSS that Mintlify **auto-loads** (no registration needed); it exists to match the landing page's black-and-silver look. Prefer global, version-stable selectors over Mintlify's internal class names, per the note at the top of the file.
- Mintlify components (e.g. `<Card>`, `<CodeGroup>`, accordions) are available inside MDX — match the components already used by neighboring pages rather than introducing new patterns.
- Product framing is consistent across the docs: **Vulcx runs on Fogo.** Multi-hop routing spans Vortex, Fluxbeam, Fogo.fun, and Moonit. There is no `chain` query parameter — the API is Fogo-only; a future chain would ship as a separate endpoint, not a proxied param. Keep new copy consistent with this.

## Assets

- Diagrams live in `images/` as editable sources (`.drawio`, `.excalidraw`) alongside exported `.png`. Edit the source, re-export the PNG, and reference the PNG from pages.
- Logos in `logo/`, favicon at repo root. OG/Twitter card is `images/og-card.png`, wired through `docs.json` `seo.metatags`.

## Gotcha

The working tree contains many `*Zone.Identifier` files (Windows "mark of the web" cruft from WSL). The `.gitignore` rule (`*:Zone.Identifier`) does not match them because they lack the colon, so dozens are tracked. Ignore them when editing — never treat one as a real content file, and don't create more.
