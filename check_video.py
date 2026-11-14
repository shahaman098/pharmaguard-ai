#!/usr/bin/env python3
"""Verify a demo video's duration from its mvhd atom (pure Python standard library, zero dependencies).

Usage:
  python3 check_video.py path/to/video.mp4

Checks the video against the project's recommended 2:00–3:00 minute demo window.
(DSH Hacks V2 does not publish a hard duration requirement; this is a quality target.)
"""
import struct
import sys
from pathlib import Path


def find_mvhd(data: bytes) -> bytes:
    # Walk the ISO-BMFF box tree to locate the mvhd box.
    def walk(buf: bytes, start: int, end: int):
        i = start
        while i + 8 <= end:
            size = struct.unpack(">I", buf[i : i + 4])[0]
            kind = buf[i + 4 : i + 8]
            header = 8
            if size == 1:
                size = struct.unpack(">Q", buf[i + 8 : i + 16])[0]
                header = 16
            elif size == 0:
                size = end - i
            if kind == b"moov":
                yield from walk(buf, i + header, i + size)
            elif kind == b"mvhd":
                yield buf[i : i + size]
                return
            i += size if size else end

    for box in walk(data, 0, len(data)):
        return box
    raise SystemExit("Error: mvhd atom not found — is this a valid MP4 file?")


def duration_seconds(path: Path) -> float:
    box = find_mvhd(path.read_bytes())
    version = box[8]
    if version == 1:
        timescale = struct.unpack(">I", box[28:32])[0]
        duration = struct.unpack(">Q", box[32:40])[0]
    else:
        timescale = struct.unpack(">I", box[20:24])[0]
        duration = struct.unpack(">I", box[24:28])[0]
    return duration / timescale if timescale else 0.0


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: File not found: {path}")
        return 2
    seconds = duration_seconds(path)
    minutes, secs = divmod(int(round(seconds)), 60)
    ok = 120.0 <= seconds <= 180.0
    verdict = "PASS (inside 2:00–3:00 sweet spot)" if ok else "FAIL (outside 2:00–3:00 sweet spot)"
    print(f"[{path.name}] Duration: {minutes}:{secs:02d} ({seconds:.1f}s) -> {verdict}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
