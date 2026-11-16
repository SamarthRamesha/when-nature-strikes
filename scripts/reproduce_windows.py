"""Rebuild the exact authorized snapshot and its local analytical artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/source/EM-DAT Custom Request Oct 31 2026.xlsx"
REFERENCE = ROOT / "results/provenance.json"


def sha256(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def run(*args, **options):
    print("Running", " ".join(map(str, args)), flush=True)
    subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True, **options)


def rebuild(workbook, prepare_only):
    expected = json.loads(REFERENCE.read_text(encoding="utf-8"))
    if not workbook.is_file():
        raise FileNotFoundError(f"Place the matching authorized workbook at {SOURCE}, or pass --workbook.")
    if sha256(workbook) != expected["source_sha256"]:
        raise ValueError("Workbook SHA-256 differs from the authorized 23 October 2026 snapshot in results/provenance.json.")
    if workbook.resolve() != SOURCE.resolve():
        if SOURCE.exists() and sha256(SOURCE) != expected["source_sha256"]:
            raise ValueError(f"A different workbook exists at {SOURCE}. Move it aside before rebuilding.")
        if not SOURCE.exists():
            shutil.copyfile(workbook, SOURCE)
    with tempfile.TemporaryFile() as capture:
        run("scripts/prepare_emdat.py", stdout=capture)
        capture.seek(0)
        actual = json.load(capture)
    if actual["output_sha256"] != expected["output_sha256"]:
        raise ValueError("Processed CSV SHA-256 values differ from the committed reference.")
    print("Verified workbook and all four processed checksums.", flush=True)
    run("scripts/validate_project_data.py")
    run("scripts/verify_eda_findings.py")
    if not prepare_only:
        for module in ("statistics", "model", "xai", "profiles", "geography"):
            run("-m", f"src.{module}")
        run("-m", "unittest", "discover", "-s", "tests", "-v")
        run("scripts/check_submission.py")


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--workbook", type=Path, default=SOURCE)
    args.add_argument("--prepare-only", action="store_true")
    parsed = args.parse_args()
    rebuild(parsed.workbook.resolve(), parsed.prepare_only)
