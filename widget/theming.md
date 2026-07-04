---
title: "Widget theming"
description: "Theme vulcx-swap with CSS variables — dark/light presets, custom accent, radius, fonts, and backgrounds."
llmDescription: "Theming guide for the Vulcx vulcx-swap Web Component. Built-in dark (default) and light themes; full CSS custom-property reference (--vulcx-bg, --vulcx-surface, --vulcx-surface-hover, --vulcx-border, --vulcx-text, --vulcx-text-secondary, --vulcx-accent, --vulcx-error, --vulcx-radius). Custom branding examples (accent, rounded/sharp corners, custom background and font), Shadow DOM notes, and width control."
---

The widget uses CSS custom properties for all visual styling. Override them on the `<vulcx-swap>` element to match your brand.

---

## Built-in Themes

### Dark (default)

```html
<vulcx-swap theme="dark" api-key="..."></vulcx-swap>
```

### Light

```html
<vulcx-swap theme="light" api-key="..."></vulcx-swap>
```

---

## CSS Variables

Override any variable on the host element:

```css
vulcx-swap {
  --vulcx-accent: #00ff88;
  --vulcx-radius: 12px;
}
```

### Full Variable Reference

| Variable | Dark Default | Light Default | Description |
|----------|-------------|---------------|-------------|
| `--vulcx-bg` | `#0c0c10` | `#ffffff` | Widget background |
| `--vulcx-surface` | `#151519` | `#f5f5f7` | Card/panel background |
| `--vulcx-surface-hover` | `#1e1e25` | `#ebebef` | Hover state background |
| `--vulcx-border` | `#252530` | `#d4d4dc` | Border color |
| `--vulcx-text` | `#e8e8ed` | `#1a1a2e` | Primary text |
| `--vulcx-text-secondary` | `#7a7a8a` | `#6b6b7a` | Secondary text |
| `--vulcx-text-dim` | `#555565` | `#9a9aaa` | Dimmed text (placeholders) |
| `--vulcx-accent` | `#c8ff00` | `#1a1a2e` | Accent / CTA button color |
| `--vulcx-accent-hover` | `#d4ff33` | `#2d2d45` | Accent hover state |
| `--vulcx-error` | `#ff4d6a` | `#ff4d6a` | Error color |
| `--vulcx-warning` | `#ffaa00` | `#ffaa00` | Warning color (price impact) |
| `--vulcx-success` | `#00d68f` | `#00d68f` | Success color |
| `--vulcx-radius` | `20px` | `20px` | Outer border radius |
| `--vulcx-radius-sm` | `14px` | `14px` | Inner panel border radius |
| `--vulcx-badge-bg` | `#0a0a0e` | `#e8e8ed` | Token badge background |
| `--vulcx-font` | `'Inter', -apple-system, ...` | `'Inter', -apple-system, ...` | Font family |

---

## Custom Branding Examples

### Green accent

```css
vulcx-swap {
  --vulcx-accent: #00ff88;
  --vulcx-accent-hover: #33ff9f;
}
```

### Rounded corners

```css
vulcx-swap {
  --vulcx-radius: 24px;
  --vulcx-radius-sm: 18px;
}
```

### Sharp corners

```css
vulcx-swap {
  --vulcx-radius: 4px;
  --vulcx-radius-sm: 2px;
}
```

### Custom background to match your app

```css
vulcx-swap {
  --vulcx-bg: #1a1b2e;
  --vulcx-surface: #222340;
  --vulcx-surface-hover: #2a2b50;
  --vulcx-border: #3a3b55;
}
```

### Custom font

```css
vulcx-swap {
  --vulcx-font: "JetBrains Mono", monospace;
}
```

---

## Shadow DOM

The widget renders inside a shadow DOM, so your page styles don't leak in and widget styles don't leak out. CSS custom properties are the only way to customize the appearance from the outside. This is by design -- it ensures the widget looks correct regardless of your page's CSS.

---

## Width

The widget has `max-width: 460px` and `width: 100%`. To control its size, wrap it in a container:

```html
<div style="width: 400px; margin: 0 auto;">
  <vulcx-swap api-key="..." theme="dark"></vulcx-swap>
</div>
```
