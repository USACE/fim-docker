#!/usr/bin/env python3
"""CGI gateway that applies dynamic inundation class colors via Python MapScript."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from typing import Dict, Iterable, Tuple
from urllib.parse import parse_qs, parse_qsl, urlencode

HEX_COLOR_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")
SHORT_RGB_KEY_RE = re.compile(r"^c[1-4][rgb]$", re.IGNORECASE)

# Supported aliases from runtime/etc/mapserver.conf MAPS block.
MAP_ALIASES = {
    "inundation": "/etc/mapserver/maps/inundation.map",
    "hsip": "/etc/mapserver/maps/hsip.map",
    "national": "/etc/mapserver/maps/national.map",
    "nid": "/etc/mapserver/maps/nid.map",
    "political": "/etc/mapserver/maps/political.map",
    "rim": "/etc/mapserver/maps/rim.map",
    "simdams": "/etc/mapserver/maps/simdams.map",
    "usace": "/etc/mapserver/maps/usace.map",
}

# Maps class names to dynamic color slots.
CLASS_COLOR_SLOT = {
    "color_1_1": "custom_color_1",
    "color_2_1": "custom_color_1",
    "color_3_1": "custom_color_1",
    "color_4_1": "custom_color_1",
    "color_2_2": "custom_color_2",
    "color_3_2": "custom_color_2",
    "color_4_2": "custom_color_2",
    "color_3_3": "custom_color_3",
    "color_4_3": "custom_color_3",
    "color_4_4": "custom_color_4",
}


def cgi_fail(status: str, message: str) -> None:
    body = (message + "\n").encode("utf-8", errors="replace")
    sys.stdout.write(f"Status: {status}\r\n")
    sys.stdout.write("Content-Type: text/plain; charset=utf-8\r\n")
    sys.stdout.write(f"Content-Length: {len(body)}\r\n\r\n")
    sys.stdout.flush()
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def parse_hex_to_rgb(value: str) -> Tuple[int, int, int] | None:
    match = HEX_COLOR_RE.match(value.strip())
    if not match:
        return None
    token = match.group(1)
    return int(token[0:2], 16), int(token[2:4], 16), int(token[4:6], 16)


def parse_rgb_channel(value: str) -> int | None:
    token = (value or "").strip()
    if not token.isdigit():
        return None
    channel = int(token)
    if channel < 0 or channel > 255:
        return None
    return channel


def parse_positive_int(value: str | None) -> int | None:
    token = (value or "").strip()
    if not token or not token.isdigit():
        return None
    parsed = int(token)
    if parsed <= 0:
        return None
    return parsed


def get_slot_rgb(query: Dict[str, Iterable[str]], slot: str) -> Tuple[int, int, int] | None:
    # Preferred style: custom_color_1=#RRGGBB
    hex_value = first_query_value(query, slot)
    if hex_value is not None:
        return parse_hex_to_rgb(hex_value)

    # Alternate style 1: custom_color_1_r=208&custom_color_1_g=240&custom_color_1_b=255
    r1 = first_query_value(query, f"{slot}_r")
    g1 = first_query_value(query, f"{slot}_g")
    b1 = first_query_value(query, f"{slot}_b")

    # Alternate style 2: c1r=208&c1g=240&c1b=255
    slot_idx = slot.rsplit("_", 1)[-1]
    r2 = first_query_value(query, f"c{slot_idx}r")
    g2 = first_query_value(query, f"c{slot_idx}g")
    b2 = first_query_value(query, f"c{slot_idx}b")

    r = r1 if r1 is not None else r2
    g = g1 if g1 is not None else g2
    b = b1 if b1 is not None else b2

    if r is None and g is None and b is None:
        return None

    if r is None or g is None or b is None:
        return None

    rr = parse_rgb_channel(r)
    gg = parse_rgb_channel(g)
    bb = parse_rgb_channel(b)
    if rr is None or gg is None or bb is None:
        return None
    return rr, gg, bb


def resolve_mapfile(map_value: str) -> str | None:
    raw = map_value.strip()
    if not raw:
        return None

    alias_key = raw.lower()
    if alias_key in MAP_ALIASES:
        return MAP_ALIASES[alias_key]

    return None


def resolve_mapfile_from_path_info(path_info: str) -> str | None:
    cleaned = (path_info or "").strip("/")
    if not cleaned:
        return None
    alias = cleaned.split("/", 1)[0].lower()
    return MAP_ALIASES.get(alias)


def first_query_value(query: Dict[str, Iterable[str]], key: str) -> str | None:
    values = query.get(key)
    if not values:
        return None
    first = next(iter(values), None)
    return first if first is not None else None


def parse_requested_layers(query: Dict[str, Iterable[str]]) -> list[str]:
    raw_layers = first_query_value(query, "LAYERS") or first_query_value(query, "layers")
    if not raw_layers:
        return []

    layers: list[str] = []
    for token in raw_layers.split(","):
        name = token.strip()
        if not name:
            continue
        if name not in layers:
            layers.append(name)
    return layers


def find_layer_by_name(map_obj: object, layer_name: str) -> object | None:
    for layer_index in range(map_obj.numlayers):
        candidate = map_obj.getLayer(layer_index)
        if (candidate.name or "").strip() == layer_name:
            return candidate
    return None


def collect_mapscript_errors(mapscript_module: object) -> str:
    messages = []
    try:
        err = mapscript_module.msGetErrorObj()
        while err is not None:
            msg = (getattr(err, "message", "") or "").strip()
            routine = (getattr(err, "routine", "") or "").strip()
            code = getattr(err, "code", None)
            if msg:
                if routine:
                    messages.append(f"{routine}: {msg}")
                elif code is not None:
                    messages.append(f"[{code}] {msg}")
                else:
                    messages.append(msg)
            err = getattr(err, "next", None)
    except Exception:
        return ""

    return " | ".join(messages)


def is_color_query_key(key: str) -> bool:
    token = (key or "").strip().lower()
    if token.startswith("custom_color_"):
        return True
    return SHORT_RGB_KEY_RE.match(token) is not None


def rewrite_query_for_temp_map(query_string: str, map_path: str) -> str:
    pairs = parse_qsl(query_string, keep_blank_values=True)
    rewritten = []
    map_replaced = False

    for key, value in pairs:
        if is_color_query_key(key):
            # Colors have already been applied directly to the temporary map.
            continue

        if key.lower() == "map":
            if not map_replaced:
                rewritten.append((key, map_path))
                map_replaced = True
            continue

        rewritten.append((key, value))

    if not map_replaced:
        rewritten.insert(0, ("MAP", map_path))

    return urlencode(rewritten, doseq=True)


def run_mapserv_with_temp_map(map_obj: object, query_string: str, mapscript_module: object) -> tuple[bytes, bytes, int]:
    # Keep temporary maps under /etc/mapserver/maps so MAP validation accepts the path.
    temp_map_dir = os.environ.get("MAPSCRIPT_TEMP_MAP_DIR", "/etc/mapserver/maps").strip() or "/etc/mapserver/maps"
    if not os.path.isdir(temp_map_dir):
        raise RuntimeError(f"Temporary map directory does not exist: {temp_map_dir}")
    if not os.access(temp_map_dir, os.W_OK):
        raise PermissionError(
            f"Temporary map directory is not writable: {temp_map_dir}; "
            "grant write access to the Apache runtime user or set MAPSCRIPT_TEMP_MAP_DIR"
        )

    fd, temp_map_path = tempfile.mkstemp(prefix="mapscript_", suffix=".map", dir=temp_map_dir)
    os.close(fd)

    try:
        # mapObj.save() serializes SIZE -1 -1 when width/height are unset,
        # which later fails map parsing. Ensure a valid size first.
        if map_obj.width <= 0 or map_obj.height <= 0:
            query = parse_qs(query_string, keep_blank_values=False)
            req_width = parse_positive_int(first_query_value(query, "WIDTH") or first_query_value(query, "width"))
            req_height = parse_positive_int(first_query_value(query, "HEIGHT") or first_query_value(query, "height"))
            if req_width is not None and req_height is not None:
                map_obj.setSize(req_width, req_height)
            else:
                tilemode = (first_query_value(query, "tilemode") or "").strip().lower()
                has_tile = first_query_value(query, "tile") is not None
                if tilemode == "gmap" or has_tile:
                    map_obj.setSize(256, 256)

        save_status = map_obj.save(temp_map_path)
        if save_status != mapscript_module.MS_SUCCESS:
            raise RuntimeError("Failed to save temporary mapfile")

        rewritten_query = rewrite_query_for_temp_map(query_string, temp_map_path)
        child_env = os.environ.copy()
        child_env["QUERY_STRING"] = rewritten_query

        result = subprocess.run(
            ["/usr/local/bin/mapserv"],
            env=child_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return result.stdout, result.stderr, result.returncode
    finally:
        try:
            os.unlink(temp_map_path)
        except OSError:
            pass


def main() -> int:
    try:
        import mapscript  # type: ignore
    except Exception as exc:  # pragma: no cover
        cgi_fail("500 Internal Server Error", f"MapScript import failed: {exc}")
        return 1

    query_string = os.environ.get("QUERY_STRING", "")
    query = parse_qs(query_string, keep_blank_values=False)

    # Handle MAP/map keys, then fallback to alias from PATH_INFO.
    map_param = first_query_value(query, "MAP") or first_query_value(query, "map")
    mapfile = resolve_mapfile(map_param) if map_param else None
    if not mapfile:
        mapfile = resolve_mapfile_from_path_info(os.environ.get("PATH_INFO", ""))

    if not mapfile:
        cgi_fail("400 Bad Request", "Missing or invalid map target (MAP or PATH_INFO alias)")
        return 1

    color_by_slot: Dict[str, Tuple[int, int, int]] = {}
    for slot in ("custom_color_1", "custom_color_2", "custom_color_3", "custom_color_4"):
        rgb = get_slot_rgb(query, slot)
        if rgb is None:
            # Reject partially specified/invalid values with a targeted error.
            has_any_related_key = any(
                key in query
                for key in (
                    slot,
                    f"{slot}_r",
                    f"{slot}_g",
                    f"{slot}_b",
                    f"c{slot.rsplit('_', 1)[-1]}r",
                    f"c{slot.rsplit('_', 1)[-1]}g",
                    f"c{slot.rsplit('_', 1)[-1]}b",
                )
            )
            if has_any_related_key:
                cgi_fail(
                    "400 Bad Request",
                    (
                        f"Invalid color values for {slot}; use {slot}=#RRGGBB "
                        f"or {slot}_r/{slot}_g/{slot}_b (0-255) "
                        f"or c{slot.rsplit('_', 1)[-1]}r/c{slot.rsplit('_', 1)[-1]}g/c{slot.rsplit('_', 1)[-1]}b (0-255)"
                    ),
                )
                return 1
            continue
        color_by_slot[slot] = rgb

    if not color_by_slot:
        cgi_fail(
            "400 Bad Request",
            "No color values provided; use custom_color_* hex or RGB triplets",
        )
        return 1

    try:
        map_obj = mapscript.mapObj(mapfile)
    except Exception as exc:
        cgi_fail("500 Internal Server Error", f"Unable to load map: {exc}")
        return 1

    requested_layers = parse_requested_layers(query)
    target_layer_names = requested_layers if requested_layers else ["cog_xyz"]

    target_layers = []
    for layer_name in target_layer_names:
        layer = find_layer_by_name(map_obj, layer_name)
        if layer is not None:
            target_layers.append(layer)

    if not target_layers:
        if requested_layers:
            cgi_fail(
                "500 Internal Server Error",
                f"None of the requested layers were found in map: {', '.join(requested_layers)}",
            )
        else:
            cgi_fail("500 Internal Server Error", "Layer 'cog_xyz' not found in map")
        return 1

    # Apply only to known class names used by the custom* class groups.
    for layer in target_layers:
        for class_index in range(layer.numclasses):
            class_obj = layer.getClass(class_index)
            slot = CLASS_COLOR_SLOT.get((class_obj.name or "").strip())
            if not slot or slot not in color_by_slot:
                continue

            r, g, b = color_by_slot[slot]
            for style_index in range(class_obj.numstyles):
                style_obj = class_obj.getStyle(style_index)
                style_obj.color.setRGB(r, g, b)

    payload, stderr_bytes, status_code = run_mapserv_with_temp_map(map_obj, query_string, mapscript)

    if not payload:
        dispatch_message = stderr_bytes.decode("utf-8", errors="replace").strip()
        if not dispatch_message:
            dispatch_message = collect_mapscript_errors(mapscript)
        if not dispatch_message:
            dispatch_message = "MapServer CGI failed without output"
        cgi_fail("500 Internal Server Error", dispatch_message)
        return 1

    # mapserv returns complete CGI headers + body; pass through unchanged.
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()

    if status_code != 0:
        return 1

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        cgi_fail("500 Internal Server Error", f"Unhandled gateway error: {exc}")
        raise SystemExit(1)
