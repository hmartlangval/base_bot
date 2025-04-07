from typing import TypedDict, Optional

class BrowserSessionConfig(TypedDict, total=False):
    annual_pdf_filename: Optional[str]
    original_json: Optional[dict]
