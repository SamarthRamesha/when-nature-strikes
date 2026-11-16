"""Validate packaged files and shared headline results without the workbook."""
import json
from pathlib import Path
import re
import zipfile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "submission"


def check():
    findings = json.loads((ROOT / "results/findings.json").read_text())
    models = json.loads((ROOT / "results/model_metrics.json").read_text())
    model = models["test"][models["selected"]]
    pdf_text = {}
    for filename, min_pages in [("final_report", 14), ("final_presentation", 18)]:
        reader = PdfReader(SUBMISSION / f"{filename}.pdf")
        assert len(reader.pages) >= min_pages
        pages = [page.extract_text() for page in reader.pages]
        assert all(page.strip() for page in pages)
        pdf_text[filename] = re.sub(r"\s+", " ", " ".join(pages))
    for text in pdf_text.values():
        assert f"{findings['events']:,}" in text, "Event count missing"
        assert f"{model['average_precision']:.3f}" in text, "Model AP missing"
    for filename, required in [
        ("final_report.docx", "word/document.xml"),
        ("final_presentation.pptx", "ppt/slides/slide18.xml"),
    ]:
        with zipfile.ZipFile(SUBMISSION / filename) as package:
            assert package.testzip() is None
            assert required in package.namelist()
            if filename.endswith("pptx"):
                assert "ppt/notesSlides/notesSlide18.xml" in package.namelist()
    for name in ("presenter_script.md", "dashboard_demo_guide.md", "viva_questions.md"):
        assert len((SUBMISSION / name).read_text(encoding="utf-8")) > 1000
    print("Submission verification passed for Word, PowerPoint, both PDFs, notes, and headline results.")


if __name__ == "__main__":
    check()
