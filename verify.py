from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys

from PIL import Image


ROOT = Path(__file__).resolve().parent


def digest(content):
    return hashlib.sha256(content).hexdigest()


def run():
    renders = []
    for attempt in range(2):
        subprocess.run([sys.executable, str(ROOT / "gen.py")], cwd=ROOT, check=True, capture_output=True, text=True)
        renders.append((ROOT / "entry.png").read_bytes())
        print(f"Render {attempt + 1}: {digest(renders[-1])}")
    if renders[0] != renders[1]:
        raise AssertionError("The two deterministic renders differ")
    image_bytes = renders[0]
    if len(image_bytes) > 1048576:
        raise AssertionError("PNG exceeds 1 MiB")
    with Image.open(ROOT / "entry.png") as image:
        if image.format != "PNG" or image.size != (1024, 1024):
            raise AssertionError(f"Unexpected image format or dimensions: {image.format} {image.size}")
        image.verify()
    print(f"PASS: deterministic PNG; 1024×1024; {len(image_bytes)} bytes")
    verification_root = ROOT / ".verify"
    verification_root.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="run-", dir=verification_root) as temporary:
        temporary_root = Path(temporary)
        copies = []
        for label in ("A", "B"):
            working_directory = temporary_root / f"cwd-{label}"
            working_directory.mkdir()
            output_directory = temporary_root / f"output-{label}"
            environment = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(output_directory))
            result = subprocess.run(["node", str(ROOT / "main.ts")], cwd=working_directory, env=environment, check=True, capture_output=True, text=True)
            copied = (output_directory / "entry.png").read_bytes()
            if copied != image_bytes:
                raise AssertionError(f"Output {label} differs from entry.png")
            copies.append(copied)
            print(f"PASS: foreign-cwd copy {label}: {result.stdout.strip()}")
        if copies[0] != copies[1]:
            raise AssertionError("Copies A and B differ")
        fixtures = {
            "signature": (b"NOTPNG!!" + image_bytes[8:], "PNG signature"),
            "truncated": (image_bytes[:24], "complete IHDR"),
            "chunk-type": (image_bytes[:12] + b"IDAT" + image_bytes[16:], "13-byte IHDR"),
            "chunk-length": (image_bytes[:8] + struct.pack(">I", 12) + image_bytes[12:], "13-byte IHDR"),
            "width": (image_bytes[:16] + struct.pack(">I", 512) + image_bytes[20:], "1024×1024"),
            "height": (image_bytes[:20] + struct.pack(">I", 512) + image_bytes[24:], "1024×1024"),
            "size": (image_bytes + bytes(1048577 - len(image_bytes)), "exceeds 1048576"),
        }
        for label, (content, expected_error) in fixtures.items():
            fixture_directory = temporary_root / label
            fixture_directory.mkdir()
            shutil.copyfile(ROOT / "main.ts", fixture_directory / "main.ts")
            (fixture_directory / "entry.png").write_bytes(content)
            output_directory = fixture_directory / "output"
            environment = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(output_directory))
            result = subprocess.run(["node", str(fixture_directory / "main.ts")], cwd=temporary_root, env=environment, capture_output=True, text=True)
            if result.returncode == 0 or expected_error not in result.stderr:
                raise AssertionError(f"Invalid {label} PNG did not produce its expected clear error")
            if output_directory.exists():
                raise AssertionError(f"Invalid {label} PNG created output")
        print(f"PASS: {len(fixtures)} invalid-PNG rejection cases")
    report = json.loads((ROOT / "layout.json").read_text())
    for name, position in report["measurements"].items():
        budget = report["budgets"][name]
        if position > budget:
            raise AssertionError(f"{name}: {position} exceeds {budget}")
        print(f"{name}: y={position:g} / budget {budget:g} — PASS")
    print(f"entry.png sha256: {digest(image_bytes)}")
    print(f"entry.png byte size: {len(image_bytes)}")
    print(f"Runtime: {subprocess.check_output(['node', '--version'], text=True).strip()}")


if __name__ == "__main__":
    run()
