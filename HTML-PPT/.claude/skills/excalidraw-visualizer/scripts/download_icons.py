#!/usr/bin/env python3
"""Download icons from Excalidraw public libraries into icons.json.

Usage:
    python3 scripts/download_icons.py [--libraries LIBRARIES_JSON]
"""

import json
import os
import sys
import urllib.request

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_PATH = os.path.join(SKILL_DIR, "references", "icons.json")
LIBRARIES_URL = "https://raw.githubusercontent.com/excalidraw/excalidraw-libraries/main/libraries.json"

BASE_URL = "https://libraries.excalidraw.com/libraries/"

# Libraries we want to extract icons from
TARGET_LIBRARIES = {
    "youritjang/stick-figures": {
        "name": "Stick Figures",
        "icon_map": {
            "Stick man": "StickMan",
            "Happy": "Happy",
            "Sad": "Sad",
            "Girl": "Girl",
            "Guy": "Guy",
            "Shrug": "Shrug",
            "Child": "Child",
            "Grandma": "Grandma",
            "Moustache man": "MoustacheMan",
        }
    },
    "morgemoensch/gadgets": {
        "name": "Gadgets",
        "icon_map": {
            "__auto__": True,
        }
    },
    "dwelle/network-topology-icons": {
        "name": "Network",
        "icon_map": {
            "__auto__": True,
        }
    },
    "dwelle/hearts": {
        "name": "Hearts",
        "icon_map": {
            "__auto__": True,
        }
    },
    "ocapraro/bubbles": {
        "name": "Bubbles",
        "icon_map": {
            "__auto__": True,
        }
    },
    "xxxdeveloper/icons": {
        "name": "Icons",
        "icon_map": {
            "__auto__": True,
        }
    },
    "ei-au/computers": {
        "name": "Computers",
        "icon_map": {
            "__auto__": True,
        }
    },
    "drwnio/storytelling": {
        "name": "Storytelling",
        "icon_map": {
            "__auto__": True,
        }
    },
    "anumithaapollo12/emojis": {
        "name": "Emojis",
        "icon_map": {
            "__auto__": True,
        }
    },
    "ferminrp/awesome-icons": {
        "name": "Awesome Icons",
        "icon_map": {
            "__auto__": True,
        }
    },
    "kinghavok/some-common-cloud-apps": {
        "name": "Cloud Apps",
        "icon_map": {
            "__auto__": True,
        }
    },
    "aleksandr-hovhannisyan/clocks": {
        "name": "Clocks",
        "icon_map": {
            "__auto__": True,
        }
    },
    "marwinburesch/github-icons": {
        "name": "GitHub Icons",
        "icon_map": {
            "__auto__": True,
        }
    },
    "youritjang/software-architecture": {
        "name": "Software Architecture",
        "icon_map": {
            "__auto__": True,
        }
    },
    "xxxdeveloper/system-icons": {
        "name": "System Icons",
        "icon_map": {
            "__auto__": True,
        }
    },
    "swissarmysam/maps": {
        "name": "Maps",
        "icon_map": {
            "__auto__": True,
        }
    },
    "g-script/charts": {
        "name": "Charts",
        "icon_map": {
            "__auto__": True,
        }
    },
    "pclainchard/it-logos": {
        "name": "IT Logos",
        "icon_map": {
            "__auto__": True,
        }
    },
}


def fetch_json(url, retries=2):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"  Attempt {attempt+1}/{retries} failed: {e}", file=sys.stderr)
            if attempt < retries - 1:
                import time
                time.sleep(2)
    return None


def normalize_coords(elements):
    if not elements:
        return elements, 0, 0
    min_x = min(e["x"] for e in elements)
    min_y = min(e["y"] for e in elements)
    for e in elements:
        e["x"] = round(e["x"] - min_x, 1)
        e["y"] = round(e["y"] - min_y, 1)
    max_x = max(e["x"] + e.get("width", 0) for e in elements)
    max_y = max(e["y"] + e.get("height", 0) for e in elements)
    return elements, max_x, max_y


def extract_items(data, icon_map, lib_prefix="Lib"):
    items = data.get("libraryItems", [])
    # version 1: "library"
    if not items:
        items = data.get("library", [])
    # version 2 with items per-group
    if not items:
        for entry in data.get("library", []):
            if isinstance(entry, list):
                items.append(entry)
            elif isinstance(entry, dict) and "elements" in entry:
                items.append(entry["elements"])

    results = {}
    for i, item in enumerate(items):
        if isinstance(item, list):
            elements_raw = item
            item_name = f"item_{i}"
        elif isinstance(item, dict):
            elements_raw = item.get("elements", [])
            item_name = item.get("name", f"item_{i}")
        else:
            continue

        if icon_map and not icon_map.get("__auto__"):
            mapped_name = icon_map.get(item_name)
            if not mapped_name:
                continue
        else:
            # clean up name for use as a key
            name = item_name.replace(" ", "_").replace("/", "_").replace(".", "_").replace("-", "_")
            # Skip items that are way too large (full page templates, etc.)
            mapped_name = f"{lib_prefix}_{name}"

        cleaned = []
        for e in elements_raw:
            if not isinstance(e, dict):
                continue
            el = {
                "type": e["type"],
                "x": e["x"],
                "y": e["y"],
                "angle": e.get("angle", 0),
            }
            if "width" in e:
                el["width"] = e["width"]
            if "height" in e:
                el["height"] = e["height"]
            if "strokeColor" in e and e["strokeColor"] != "#000000":
                el["strokeColor"] = e["strokeColor"]
            if "backgroundColor" in e and e["backgroundColor"] != "#ffffff":
                el["backgroundColor"] = e["backgroundColor"]
            if "fillStyle" in e and e.get("fillStyle") != "solid":
                el["fillStyle"] = e["fillStyle"]
            if "roughness" in e and e["roughness"] != 0:
                el["roughness"] = e["roughness"]
            if e["type"] == "text" and "text" in e:
                el["text"] = e["text"]
                el["fontSize"] = e.get("fontSize", 16)
                el["fontFamily"] = e.get("fontFamily", 1)
            if e["type"] in ("line", "arrow", "freedraw") and "points" in e:
                el["points"] = e["points"]
            if e["type"] == "freedraw":
                for attr in ("pressures", "simulatePressure", "lastCommittedPoint"):
                    if attr in e:
                        el[attr] = e[attr]
            if "roundness" in e and e["roundness"] is not None:
                el["roundness"] = e["roundness"]
            if "opacity" in e and e["opacity"] != 100:
                el["opacity"] = e["opacity"]
            if "strokeWidth" in e and e["strokeWidth"] != 1:
                el["strokeWidth"] = e["strokeWidth"]
            if "strokeStyle" in e and e["strokeStyle"] != "solid":
                el["strokeStyle"] = e["strokeStyle"]
            # Post-processing: ensure valid values for icon use
            if "fillStyle" not in el:
                el["fillStyle"] = "solid"
            if "opacity" not in el:
                el["opacity"] = 100
            if "strokeColor" not in el:
                el["strokeColor"] = "#1e1e1e"
            if el["type"] in ("line", "arrow", "freedraw") and el.get("backgroundColor", "transparent") != "transparent":
                el["backgroundColor"] = "transparent"
            cleaned.append(el)

        if not cleaned:
            continue

        cleaned, w, h = normalize_coords(cleaned)

        # Skip items that are unreasonably large (likely page templates, not icons)
        if w > 600 or h > 600:
            print(f"    Skipping {mapped_name}: too large ({w:.0f}x{h:.0f})")
            continue

        results[mapped_name] = {
            "width": round(w, 1),
            "height": round(h, 1),
            "elements": cleaned,
        }

    return results


def main():
    out_path = ICONS_PATH
    existing = {}
    if os.path.exists(out_path):
        with open(out_path, "r") as f:
            existing = json.load(f)

    all_icons = existing.get("icons", {})

    for lib_slug, lib_cfg in sorted(TARGET_LIBRARIES.items()):
        url = f"{BASE_URL}{lib_slug}.excalidrawlib"
        print(f"Fetching {lib_slug}...")
        data = fetch_json(url)
        if not data:
            print(f"  Skipping.", file=sys.stderr)
            continue
        print(f"  Got data, extracting icons...")

        # Use a short library prefix to namespace auto-generated names
        lib_prefix = lib_cfg.get("name", lib_slug.split("/")[-1].replace("-", "_"))
        icon_map = lib_cfg.get("icon_map", {})
        if icon_map.get("__auto__"):
            icon_map = {"__auto__": True, "__lib_prefix__": lib_prefix}

        icons = extract_items(data, icon_map, lib_prefix=lib_prefix)
        print(f"  Extracted {len(icons)} icons:")
        for name in sorted(icons):
            ec = len(icons[name]["elements"])
            print(f"    {name}: {ec} elements, {icons[name]['width']}x{icons[name]['height']}")
        all_icons.update(icons)

    result = {"icons": all_icons}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(all_icons)} total icons to {out_path}")


if __name__ == "__main__":
    main()
