#!/usr/bin/env python3
"""Minimal drawio -> PNG renderer for the vulcx-docs diagrams.

Handles exactly the subset those files use: absolutely-positioned vertices
nested in container vertices, orthogonal edges with explicit waypoints and
exitX/entryX fractions, centered multi-line labels, title text cells.
"""
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

S = 3  # supersample scale (original exports were ~3x page size)
BG = "#08080a"
FONT = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf"
FONT_B = "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf"


def style_map(s):
    d = {}
    for part in (s or "").split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k] = v
        elif part:
            d[part] = "1"
    return d


def load(path):
    # Literal newlines inside value="..." would be normalized to spaces by the
    # XML parser; protect them as character references first.
    raw = open(path).read().replace("\n", "&#10;")
    root = ET.fromstring(raw)
    model = root.find(".//mxGraphModel")
    page_w = int(model.get("pageWidth"))
    page_h = int(model.get("pageHeight"))
    cells = {}
    order = []
    for c in model.iter("mxCell"):
        cells[c.get("id")] = c
        order.append(c)
    return page_w, page_h, cells, order


def abs_xy(cells, cell):
    """Absolute top-left of a vertex, walking the parent chain."""
    x = y = 0.0
    cur = cell
    while cur is not None:
        g = cur.find("mxGeometry")
        if g is not None:
            x += float(g.get("x", 0))
            y += float(g.get("y", 0))
        pid = cur.get("parent")
        cur = cells.get(pid) if pid not in (None, "0", "1") else None
    g = cell.find("mxGeometry")
    return x, y, float(g.get("width", 0)), float(g.get("height", 0))


def text_lines(value):
    v = (value or "").replace("&lt;", "<").replace("&gt;", ">")
    return v.split("\n")


def draw_label(dr, lines, cx, top, st, line_gap=1.35, bg=None):
    size = int(round(float(st.get("fontSize", 11)) * S))
    bold = st.get("fontStyle", "0") == "1"
    font = ImageFont.truetype(FONT_B if bold else FONT, size)
    color = st.get("fontColor", "#e8eaef")
    lh = int(size * line_gap)
    if bg:
        w = max((dr.textlength(l, font=font) for l in lines), default=0)
        h = lh * len(lines)
        dr.rectangle([cx - w / 2 - 4 * S, top - 2 * S, cx + w / 2 + 4 * S, top + h - int(0.35 * lh) + 2 * S], fill=bg)
    y = top
    for l in lines:
        dr.text((cx, y), l, font=font, fill=color, anchor="ma")
        y += lh
    return lh * len(lines)


def label_height(lines, st, line_gap=1.35):
    size = int(round(float(st.get("fontSize", 11)) * S))
    return int(size * line_gap) * len(lines)


def arrow(dr, p, q, color, width):
    """Line q<-p with an arrowhead at q."""
    dr.line([p, q], fill=color, width=width)
    import math
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    L = 11 * S
    W = math.radians(24)
    a = (q[0] - L * math.cos(ang - W), q[1] - L * math.sin(ang - W))
    b = (q[0] - L * math.cos(ang + W), q[1] - L * math.sin(ang + W))
    dr.polygon([q, a, b], fill=color)


def render(path, out):
    page_w, page_h, cells, order = load(path)
    img = Image.new("RGB", (page_w * S, page_h * S), BG)
    dr = ImageDraw.Draw(img)

    verts = [c for c in order if c.get("vertex") == "1"]
    edges = [c for c in order if c.get("edge") == "1"]

    # vertices (document order: containers first, children painted over)
    for c in verts:
        st = style_map(c.get("style"))
        x, y, w, h = abs_xy(cells, c)
        X, Y, W, H = x * S, y * S, w * S, h * S
        if st.get("text") == "1":  # bare text cell (title)
            lines = text_lines(c.get("value"))
            draw_label(dr, lines, X + W / 2, Y, st)
            continue
        fill = st.get("fillColor")
        stroke = st.get("strokeColor")
        dr.rectangle([X, Y, X + W, Y + H],
                     fill=None if fill in (None, "none") else fill,
                     outline=None if stroke in (None, "none") else stroke,
                     width=max(1, S))
        lines = [l for l in text_lines(c.get("value"))]
        if not any(lines):
            continue
        if st.get("verticalAlign") == "top":
            draw_label(dr, lines, X + W / 2, Y + 10 * S, st)
        else:
            th = label_height(lines, st)
            draw_label(dr, lines, X + W / 2, Y + (H - th) / 2 + 2 * S, st)

    # edges
    for e in edges:
        st = style_map(e.get("style"))
        src, tgt = cells[e.get("source")], cells[e.get("target")]
        sx, sy, sw, sh = abs_xy(cells, src)
        tx, ty, tw, th_ = abs_xy(cells, tgt)
        ex = sx + sw * float(st.get("exitX", 1)), sy + sh * float(st.get("exitY", 0.5))
        en = tx + tw * float(st.get("entryX", 0)), ty + th_ * float(st.get("entryY", 0.5))
        pts = [ex]
        g = e.find("mxGeometry")
        arr = g.find("Array") if g is not None else None
        if arr is not None:
            for p in arr.iter("mxPoint"):
                pts.append((float(p.get("x")), float(p.get("y"))))
        pts.append(en)
        # orthogonalize: consecutive points sharing neither x nor y get a bend
        path_pts = [pts[0]]
        for p in pts[1:]:
            last = path_pts[-1]
            if p[0] != last[0] and p[1] != last[1]:
                path_pts.append((p[0], last[1]))
            path_pts.append(p)
        path_pts = [(px * S, py * S) for (px, py) in path_pts]
        color = st.get("strokeColor", "#c9ced6")
        width = int(float(st.get("strokeWidth", 1)) * S)
        if len(path_pts) > 2:
            dr.line(path_pts[:-1], fill=color, width=width, joint="curve")
        arrow(dr, path_pts[-2], path_pts[-1], color, width)
        label = (e.get("value") or "").strip()
        if label:
            # place at the arc-length midpoint, like drawio does
            segs = list(zip(path_pts, path_pts[1:]))
            total = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in segs)
            walk = total / 2
            for a, b in segs:
                seg = abs(b[0] - a[0]) + abs(b[1] - a[1])
                if walk <= seg:
                    t = walk / seg if seg else 0
                    break
                walk -= seg
            mx, my = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            size = int(round(float(st.get("fontSize", 10)) * S))
            font = ImageFont.truetype(FONT, size)
            tw_ = dr.textlength(label, font=font)
            pad = 4 * S
            dr.rectangle([mx - tw_ / 2 - pad, my - size * 0.75 - pad, mx + tw_ / 2 + pad, my + size * 0.75 + pad],
                         fill=st.get("labelBackgroundColor", BG))
            dr.text((mx, my), label, font=font, fill=st.get("fontColor", "#9ca3af"), anchor="mm")

    img.save(out)
    print(out, img.size)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
