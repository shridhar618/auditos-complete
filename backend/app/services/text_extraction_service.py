"""
Extracts plain text from an uploaded file so it can be previewed,
searched, and (for policy documents) chunked and embedded.

Native extraction (pypdf / python-docx / plain read) is tried first.
For PDFs that come back empty or near-empty (a strong signal the PDF
is a scanned image rather than digital text), OCR is attempted via
pytesseract + pdf2image. Both of those require system binaries
(tesseract-ocr, poppler-utils) that may not be installed - if so, we
catch that and report `extraction_method="unsupported"` with a clear
error rather than crashing the request or fabricating text.
"""
from dataclasses import dataclass

MIN_NATIVE_TEXT_LENGTH = 20  # below this, assume the PDF is a scanned image


@dataclass
class ExtractionResult:
    text: str
    method: str  # "native", "ocr", "unsupported"
    error: str | None = None


def extract_text(file_path: str, content_type: str | None) -> ExtractionResult:
    if content_type == "application/pdf" or file_path.lower().endswith(".pdf"):
        return _extract_pdf(file_path)
    if content_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ) or file_path.lower().endswith(".docx"):
        return _extract_docx(file_path)
    if content_type in ("text/plain", "text/csv") or file_path.lower().endswith((".txt", ".csv", ".md")):
        return _extract_plain_text(file_path)

    return ExtractionResult(text="", method="unsupported", error=f"No text extraction available for {content_type}.")


def _extract_pdf(file_path: str) -> ExtractionResult:
    try:
        from pypdf import PdfReader

        reader = PdfReader(file_path)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as exc:
        return ExtractionResult(text="", method="unsupported", error=f"Failed to read PDF: {exc}")

    if len(text.strip()) >= MIN_NATIVE_TEXT_LENGTH:
        return ExtractionResult(text=text, method="native")

    # Likely a scanned/image-only PDF - attempt OCR.
    ocr_result = _try_ocr_pdf(file_path)
    if ocr_result is not None:
        return ocr_result

    return ExtractionResult(
        text=text,
        method="unsupported",
        error="This PDF appears to be scanned and OCR is unavailable (tesseract/poppler not installed).",
    )


def _try_ocr_pdf(file_path: str) -> ExtractionResult | None:
    try:
        import pytesseract
        from pdf2image import convert_from_path

        pages = convert_from_path(file_path)
        text = "\n".join(pytesseract.image_to_string(page) for page in pages)
        if text.strip():
            return ExtractionResult(text=text, method="ocr")
        return ExtractionResult(text="", method="ocr", error="OCR ran but found no readable text.")
    except Exception:
        # tesseract/poppler not installed, or OCR failed for another reason -
        # degrade gracefully rather than raising.
        return None


def _extract_docx(file_path: str) -> ExtractionResult:
    try:
        import docx

        document = docx.Document(file_path)
        text = "\n".join(p.text for p in document.paragraphs)
        return ExtractionResult(text=text, method="native")
    except Exception as exc:
        return ExtractionResult(text="", method="unsupported", error=f"Failed to read DOCX: {exc}")


def _extract_plain_text(file_path: str) -> ExtractionResult:
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return ExtractionResult(text=f.read(), method="native")
    except Exception as exc:
        return ExtractionResult(text="", method="unsupported", error=f"Failed to read file: {exc}")
