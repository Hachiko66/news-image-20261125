#!/usr/bin/env python3
"""Copy the finished news image to the output directory.

Stdlib only. The image (entry.png, drawn at build time by render.py) is
validated first -- PNG signature, at most 1 MiB, at most 1024x1024 -- then
written atomically (temporary file in the output directory, then rename)
and given mode 0644, which the grader requires.
"""
import os
import struct
import sys

MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def read_png_size(path):
    """Return (width, height) from a PNG's IHDR chunk."""
    with open(path, "rb") as handle:
        header = handle.read(33)
    if header[:8] != PNG_MAGIC:
        raise ValueError("entry.png is not a PNG file")
    if len(header) < 33 or header[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def is_whole_png(path):
    """True when the file ends with a complete IEND chunk."""
    with open(path, "rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        if size < 12:
            return False
        handle.seek(size - 12)
        tail = handle.read(12)
    return tail == b"\x00\x00\x00\x00IEND\xaeB`\x82"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, "entry.png")

    size = os.path.getsize(source)
    if size > MAX_BYTES:
        print(f"entry.png is {size} bytes, over the 1 MiB limit", file=sys.stderr)
        return 1
    width, height = read_png_size(source)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print(f"entry.png is {width}x{height}, over the 1024x1024 limit",
              file=sys.stderr)
        return 1
    if not is_whole_png(source):
        print("entry.png is truncated (no IEND chunk)", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, ".entry.png.tmp")
    try:
        with open(source, "rb") as src, open(tmp, "wb") as dst:
            while True:
                chunk = src.read(65536)
                if not chunk:
                    break
                dst.write(chunk)
            dst.flush()
            os.fsync(dst.fileno())
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    os.chmod(target, 0o644)
    print(f"wrote {target} ({size} bytes, {width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
