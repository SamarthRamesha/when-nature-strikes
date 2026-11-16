"""Check tracked release paths or package the committed tree and verify extraction."""
import argparse
import hashlib
from io import BytesIO
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAME = "WHEN_NATURE_STRIKES_COMPLETE_SUBMISSION"
REQUIRED = (
    "README.md", "NEXT_SESSION.md", "WINDOWS_HANDOVER/START_HERE.md", "submission/COMPLETION_MATRIX.csv",
    "submission/DELIVERABLES_MANIFEST.md", "submission/evidence/powerbi_author_cli.json",
    "submission/evidence/streamlit/01-overview.png", "submission/evidence/streamlit/05-story.png",
    "submission/evidence/streamlit/07-global-xai.png", "submission/evidence/streamlit/10-pca-3d.png",
    "submission/evidence/streamlit/13-data-quality.png", "results/xai/summary.json",
    "results/dimensionality_reduction/projection_cells.csv", "results/model_metrics.json",
    "submission/powerbi/demo/When_Nature_Strikes.pbip", "submission/final_report.pdf",
    "submission/final_report.docx", "submission/final_presentation.pdf", "submission/final_presentation.pptx",
)
SENSITIVE = {"country.csv", "country_by_year.csv", "type_by_year.csv", "map_unmatched.csv",
             "event_profiles.csv", "embeddings_local.csv", "predictions_local.csv", "ice_local.csv"}
FORBIDDEN_SEGMENTS = {".git", ".pbi", ".venv", "__pycache__", "node_modules", ".build", ".pytest_cache"}


def permitted(name):
    path = PurePosixPath(name.casefold())
    if path.parts[:2] in {("data", "source"), ("data", "processed")}:
        return path.as_posix() in {"data/source/readme.md", "data/processed/readme.md"}
    return (not path.is_absolute() and ".." not in path.parts
            and not FORBIDDEN_SEGMENTS.intersection(path.parts)
            and path.name not in SENSITIVE
            and path.suffix not in {".xls", ".xlsx", ".xlsb", ".xlsm", ".joblib", ".pbix", ".zip", ".pyc"}
            and path.parts[:3] != ("submission", "powerbi", "local"))


def check_tracked():
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    restricted = [name for name in tracked if name and not permitted(name)]
    if restricted:
        raise SystemExit("Restricted tracked paths:\n" + "\n".join(restricted))
    print("Tracked paths passed the public data and release file check.")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify(folder):
    assert all((folder / item).is_file() for item in REQUIRED)
    entries = (folder / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    assert entries
    for entry in entries:
        digest, item = entry.split("  ", 1)
        assert permitted(item) and sha(folder / item) == digest, item
    protected = [p.relative_to(folder).as_posix() for p in folder.rglob("*")
                 if p.is_file() and not permitted(p.relative_to(folder).as_posix())]
    assert not protected, protected


def build(destination):
    destination.mkdir(parents=True, exist_ok=True)
    folder, archive = destination / NAME, destination / f"{NAME}.zip"
    if folder.exists() or archive.exists():
        raise FileExistsError("Choose a new empty output location to preserve existing artifacts.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    payload = subprocess.check_output(["git", "archive", "--format=zip", commit], cwd=ROOT)
    with tempfile.TemporaryDirectory(dir=destination) as working:
        stage = Path(working) / NAME
        stage.mkdir()
        with zipfile.ZipFile(BytesIO(payload)) as previous:
            for item in previous.infolist():
                if item.is_dir():
                    continue
                relative = item.filename
                if not permitted(relative):
                    raise ValueError(f"Restricted or unexpected file in commit: {relative}")
                target = stage / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(previous.read(item))
        (stage / "PACKAGED_COMMIT.txt").write_text(commit + "\n", encoding="utf-8")
        items = sorted(p for p in stage.rglob("*") if p.is_file())
        (stage / "SHA256SUMS.txt").write_text(
            "".join(f"{sha(p)}  {p.relative_to(stage).as_posix()}\n" for p in items), encoding="utf-8")
        intermediate = Path(working) / archive.name
        with zipfile.ZipFile(intermediate, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as new:
            for file in [*items, stage / "SHA256SUMS.txt"]:
                new.write(file, f"{NAME}/{file.relative_to(stage).as_posix()}")
        with zipfile.ZipFile(intermediate) as new:
            assert new.testzip() is None
            new.extractall(Path(working) / "independent_verification")
        fresh = Path(working) / "independent_verification" / NAME
        verify(fresh)
        for commands in ([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                         [sys.executable, "scripts/check_submission.py"]):
            subprocess.run(commands, cwd=fresh, check=True)
        shutil.move(stage, folder)
        shutil.move(intermediate, archive)
    shutil.copyfile(folder / "submission/DELIVERABLES_MANIFEST.md", destination / "DELIVERABLES_MANIFEST.md")
    (destination / f"{archive.name}.sha256").write_text(f"{sha(archive)}  {archive.name}\n", encoding="utf-8")
    print(f"Verified {len(items)} files after a fresh extraction from {commit}.\n{archive}\n{folder}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--output", type=Path)
    action.add_argument("--check-tracked", action="store_true")
    options = parser.parse_args()
    if options.check_tracked:
        check_tracked()
    else:
        build(options.output.resolve())
