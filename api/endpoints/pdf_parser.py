from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
import tempfile
import magic
import logging
from services.pdf_service import parse_pdf
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {"application/pdf", "application/x-pdf"}

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def parse_pdf_endpoint(
    pdf: UploadFile = File(..., max_length=MAX_FILE_SIZE),
    documentName: str = Form(None, max_length=100),
    verification: bool = Form(False)
):
    """
    Secure PDF processing endpoint with validation:
    - Limits file size to 10MB
    - Verifies actual file type using magic numbers
    - Processes files on disk to avoid memory issues
    """
    try:
        # Validate file type using magic numbers
        file_header = await pdf.read(2048)
        await pdf.seek(0)
        mime_type = magic.from_buffer(file_header, mime=True)
        
        if mime_type not in ALLOWED_MIME_TYPES:
            logger.warning(f"Rejected invalid file type: {mime_type}")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="Only PDF files are accepted"
            )

        # Process in temporary directory
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / pdf.filename
            with tmp_path.open("wb") as buffer:
                while content := await pdf.read(1024 * 1024):  # 1MB chunks
                    buffer.write(content)
            
            full_text = parse_pdf(tmp_path)
            
            # Analysis logic preserved
            fraudRisk = False
            if verification and documentName:
                fraudRisk = documentName not in full_text

            return {
                "success": True,
                "extractedText": full_text[:500],
                "fraudRisk": fraudRisk,
                "analyzedChars": len(full_text)
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("PDF processing failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF processing error"
        )