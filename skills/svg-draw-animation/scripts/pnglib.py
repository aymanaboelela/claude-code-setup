#!/usr/bin/env python3
"""Minimal dependency-free PNG decode/encode + foreground-mask detection.

Shared by logo_probe.py and trace_check.py. Supports colortypes 0/2/3/4/6,
8-bit channels, all 5 scanline filters. No PIL / numpy required.
"""
import struct
import zlib


def decode_png(path):
    """Return (w, h, nchannels, pixels_bytes). pixels are row-major, nch bytes
    per pixel. For palette images the palette is already applied to RGB."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    pos = 8
    idat = b""
    w = h = bitdepth = colortype = None
    plte = None
    trns = None
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            w, h, bitdepth, colortype = struct.unpack(">IIBB", chunk[:10])
        elif ctype == b"IDAT":
            idat += chunk
        elif ctype == b"PLTE":
            plte = chunk
        elif ctype == b"tRNS":
            trns = chunk
        pos += 12 + length
    if bitdepth != 8:
        raise ValueError(f"only 8-bit PNGs supported (got {bitdepth}-bit)")
    raw = zlib.decompress(idat)
    nch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colortype]
    stride = w * nch
    out = bytearray(w * h * nch)
    prev = bytearray(stride)
    p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p + stride]); p += stride
        if f == 1:
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                b = prev[i]
                c = prev[i - nch] if i >= nch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line

    # Expand palette to RGB so callers can treat everything uniformly.
    if colortype == 3 and plte is not None:
        rgb = bytearray(w * h * 3)
        for i in range(w * h):
            idx = out[i]
            rgb[i * 3:i * 3 + 3] = plte[idx * 3:idx * 3 + 3]
        return w, h, 3, bytes(rgb)
    return w, h, nch, bytes(out)


def foreground_mask(w, h, nch, px, threshold=48):
    """1 = logo ink, 0 = background. Uses alpha if present; otherwise treats
    the top-left corner pixel as the background color and marks pixels whose
    color distance exceeds `threshold` as foreground."""
    mask = bytearray(w * h)
    has_alpha = nch in (2, 4)
    if has_alpha:
        varied = False
        first = px[nch - 1]
        for i in range(0, w * h, max(1, (w * h) // 512)):
            if px[i * nch + nch - 1] != first:
                varied = True
                break
        if varied:
            for i in range(w * h):
                mask[i] = 1 if px[i * nch + nch - 1] > 127 else 0
            return mask
    # color-distance against corner background
    bg = px[0:nch]
    for i in range(w * h):
        d = 0
        for c in range(min(nch, 3)):
            d += abs(px[i * nch + c] - bg[c])
        mask[i] = 1 if d > threshold else 0
    return mask


def encode_png_rgb(path, w, h, rgb):
    """Write an 8-bit RGB PNG from a flat bytes/bytearray of length w*h*3."""
    def chunk(typ, payload):
        body = typ + payload
        return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))
    raw = b"".join(b"\x00" + bytes(rgb[y * w * 3:(y + 1) * w * 3]) for y in range(h))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)
