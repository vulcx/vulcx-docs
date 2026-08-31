#!/usr/bin/env python3
"""Regenerate llms.txt from docs.json navigation + page frontmatter.

llms.txt is the index LLMs read. Hand-maintaining it let it drift badly
(it advertised a removed Widget tab and a since-dropped auth model), so it
is generated from the same frontmatter the site renders. Run after editing
navigation or any llmDescription:

    python3 scripts/gen-llms-txt.py
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://docs.vulcx.xyz"

HEADER = """# Vulcx

> Vulcx is a swap aggregator for SVM (Solana Virtual Machine) chains, providing best-price
> multi-hop routing across every DEX on a supported chain. Live on Fogo today, routing across
> Valiant, Fluxbeam and Moonit; Solana support is in progress.
> Base URL: `https://api.vulcx.xyz`. Three core endpoints: GET /api/v1/quote, POST /api/v1/swap,
> POST /api/v1/instructions. An API key is OPTIONAL on REST endpoints — anonymous calls work but
> are capped at 1 cost unit/second; a key raises that to the one published budget of 100 cost
> units/second, burst 200, which is the same for every plan. GET /health
> needs no key. The WebSocket stream (GET /api/v1/stream) is the one endpoint where a key is
> required, passed as ?key=vulcx_...
"""


def frontmatter(path):
    for ext in (".mdx", ".md"):
        f = ROOT / f"{path}{ext}"
        if f.exists():
            break
    else:
        return None
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).split("\n"):
        km = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if km:
            fm[km.group(1)] = km.group(2)
    return fm


def url_for(path):
    return f"{BASE}/{path[:-len('/index')] if path.endswith('/index') else path}"


def collect(node, pages):
    if isinstance(node, list):
        for n in node:
            collect(n, pages)
    elif isinstance(node, dict):
        for p in node.get("pages", []):
            if isinstance(p, str):
                pages.append(p)
            else:
                collect(p, pages)


def main():
    cfg = json.loads((ROOT / "docs.json").read_text(encoding="utf-8"))
    out, missing = [HEADER], []

    for tab in cfg["navigation"]["tabs"]:
        groups = tab.get("groups") or [tab]
        for group in groups:
            pages = []
            collect(group, pages)
            if not pages:
                continue
            name = group.get("group", tab["tab"])
            heading = name if name == tab["tab"] else f"{tab['tab']} — {name}"
            lines = []
            for path in pages:
                fm = frontmatter(path)
                if not fm:
                    missing.append(path)
                    continue
                title = fm.get("sidebarTitle") or fm.get("title") or path
                desc = fm.get("llmDescription") or fm.get("description") or ""
                lines.append(f"- [{title}]({url_for(path)}): {desc}")
            if lines:
                out.append(f"## {heading}\n\n" + "\n".join(lines) + "\n")

    (ROOT / "llms.txt").write_text("\n".join(out), encoding="utf-8")
    print(f"wrote llms.txt ({sum(1 for s in out for _ in s.split(chr(10)) )} lines)")
    if missing:
        print("WARNING: no frontmatter found for:", ", ".join(missing), file=sys.stderr)
        return 1
    return 0


sys.exit(main())
