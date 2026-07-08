#!/usr/bin/env python3
"""Excalidraw layout engine.

Takes structured diagram data from LLM analysis
and generates a valid .excalidraw file with hand-drawn style.

Usage:
    python layout.py --input structured.json --output diagram.excalidraw
"""

import json
import math
import os
import random
import sys
import uuid
import argparse


# --- Constants ---

FONT_SIZE = 16
FONT_FAMILY = 1
NODE_MIN_WIDTH = 160
NODE_HEIGHT = 56
NODE_PADDING = 24
TEXT_LR_PAD = 14
LEVEL_GAP = 80
HORIZONTAL_GAP = 50
DIAGRAM_GAP = 100
SECTION_GAP = 140
CANVAS_MARGIN = 80
MAX_DIAGRAM_WIDTH = 720

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PALETTE = {
    "stroke": "#1e1e1e",
    "process_fill": "#d0ebff",
    "decision_fill": "#ffec99",
    "terminal_fill": "#b2f2bb",
    "arrow_stroke": "#495057",
    "text_color": "#1e1e1e",
    "comparison_left": "#e7f5ff",
    "comparison_right": "#fff0f6",
    "comparison_feat": "#f1f3f5",
    "tree_fill": "#e5dbff",
    "timeline_line": "#adb5bd",
    "mindmap_fill": "#fff3bf",
    "row_even": "#f1f3f5",
    "card_fill": "#ffffff",
    "card_stroke": "#ced4da",
    "accent_stroke": "#d6336c",
}

FILL_STYLES = {"solid", "hachure", "cross-hatch"}


def load_style_preset(style_name="professional"):
    path = os.path.join(SKILL_DIR, "references", "style-presets.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        presets = json.load(f)
    return presets.get("presets", {}).get(style_name)


def _char_width(c, font_size=FONT_SIZE):
    if '\u4e00' <= c <= '\u9fff' or '\u3000' <= c <= '\u303f' or '\uff00' <= c <= '\uffef':
        return font_size
    if c in '\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251':
        return font_size * 1.1
    if c.isascii() and c.isprintable():
        return font_size * 0.55
    return font_size * 0.7


def estimate_text_dimensions(text, font_size=FONT_SIZE, max_width=240,
                             icon=None):
    if icon:
        text = f"{icon} {text}"
    if not text:
        return (NODE_MIN_WIDTH, NODE_HEIGHT)

    lines = text.split('\n')
    internal_width = max_width - 2 * TEXT_LR_PAD
    if internal_width <= 0:
        internal_width = 100

    total_lines = 0
    max_line_w = 0
    for line in lines:
        lw = sum(_char_width(c, font_size) for c in line)
        max_line_w = max(max_line_w, lw)
        n = max(1, math.ceil(lw / internal_width))
        total_lines += n

    text_height = total_lines * font_size * 1.5
    actual_width = min(max_line_w, internal_width) + 2 * TEXT_LR_PAD
    actual_width = max(actual_width, NODE_MIN_WIDTH)
    actual_height = max(text_height + 2 * NODE_PADDING, NODE_HEIGHT)
    return (actual_width, actual_height)


def estimate_text_width_raw(text, font_size=FONT_SIZE):
    return sum(_char_width(c, font_size) for c in text)


# --- Excalidraw Element Factory ---

class ExcalidrawBuilder:
    def __init__(self, style_preset=None):
        self.elements = []
        self._seed_counter = random.randint(0, 10000)
        self._current_y = CANVAS_MARGIN
        self._preset = style_preset or {}
        self._colors = self._preset.get("colors", {})
        self._fills = self._preset.get("fills", {})
        self._deco = self._preset.get("decorations", {})
        self._typo = self._preset.get("typography", {})

    def _seed(self):
        self._seed_counter += 1
        return self._seed_counter

    def _gid(self, prefix="e"):
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    def _text(self, x, y, w, h, text, font_size=FONT_SIZE,
              font_family=FONT_FAMILY, text_align="center",
              vertical_align="middle", container_id=None, color=None):
        return {
            "id": self._gid("t"),
            "type": "text",
            "x": x, "y": y,
            "width": w, "height": h,
            "angle": 0,
            "strokeColor": color or PALETTE["text_color"],
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 1,
            "roughness": 1,
            "opacity": 100,
            "groupIds": [],
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "text": text,
            "fontSize": font_size,
            "fontFamily": font_family,
            "textAlign": text_align,
            "verticalAlign": vertical_align,
            "containerId": container_id,
            "originalText": text,
        }

    def _style_val(self, key, default):
        return self._deco.get(key) if self._deco else default

    def _fill_style(self):
        return self._style_val("fill_style", "solid")

    def _stroke_width(self):
        return self._style_val("stroke_width", 2)

    def _roughness(self):
        return self._style_val("roughness", 2)

    def _opacity(self, level="primary"):
        key = f"opacity_{level}"
        return self._style_val(key, 100)

    def _rect(self, x, y, w, h, fill="transparent",
              stroke=None, roundness=None, fill_style=None, opacity=None):
        return {
            "id": self._gid("r"),
            "type": "rectangle",
            "x": x, "y": y,
            "width": w, "height": h,
            "angle": 0,
            "strokeColor": stroke or (self._colors.get("stroke") if self._colors else PALETTE["stroke"]),
            "backgroundColor": fill,
            "fillStyle": fill_style or self._fill_style(),
            "strokeWidth": self._stroke_width(),
            "roughness": self._roughness(),
            "opacity": opacity if opacity is not None else self._opacity("primary"),
            "groupIds": [],
            "roundness": roundness,
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
        }

    def _diamond(self, x, y, w, h, fill="transparent", fill_style=None, opacity=None):
        return {
            "id": self._gid("d"),
            "type": "diamond",
            "x": x, "y": y,
            "width": w, "height": h,
            "angle": 0,
            "strokeColor": self._colors.get("stroke") if self._colors else PALETTE["stroke"],
            "backgroundColor": fill,
            "fillStyle": fill_style or self._fill_style(),
            "strokeWidth": self._stroke_width(),
            "roughness": self._roughness(),
            "opacity": opacity if opacity is not None else self._opacity("primary"),
            "groupIds": [],
            "roundness": None,
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
        }

    def _ellipse(self, x, y, w, h, fill="transparent", fill_style=None, opacity=None):
        return {
            "id": self._gid("e"),
            "type": "ellipse",
            "x": x, "y": y,
            "width": w, "height": h,
            "angle": 0,
            "strokeColor": self._colors.get("stroke") if self._colors else PALETTE["stroke"],
            "backgroundColor": fill,
            "fillStyle": fill_style or self._fill_style(),
            "strokeWidth": self._stroke_width(),
            "roughness": self._roughness(),
            "opacity": opacity if opacity is not None else self._opacity("primary"),
            "groupIds": [],
            "roundness": None,
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
        }

    def _arrow(self, x1, y1, x2, y2, start_id=None, end_id=None,
               label="", lx=0, ly=0, arrow_style=None):
        dx = x2 - x1
        dy = y2 - y1
        if arrow_style == "dot":
            end_head = "dot"
        elif arrow_style == "bidirectional":
            end_head = "arrow"
        elif arrow_style == "line":
            end_head = None
        else:
            end_head = "arrow"
        arrow = {
            "id": self._gid("a"),
            "type": "arrow",
            "x": x1, "y": y1,
            "width": abs(dx), "height": abs(dy),
            "angle": 0,
            "strokeColor": self._colors.get("arrow") if self._colors else PALETTE["arrow_stroke"],
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": self._stroke_width(),
            "roughness": 1,
            "opacity": self._opacity("primary"),
            "groupIds": [],
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": {
                "elementId": start_id, "focus": 0, "gap": 5
            } if start_id else None,
            "endBinding": {
                "elementId": end_id, "focus": 0, "gap": 5
            } if end_id else None,
            "startArrowhead": "arrow" if arrow_style == "bidirectional" else None,
            "endArrowhead": end_head,
        }
        elems = [arrow]
        if label:
            ew = estimate_text_width_raw(label, 12) + 20
            elems.append(self._text(lx, ly, max(ew, 40), 20, label,
                          font_size=12, text_align="center"))
        return elems

    def _line(self, x, y, x2, y2, color=None, width=None, opacity=None, stroke_style="solid"):
        return {
            "id": self._gid("l"),
            "type": "line",
            "x": x, "y": y,
            "width": abs(x2 - x), "height": abs(y2 - y),
            "angle": 0,
            "strokeColor": color or (self._colors.get("line") if self._colors else PALETTE["arrow_stroke"]),
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": width or self._stroke_width(),
            "strokeStyle": stroke_style,
            "roughness": 1,
            "opacity": opacity if opacity is not None else self._opacity("secondary"),
            "groupIds": [],
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[0, 0], [x2 - x, y2 - y]],
        }

    def _make_node(self, node_id, label, shape, x, y, w, h, fill, icon=None, fill_style=None):
        if icon:
            label = f"{icon} {label}"
        if shape == "diamond":
            se = self._diamond(x, y, w, h, fill, fill_style=fill_style)
        elif shape == "ellipse":
            se = self._ellipse(x, y, w, h, fill, fill_style=fill_style)
        elif shape == "cloud":
            rn = {"type": 3}
            se = self._rect(x, y, w, h, fill, roundness=rn, fill_style=fill_style or "hachure")
        elif shape == "pill":
            se = self._rect(x, y, w, h, fill, roundness={"type": 2})
        else:
            rn = {"type": 3} if shape == "rounded" else None
            se = self._rect(x, y, w, h, fill, roundness=rn, fill_style=fill_style)
        fs = self._typo.get("node_label_size") if self._typo else FONT_SIZE
        te = self._text(x + TEXT_LR_PAD, y + NODE_PADDING, w - 2 * TEXT_LR_PAD, h - 2 * NODE_PADDING, label,
                        font_size=fs, container_id=se["id"])
        se["boundElements"].append({"type": "text", "id": te["id"]})
        return (se, te)

    def _add_title(self, x, y, title, font_size=None):
        if font_size is None:
            font_size = self._typo.get("title_size") if self._typo else 20
        tw = estimate_text_width_raw(title, font_size) + 40
        te = self._text(x, y, max(tw, 200), 30, title,
                        font_size=font_size, text_align="left",
                        color=self._colors.get("text") if self._colors else None)
        self.elements.append(te)
        return y + 40


    # === Layout Algorithms ===

    def _layout_flowchart(self, data):
        nodes = data.get("nodes", [])
        edges = data.get("edges", [])
        title = data.get("title", "")
        if not nodes:
            return (0, 0)

        adj = {n["id"]: [] for n in nodes}
        indeg = {n["id"]: 0 for n in nodes}
        for e in edges:
            adj.setdefault(e["from"], []).append(e["to"])
            indeg[e["to"]] = indeg.get(e["to"], 0) + 1

        roots = [n["id"] for n in nodes if indeg.get(n["id"], 0) == 0]
        if not roots:
            roots = [nodes[0]["id"]]

        levels = {}
        q = [(r, 0) for r in roots]
        visited = set()
        while q:
            nid, lv = q.pop(0)
            if nid in visited:
                continue
            visited.add(nid)
            levels[nid] = max(levels.get(nid, 0), lv)
            for ch in adj.get(nid, []):
                q.append((ch, lv + 1))
        for n in nodes:
            if n["id"] not in levels:
                levels[n["id"]] = 0

        lgroups = {}
        for n in nodes:
            lv = levels[n["id"]]
            lgroups.setdefault(lv, []).append(n)
        slvls = sorted(lgroups.keys())

        nwidths = {}
        for n in nodes:
            w, h = estimate_text_dimensions(n.get("label", ""), icon=n.get("icon"))
            w = max(w, NODE_MIN_WIDTH)
            nwidths[n["id"]] = (w, h)

        x = CANVAS_MARGIN
        y = self._current_y

        if title:
            y = self._add_title(x, y, title)

        pos = {}
        for lv in slvls:
            grp = lgroups[lv]
            tw = sum(nwidths[n["id"]][0] for n in grp)
            tw += (len(grp) - 1) * HORIZONTAL_GAP
            sx = x + max(0, (MAX_DIAGRAM_WIDTH - tw) / 2)
            cy = y
            cx = sx
            max_h = 0
            for n in grp:
                w, h = nwidths[n["id"]]
                max_h = max(max_h, h)
                shp = n.get("shape", "rect")
                fl = PALETTE["terminal_fill"] if shp in ("rounded","terminal") else (
                    PALETTE["decision_fill"] if shp == "diamond" else PALETTE["process_fill"])
                se, te = self._make_node(n["id"], n["label"], shp, cx, cy, w, h, fl, icon=n.get("icon"))
                self.elements.extend([se, te])
                pos[n["id"]] = (cx, cy, w, h, se)
                cx += w + HORIZONTAL_GAP
            y += max_h + LEVEL_GAP

        for e in edges:
            if e["from"] not in pos or e["to"] not in pos:
                continue
            fx, fy, fw, fh, fe = pos[e["from"]]
            tx, ty, tw, th, te = pos[e["to"]]
            ax1, ay1 = fx + fw/2, fy + fh
            ax2, ay2 = tx + tw/2, ty
            lbl = e.get("label", "")
            arrs = self._arrow(ax1, ay1, ax2, ay2,
                               start_id=fe["id"], end_id=te["id"],
                               label=lbl, lx=(ax1+ax2)/2-30, ly=(ay1+ay2)/2-10)
            self.elements.extend(arrs)

        dh = y - self._current_y + 20
        self._current_y = y + DIAGRAM_GAP - LEVEL_GAP
        return (700, dh)

    def _layout_comparison(self, data):
        title = data.get("title", "")
        lh = data.get("left_header", "")
        rh = data.get("right_header", "")
        items = data.get("items", [])

        x = CANVAS_MARGIN
        y = self._current_y
        fw = 130
        cw = 255
        cg = 16
        rh2 = 46
        left_x = x + fw + cg
        right_x = x + fw + cg + cw + cg
        mid_x = left_x + cw / 2

        if title:
            y = self._add_title(x, y, title)

        if lh and rh:
            fhr = self._rect(x, y, fw, rh2, PALETTE["comparison_feat"])
            fht = self._text(x + 8, y + 11, fw - 16, rh2 - 22, "特征",
                             font_size=14, container_id=fhr["id"])
            fhr["boundElements"].append({"type": "text", "id": fht["id"]})
            self.elements.extend([fhr, fht])

            lhr = self._rect(left_x, y, cw, rh2, PALETTE["comparison_left"])
            lht = self._text(left_x + 12, y + 11, cw - 24, rh2 - 22, lh,
                             font_size=15, container_id=lhr["id"])
            lhr["boundElements"].append({"type": "text", "id": lht["id"]})
            self.elements.extend([lhr, lht])

            rhr = self._rect(right_x, y, cw, rh2, PALETTE["comparison_right"])
            rht = self._text(right_x + 12, y + 11, cw - 24, rh2 - 22, rh,
                             font_size=15, container_id=rhr["id"])
            rhr["boundElements"].append({"type": "text", "id": rht["id"]})
            self.elements.extend([rhr, rht])
            y += rh2

        ml_top = y
        ml_bot = y + len(items) * rh2
        self.elements.append(self._line(mid_x, ml_top, mid_x, ml_bot,
                              color="#adb5bd", opacity=60))

        for i, item in enumerate(items):
            feat = item.get("feature", "")
            lv = item.get("left", "")
            rv = item.get("right", "")

            fl = PALETTE["row_even"] if i % 2 == 0 else "transparent"

            fr = self._rect(x, y, fw, rh2, fl)
            ft = self._text(x + 8, y + 11, fw - 16, rh2 - 22, feat,
                            font_size=13, container_id=fr["id"])
            fr["boundElements"].append({"type": "text", "id": ft["id"]})
            self.elements.extend([fr, ft])

            lvr = self._rect(left_x, y, cw, rh2, fl)
            lvt = self._text(left_x + 12, y + 11, cw - 24, rh2 - 22, lv,
                             font_size=14, container_id=lvr["id"])
            lvr["boundElements"].append({"type": "text", "id": lvt["id"]})
            self.elements.extend([lvr, lvt])

            rvr = self._rect(right_x, y, cw, rh2, fl)
            rvt = self._text(right_x + 12, y + 11, cw - 24, rh2 - 22, rv,
                             font_size=14, container_id=rvr["id"])
            rvr["boundElements"].append({"type": "text", "id": rvt["id"]})
            self.elements.extend([rvr, rvt])

            y += rh2

        dh = y - self._current_y + 20
        self._current_y = y + DIAGRAM_GAP
        return (right_x + cw - x + 20, dh)

    def _layout_tree(self, data):
        title = data.get("title", "")
        root = data.get("root", {})
        if not root:
            return (0, 0)

        x = CANVAS_MARGIN
        y = self._current_y
        if title:
            y = self._add_title(x, y, title)

        def _compute(n):
            lb = n.get("label", "")
            w, h = estimate_text_dimensions(lb, icon=n.get("icon"))
            w = max(w, NODE_MIN_WIDTH)
            chs = n.get("children", [])
            if not chs:
                return {"w": w, "h": h, "tw": w, "th": h + 40}
            cr = [_compute(c) for c in chs]
            tw = sum(c["tw"] for c in cr) + (len(chs) - 1) * HORIZONTAL_GAP
            mh = max(c["th"] for c in cr)
            return {"w": w, "h": h, "tw": max(w, tw), "th": h + LEVEL_GAP + mh,
                    "children": cr}

        def _position(n, res, px, py, aw):
            lb = n.get("label", "")
            w, h = res["w"], res["h"]
            nx = px + (aw - w) / 2
            se, te = self._make_node(n.get("id",""), lb, "rect",
                                      nx, py, w, h, PALETTE["tree_fill"], icon=n.get("icon"))
            self.elements.extend([se, te])
            chs = n.get("children", [])
            ch_res = res.get("children", [])
            if not chs:
                return
            ctw = sum(cr["tw"] for cr in ch_res)
            ctw += (len(chs) - 1) * HORIZONTAL_GAP
            cx = px + (aw - ctw) / 2
            cy = py + h + LEVEL_GAP
            for i, ch in enumerate(chs):
                _position(ch, ch_res[i], cx, cy, ch_res[i]["tw"])
                self.elements.extend(self._arrow(
                    nx + w/2, py + h,
                    cx + ch_res[i]["tw"]/2, cy))
                cx += ch_res[i]["tw"] + HORIZONTAL_GAP

        res = _compute(root)
        _position(root, res, x, y, res["tw"])
        dh = res["th"] + 20
        self._current_y = y + res["th"] + DIAGRAM_GAP
        return (max(res["tw"] + CANVAS_MARGIN, 600), dh)

    def _layout_timeline(self, data):
        events = data.get("events", [])
        title = data.get("title", "")
        if not events:
            return (0, 0)

        x = CANVAS_MARGIN + 20
        y = self._current_y
        if title:
            y = self._add_title(x, y, title)

        ev_w = 160
        ev_gap = 40
        total_w = len(events) * (ev_w + ev_gap) - ev_gap
        line_y = y + 30
        self.elements.append(self._line(x, line_y, x + total_w, line_y,
                              color="#adb5bd", opacity=60))

        for i, ev in enumerate(events):
            ex = x + i * (ev_w + ev_gap)
            edate = ev.get("date", "")
            etitle = ev.get("title", "")
            edesc = ev.get("description", "")

            dot = self._ellipse(ex + ev_w / 2 - 6, line_y - 6, 12, 12,
                                PALETTE["process_fill"])
            self.elements.append(dot)

            above = i % 2 == 0
            if above:
                dt = self._text(ex, line_y - 55, ev_w, 20, edate,
                                font_size=12, text_align="center")
                tt = self._text(ex, line_y - 35, ev_w, 20, etitle,
                                font_size=14, text_align="center", color="#1971c2")
                self.elements.extend([dt, tt])
            else:
                dt = self._text(ex, line_y + 25, ev_w, 20, edate,
                                font_size=12, text_align="center")
                tt = self._text(ex, line_y + 45, ev_w, 20, etitle,
                                font_size=14, text_align="center", color="#1971c2")
                self.elements.extend([dt, tt])
            if edesc:
                dy = line_y + 70 if above else line_y - 75
                ds = self._text(ex, dy, ev_w, 30, edesc,
                                font_size=12, text_align="center", color="#868e96")
                self.elements.append(ds)

        dh = 160
        self._current_y = line_y + 100 + DIAGRAM_GAP
        return (total_w + 100, dh)

    def _layout_mindmap(self, data):
        title = data.get("title", "")
        root = data.get("root", {})
        if not root:
            return (0, 0)

        x = CANVAS_MARGIN
        y = self._current_y

        if title:
            y = self._add_title(x, y, title)

        level_w = 200
        v_gap = 16

        def _compute(n, depth=0):
            lb = n.get("label", "")
            w, h = estimate_text_dimensions(lb, max_width=180, icon=n.get("icon"))
            w = max(w, NODE_MIN_WIDTH)
            brs = n.get("branches", [])
            if not brs:
                return {"w": w, "h": h, "tw": w, "th": h, "count": 1,
                        "children": []}
            cr = [_compute(b, depth + 1) for b in brs]
            total_ch = sum(c["count"] for c in cr)
            max_th = max(c["th"] for c in cr)
            child_h = sum(c["th"] for c in cr) + (len(brs) - 1) * v_gap
            tw = w + level_w + max(c["tw"] for c in cr)
            return {"w": w, "h": h, "tw": tw, "th": max(child_h, h),
                    "count": total_ch, "children": cr}

        def _position(n, res, px, py, depth=0):
            lb = n.get("label", "")
            w, h = res["w"], res["h"]
            label_display = lb
            icon = n.get("icon")
            if icon:
                label_display = f"{icon} {lb}"
            se = self._rect(px, py - h/2, w, h, PALETTE["mindmap_fill"],
                            roundness={"type": 2})
            te = self._text(px + 10, py - h/2 + 10, w - 20, h - 20, label_display,
                            container_id=se["id"])
            se["boundElements"].append({"type": "text", "id": te["id"]})
            self.elements.extend([se, te])

            brs = n.get("branches", [])
            ch_res = res.get("children", [])
            if not brs:
                return

            bx = px + w + level_w - w
            total_ch_h = sum(cr["th"] for cr in ch_res) + (len(brs) - 1) * v_gap
            by = py - total_ch_h / 2

            for i, br in enumerate(brs):
                ch_y = by + ch_res[i]["th"] / 2
                _position(br, ch_res[i], bx, ch_y, depth + 1)
                self.elements.extend(self._arrow(
                    px + w, py, bx, ch_y))
                by += ch_res[i]["th"] + v_gap

        res = _compute(root)
        _position(root, res, x, y + res["th"] / 2, 0)

        dh = res["th"] + 80
        self._current_y = y + res["th"] + DIAGRAM_GAP
        return (res["tw"] + 100, dh)


    def _layout_cycle(self, data):
        nodes = data.get("nodes", [])
        title = data.get("title", "")
        exit_node = data.get("exit_node", None)
        if len(nodes) < 2:
            return (0, 0)

        y0 = self._current_y
        if title:
            y0 = self._add_title(CANVAS_MARGIN, y0, title)

        nws = [max(NODE_MIN_WIDTH, estimate_text_dimensions(
            n["label"], icon=n.get("icon"))[0]) for n in nodes]
        nw = max(nws)
        nh = NODE_HEIGHT
        vg = 80
        x0 = CANVAS_MARGIN + 60
        cx = x0 + nw / 2

        pos = {}
        for i, n in enumerate(nodes):
            nx = x0
            ny = y0 + 10 + i * (nh + vg)
            fl = PALETTE["process_fill"]
            se, te = self._make_node(n["id"], n["label"], n.get("shape","rect"),
                                      nx, ny, nw, nh, fl, icon=n.get("icon"))
            self.elements.extend([se, te])
            pos[n["id"]] = (nx, ny, nw, nh, se)

        for i in range(len(nodes) - 1):
            fa, ta = nodes[i]["id"], nodes[i + 1]["id"]
            fx, fy, fw, fh, fe = pos[fa]
            tx, ty, tw, th, te = pos[ta]
            self.elements.extend(self._arrow(
                fx + fw/2, fy + fh, tx + tw/2, ty,
                start_id=fe["id"], end_id=te["id"]))

        if exit_node:
            last = nodes[-1]
            lx, ly, lw, lh, le = pos[last["id"]]
            dx = x0 + nw + 60
            dy = y0 + 10 + len(nodes) * (nh + vg) - vg + 20

            se, te = self._make_node(exit_node["id"], exit_node["label"],
                                      "diamond", dx, dy, 120, nh,
                                      PALETTE["decision_fill"],
                                      icon=exit_node.get("icon"))
            self.elements.extend([se, te])
            edx = dx + 60

            rex = lx + lw / 2
            rey = ly + lh
            self.elements.extend(self._arrow(rex, rey, edx, dy,
               start_id=le["id"], end_id=se["id"]))

            output = exit_node.get("on_yes")
            if output:
                ox = dx + 120 + 50
                oy = dy
                se2, te2 = self._make_node(output["id"], output["label"],
                                            "rounded", ox, oy, nw, nh,
                                            PALETTE["terminal_fill"],
                                            icon=output.get("icon"))
                self.elements.extend([se2, te2])
                self.elements.extend(self._arrow(
                    dx + 120, dy + nh/2, ox, oy + nh/2,
                    start_id=se["id"], end_id=se2["id"],
                    label="是", lx=dx+175, ly=dy-20))

            first = nodes[0]
            fx, fy, fw, fh, fe = pos[first["id"]]
            fcx = fx + fw / 2

            return_target_y = fy + fh
            return_bot_y = dy + nh + 80
            return_right_x = dx + nw + 220

            arr_path = {
                "id": self._gid("ra"),
                "type": "arrow",
                "x": edx, "y": dy + nh,
                "width": abs(return_right_x - edx),
                "height": abs(return_bot_y - (dy + nh)),
                "angle": 0,
                "strokeColor": PALETTE["arrow_stroke"],
                "backgroundColor": "transparent",
                "fillStyle": "solid",
                "strokeWidth": 2,
                "roughness": 2,
                "opacity": 100,
                "groupIds": [],
                "seed": self._seed(),
                "version": 1,
                "versionNonce": 0,
                "isDeleted": False,
                "boundElements": None,
                "updated": 1,
                "link": None,
                "locked": False,
                "points": [
                    [0, 0],
                    [0, return_bot_y - (dy + nh)],
                    [return_right_x - edx, return_bot_y - (dy + nh)],
                    [return_right_x - edx, return_target_y - (dy + nh)],
                    [fcx - edx, return_target_y - (dy + nh)],
                ],
                "lastCommittedPoint": None,
                "startBinding": {"elementId": se["id"], "focus": 0, "gap": 5},
                "endBinding": {"elementId": fe["id"], "focus": 0, "gap": 5},
                "startArrowhead": None,
                "endArrowhead": "arrow",
            }
            self.elements.append(arr_path)

            no_lbl = exit_node.get("on_no_label", "否")
            self.elements.append(self._text(
                edx - 45, dy + nh + 25, 60, 20, no_lbl, font_size=12,
                text_align="center"))

            diagram_bottom = return_bot_y + 20
        else:
            diagram_bottom = y0 + 10 + len(nodes) * (nh + vg)

        dh = diagram_bottom - y0 + 10
        self._current_y = diagram_bottom + DIAGRAM_GAP
        return (max(return_right_x if exit_node else x0 + nw + 100, 700), dh)


    # --- Sketchnote (手绘信息图) ---

    def _doodle_star(self, cx, cy, size=20):
        s = size / 2
        pts = [
            [0, -s], [s * 0.22, -s * 0.22], [s, -s * 0.22],
            [s * 0.35, 0.08], [s * 0.55, s], [0, s * 0.38],
            [-s * 0.55, s], [-s * 0.35, 0.08], [-s, -s * 0.22],
            [-s * 0.22, -s * 0.22]
        ]
        pts = [[p[0] + cx, p[1] + cy] for p in pts]
        return {
            "id": self._gid("ds"),
            "type": "line",
            "x": cx - s, "y": cy - s,
            "width": s * 2, "height": s * 2,
            "angle": 0,
            "strokeColor": "#fab005",
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "roughness": 2,
            "opacity": 90,
            "groupIds": [],
            "seed": self._seed(),
            "version": 1,
            "versionNonce": 0,
            "isDeleted": False,
            "boundElements": None,
            "updated": 1,
            "link": None,
            "locked": False,
            "points": [[p[0] - (cx - s), p[1] - (cy - s)] for p in pts],
        }

    def _doodle_sparkle(self, cx, cy, size=12):
        elems = []
        s = size / 2
        for dx, dy, rot in [(0, -s * 1.2, 0), (s * 0.8, -s * 0.4, 0.5),
                             (s * 0.6, s * 0.8, 1.0), (-s * 0.6, s * 0.6, 1.5),
                             (-s * 0.8, -s * 0.5, 2.0)]:
            c = self._ellipse(cx + dx - 3, cy + dy - 3, 6, 6,
                              "#ffe066", fill_style="solid")
            c["opacity"] = 70
            c["strokeColor"] = "#fab005"
            elems.append(c)
        return elems

    SKETCHNOTE_COLORS = {
        "yellow": {"fill": "#fff3bf", "stroke": "#fab005", "text": "#2d2d2d"},
        "blue": {"fill": "#d0ebff", "stroke": "#4dabf7", "text": "#2d2d2d"},
        "pink": {"fill": "#fcc2d7", "stroke": "#f06595", "text": "#2d2d2d"},
        "green": {"fill": "#d3f9d8", "stroke": "#51cf66", "text": "#2d2d2d"},
        "purple": {"fill": "#e5dbff", "stroke": "#845ef7", "text": "#2d2d2d"},
        "orange": {"fill": "#ffd8a8", "stroke": "#fd7e14", "text": "#2d2d2d"},
    }

    def _layout_sketchnote(self, data):
        title = data.get("title", "")
        subtitle = data.get("subtitle", "")
        steps = data.get("steps", [])
        if not steps:
            return (0, 0)

        x = CANVAS_MARGIN
        y = self._current_y
        step_w = 600
        step_h = 90
        step_gap = 30

        # --- Title area ---
        cx = x + step_w / 2
        if title:
            tis = 26
            tw = estimate_text_width_raw(title, tis) + 40
            te = self._text(cx - tw / 2, y, tw, 38, title,
                            font_size=tis, text_align="center",
                            color="#2d2d2d")
            self.elements.append(te)
            y += 42
            self.elements.append(self._doodle_star(cx - tw / 2 - 30, y - 20, 18))
            self.elements.append(self._doodle_star(cx + tw / 2 + 30, y - 20, 14))
            sparkles = self._doodle_sparkle(cx, y - 30, 16)
            self.elements.extend(sparkles)

        if subtitle:
            sw = estimate_text_width_raw(subtitle, 15) + 40
            st = self._text(cx - sw / 2, y, sw, 28, subtitle,
                           font_size=15, text_align="center",
                           color="#868e96")
            self.elements.append(st)
            y += 40

        # --- Steps ---
        y += 24
        pos = {}
        color_keys = ["yellow", "blue", "pink", "green", "purple", "orange"]

        for i, step in enumerate(steps):
            stp = step.get("title", "")
            ssub = step.get("subtitle", "")
            sicon = step.get("icon", "")
            ckey = step.get("color", color_keys[i % len(color_keys)])
            sc = self.SKETCHNOTE_COLORS.get(ckey, self.SKETCHNOTE_COLORS["blue"])

            sx = x
            sy = y

            box = self._rect(sx, sy, step_w, step_h, sc["fill"],
                             stroke=sc["stroke"], roundness={"type": 3},
                             fill_style="solid")
            self.elements.append(box)

            # Icon on left side
            icon_w = 0
            if sicon:
                result = self._place_icon(sicon, sx + 18, sy + 18, 0.6)
                if result:
                    icon_w, _ = result
                else:
                    icon_w = 0

            text_left = sx + 18 + icon_w + 14

            # Title
            fs = 18
            ttw = estimate_text_width_raw(stp, fs) + 20
            tt = self._text(text_left, sy + 14, ttw, 30, stp,
                           font_size=fs, text_align="left", color=sc["text"])
            self.elements.append(tt)

            # Subtitle
            if ssub:
                sw2 = estimate_text_width_raw(ssub, 14) + 20
                sst = self._text(text_left, sy + 46, sw2, 26, ssub,
                                font_size=14, text_align="left", color="#868e96")
                self.elements.append(sst)

            pos[step.get("id", f"s{i}")] = (sx, sy, step_w, step_h, box)
            y += step_h + step_gap

        # --- Arrows between steps ---
        for i in range(len(steps) - 1):
            fid = steps[i].get("id", f"s{i}")
            tid = steps[i + 1].get("id", f"s{i+1}")
            if fid in pos and tid in pos:
                fx, fy, fw, fh, fe = pos[fid]
                tx, ty, tw, th, te = pos[tid]
                ax1, ay1 = fx + fw / 2, fy + fh
                ax2, ay2 = tx + tw / 2, ty
                arrs = self._arrow(ax1, ay1, ax2, ay2,
                                   start_id=fe["id"], end_id=te["id"])
                self.elements.extend(arrs)

        dh = y - self._current_y + 20
        self._current_y = y + DIAGRAM_GAP
        return (step_w + 100, dh)

    # --- Icons & Decorations ---

    def _load_icons(self):
        path = os.path.join(SKILL_DIR, "references", "icons.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("icons", {})

    def _place_icon(self, icon_name, x, y, scale=1.0):
        icons = self._load_icons()
        if icon_name not in icons:
            return []
        icon = icons[icon_name]
        placed = []
        gid = self._gid("ico")
        for e in icon["elements"]:
            if e["type"] == "text":
                continue
            ne = dict(e)
            ne["x"] = round(x + e["x"] * scale, 1)
            ne["y"] = round(y + e["y"] * scale, 1)
            if "width" in ne:
                ne["width"] = round(e["width"] * scale, 1)
            if "height" in ne:
                ne["height"] = round(e["height"] * scale, 1)
            if "angle" not in ne:
                ne["angle"] = 0
            if "fillStyle" not in ne:
                ne["fillStyle"] = "solid"
            if "opacity" not in ne:
                ne["opacity"] = 100
            if "strokeColor" not in ne:
                ne["strokeColor"] = "#1e1e1e"
            if "strokeWidth" not in ne:
                ne["strokeWidth"] = 2
            if "roughness" not in ne:
                ne["roughness"] = 1
            if "roundness" not in ne and ne["type"] in ("rectangle", "diamond", "ellipse"):
                ne["roundness"] = None
            if ne["type"] in ("line", "arrow", "freedraw") and ne.get("backgroundColor", "transparent") != "transparent":
                ne["backgroundColor"] = "transparent"
            if "points" in ne:
                ne["points"] = [[round(p[0] * scale, 1), round(p[1] * scale, 1)] for p in e["points"]]
            ne["id"] = self._gid("ic")
            ne["seed"] = self._seed()
            ne["version"] = 1
            ne["versionNonce"] = 0
            ne["isDeleted"] = False
            ne["groupIds"] = [gid]
            ne["updated"] = 1
            ne["link"] = None
            ne["locked"] = False
            if "boundElements" not in ne:
                ne["boundElements"] = None
            placed.append(ne)
        self.elements.extend(placed)
        iw = icon["width"] * scale
        ih = icon["height"] * scale
        return (iw, ih)

    def _apply_decorations(self, diagram, x, y, w, h):
        decos = diagram.get("decorations", [])
        for dec in decos:
            dtype = dec.get("type", "icon")
            if dtype == "icon":
                iname = dec.get("name", "")
                pos = dec.get("position", "top-right")
                iscale = dec.get("scale", 0.6)
                if pos == "top-right":
                    ix = x + w - 70 * iscale
                    iy = y - 20
                elif pos == "top-left":
                    ix = x - 20
                    iy = y - 20
                elif pos == "bottom-right":
                    ix = x + w - 70 * iscale
                    iy = y + h - 20
                elif pos == "inline-left":
                    ix = x - 80 * iscale
                    iy = y + h/2 - 50 * iscale
                else:
                    ix = x + w/2 - 35 * iscale
                    iy = y - 70 * iscale
                self._place_icon(iname, ix, iy, iscale)

    # --- Visual Card ---

    def _card_accent_bar(self, x, y, w, h, color, position="top", fill_style="solid"):
        if position == "left":
            return self._rect(x, y, 8, h, color, stroke=color, fill_style=fill_style,
                              roundness={"type": 3})
        else:
            return self._rect(x, y, w, 8, color, stroke=color, fill_style=fill_style,
                              roundness={"type": 3})

    def _layout_visual_card(self, data):
        title = data.get("title", "")
        content = data.get("content", "")
        icon = data.get("icon", "")
        card_style = data.get("card_style", "rounded")
        x = CANVAS_MARGIN
        y = self._current_y
        card_w = 660

        accent_color = self._colors.get("accent", PALETTE["accent_stroke"])
        card_fill = PALETTE["card_fill"]
        card_stroke = PALETTE["card_stroke"]
        text_color = self._colors.get("text") if self._colors else PALETTE["text_color"]

        roundness_val = {"type": 3}
        card_opacity = 92
        content_x_offset = 28
        title_x_offset = 28

        if card_style == "rounded":
            pass

        elif card_style == "accent-left":
            content_x_offset = 40
            title_x_offset = 40

        elif card_style == "accent-top":
            y += 10

        elif card_style == "pattern":
            card_opacity = 95

        elif card_style == "minimal":
            card_opacity = 100
            card_fill = "transparent"

        elif card_style == "banner":
            card_opacity = 85
            card_w = 680

        if card_style == "accent-left":
            bar = self._card_accent_bar(x, y, 8, 200, accent_color, "left",
                                        fill_style="solid")
            self.elements.append(bar)
        elif card_style == "accent-top":
            bar = self._card_accent_bar(x, y, card_w, 10, accent_color, "top",
                                        fill_style="solid")
            self.elements.append(bar)

        if card_style == "pattern":
            card = self._rect(x, y, card_w, 200, card_fill,
                              roundness=roundness_val, opacity=card_opacity,
                              fill_style="cross-hatch", stroke=card_stroke)
        else:
            card = self._rect(x, y, card_w, 200, card_fill,
                              roundness=roundness_val, opacity=card_opacity,
                              stroke=card_stroke)
        self.elements.append(card)

        yp = y + 24
        if title:
            tis = self._typo.get("title_size") if self._typo else 20
            if card_style == "banner":
                tis = 24
            disp = f"{icon}  {title}" if icon else title
            tw = estimate_text_width_raw(disp, tis) + 40
            te = self._text(x + title_x_offset, yp, max(tw, 240), 34, disp,
                            font_size=tis, text_align="left", color=text_color)
            self.elements.append(te)
            yp += 48 if card_style != "banner" else 56

        if content:
            lines = content.split("\n")
            for line in lines:
                if not line.strip():
                    yp += 12 if card_style != "banner" else 18
                    continue
                cfs = self._typo.get("detail_size") if self._typo else 14
                if card_style == "banner":
                    cfs = 15
                cw_e = estimate_text_width_raw(line.strip(), cfs) + 40
                ct = self._text(x + content_x_offset, yp, min(cw_e, card_w - 60), 26,
                                line.strip(), font_size=cfs, text_align="left",
                                color=text_color)
                self.elements.append(ct)
                yp += 32 if card_style != "banner" else 36

        dh = yp - y + 32
        card["height"] = dh
        if card_style in ("accent-left", "accent-top"):
            bar["height"] = dh
        self._current_y = y + dh + DIAGRAM_GAP
        return (card_w + 100, dh)

    # --- Public API ---

    def apply_style(self, diagram):
        preset_name = diagram.get("style") if isinstance(diagram, dict) else None
        if preset_name and not self._preset:
            loaded = load_style_preset(preset_name)
            if loaded:
                self._preset = loaded
                self._colors = loaded.get("colors", {})
                self._fills = loaded.get("fills", {})
                self._deco = loaded.get("decorations", {})
                self._typo = loaded.get("typography", {})

    def add_diagram(self, diagram):
        self.apply_style(diagram)
        dtype = diagram.get("type", "flowchart")
        handler_name = f"_layout_{dtype}"
        handler = getattr(self, handler_name, None)
        if handler:
            start_y = self._current_y
            result = handler(diagram)
            if diagram.get("decorations"):
                d_w, d_h = result if result else (0, 0)
                self._apply_decorations(diagram, CANVAS_MARGIN, start_y, d_w or 600, d_h or 200)
            return result
        print(f"Warning: unknown diagram type '{dtype}'", file=sys.stderr)
        return (0, 0)

    def build(self, diagrams, style_preset=None):
        if style_preset:
            self._preset = style_preset
            self._colors = style_preset.get("colors", {})
            self._fills = style_preset.get("fills", {})
            self._deco = style_preset.get("decorations", {})
            self._typo = style_preset.get("typography", {})
        global_decos = {}
        for d in diagrams:
            self.add_diagram(d)

    def save(self, filepath):
        if not self.elements:
            max_x, max_y = 800, 600
        else:
            max_x = max(e["x"] + e.get("width", 0) + 60 for e in self.elements)
            max_y = max(e["y"] + e.get("height", 0) + 60 for e in self.elements)
            for e in self.elements:
                points = e.get("points")
                if points:
                    for pt in points:
                        max_x = max(max_x, e["x"] + pt[0] + 60)
                        max_y = max(max_y, e["y"] + pt[1] + 60)
        data = {
            "type": "excalidraw",
            "version": 2,
            "source": "excalidraw-visualizer-skill",
            "elements": self.elements,
            "appState": {
                "viewBackgroundColor": "#ffffff",
                "gridSize": None,
            },
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Excalidraw layout engine")
    parser.add_argument("--input", "-i", required=True,
                        help="Input JSON file with diagram structures")
    parser.add_argument("--output", "-o", required=True,
                        help="Output .excalidraw file path")
    parser.add_argument("--style", "-s", default=None,
                        help="Style preset name (professional/warm/minimal/vivid/dark)")
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    diagrams = data.get("diagrams", [data] if "type" in data else [])
    if not diagrams:
        print("Error: no diagrams found in input", file=sys.stderr)
        sys.exit(1)

    style_preset = None
    style_name = args.style or data.get("style", "professional")
    if style_name:
        style_preset = load_style_preset(style_name)
        if style_preset is None and args.style:
            print(f"Warning: style '{args.style}' not found, using defaults",
                  file=sys.stderr)

    builder = ExcalidrawBuilder(style_preset=style_preset)
    builder.build(diagrams, style_preset=style_preset)
    builder.save(args.output)
    print(f"Saved {len(diagrams)} diagram(s) to: {args.output}")


if __name__ == "__main__":
    main()
