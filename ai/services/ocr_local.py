"""
Local OCR service using Tesseract
"""

import os
import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import time

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pdf2image
import cv2
import numpy as np

from models.ocr_models import (
    OCRRequest, OCRResult, OCRPage, OCRParagraph, OCRLine, OCRTable,
    BoundingBox, DocumentInfo, ProcessingMetadata
)
from utils.config import get_settings

logger = logging.getLogger(__name__)


class LocalOCRService:
    """Local OCR service using Tesseract"""

    def __init__(self):
        self.settings = get_settings()
        self._configure_tesseract()

    def _configure_tesseract(self):
        """Configure Tesseract settings"""
        if self.settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = self.settings.tesseract_cmd

        if self.settings.tesseract_data_path:
            os.environ['TESSDATA_PREFIX'] = self.settings.tesseract_data_path

    async def extract_text(self, request: OCRRequest, file_content: bytes, filename: str) -> OCRResult:
        """Extract text from document using Tesseract"""
        start_time = time.time()

        try:
            # Determine file type
            file_ext = Path(filename).suffix.lower()

            if file_ext == '.pdf':
                pages_data = await self._process_pdf(file_content, request)
            elif file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                pages_data = await self._process_image(file_content, request)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

            # Process pages
            ocr_pages = []
            full_text = ""

            for page_num, page_data in enumerate(pages_data, 1):
                ocr_page = await self._process_page(page_data, page_num, request)
                ocr_pages.append(ocr_page)
                full_text += ocr_page.text + "\n"

            # Calculate overall confidence
            if ocr_pages:
                overall_confidence = sum(page.confidence for page in ocr_pages) / len(ocr_pages)
            else:
                overall_confidence = 0.0

            # Create document info
            document_info = DocumentInfo(
                filename=filename,
                file_size=len(file_content),
                mime_type=self._get_mime_type(file_ext),
                page_count=len(ocr_pages),
                language=request.languages[0] if request.languages else "eng"
            )

            # Create processing metadata
            processing_metadata = ProcessingMetadata(
                provider="local",
                model="tesseract",
                processing_time=time.time() - start_time,
                parameters={
                    "languages": request.languages,
                    "extract_layout": request.extract_layout,
                    "extract_tables": request.extract_tables,
                    "options": request.options
                }
            )

            return OCRResult(
                text=full_text.strip(),
                confidence=overall_confidence,
                pages=ocr_pages,
                language=document_info.language,
                document_info=document_info,
                processing_metadata=processing_metadata
            )

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise

    async def _process_pdf(self, pdf_content: bytes, request: OCRRequest) -> List[np.ndarray]:
        """Process PDF file and convert to images"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_path = temp_file.name

            try:
                # Convert PDF to images
                loop = asyncio.get_event_loop()
                images = await loop.run_in_executor(
                    None,
                    lambda: pdf2image.convert_from_path(
                        temp_path,
                        dpi=300,  # High DPI for better OCR
                        fmt='RGB'
                    )
                )

                # Convert PIL images to numpy arrays
                pages_data = []
                for img in images:
                    img_array = np.array(img)
                    pages_data.append(img_array)

                return pages_data

            finally:
                # Cleanup temporary file
                os.unlink(temp_path)

        except Exception as e:
            logger.error(f"PDF processing failed: {e}")
            raise

    async def _process_image(self, image_content: bytes, request: OCRRequest) -> List[np.ndarray]:
        """Process image file"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(image_content)
                temp_path = temp_file.name

            try:
                # Load image
                loop = asyncio.get_event_loop()
                img = await loop.run_in_executor(
                    None,
                    lambda: Image.open(temp_path)
                )

                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Convert to numpy array
                img_array = np.array(img)
                return [img_array]

            finally:
                # Cleanup temporary file
                os.unlink(temp_path)

        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            raise

    async def _process_page(self, image_array: np.ndarray, page_num: int, request: OCRRequest) -> OCRPage:
        """Process a single page image"""
        try:
            # Preprocess image for better OCR
            processed_image = await self._preprocess_image(image_array)

            # Configure Tesseract
            config = self._build_tesseract_config(request)

            loop = asyncio.get_event_loop()

            # Extract text data with detailed information
            data = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_data(
                    processed_image,
                    config=config,
                    output_type=pytesseract.Output.DICT
                )
            )

            # Extract plain text for the page
            page_text = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_string(processed_image, config=config)
            )

            # Calculate page confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            page_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

            # Build paragraphs and lines if layout extraction is requested
            paragraphs = []
            tables = []

            if request.extract_layout:
                paragraphs = await self._build_paragraphs(data, image_array.shape)

            if request.extract_tables:
                tables = await self._extract_tables(processed_image, image_array.shape)

            return OCRPage(
                page_number=page_num,
                text=page_text.strip(),
                confidence=page_confidence,
                width=float(image_array.shape[1]),
                height=float(image_array.shape[0]),
                language=request.languages[0] if request.languages else "eng",
                paragraphs=paragraphs,
                tables=tables
            )

        except Exception as e:
            logger.error(f"Page processing failed: {e}")
            raise

    async def _preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Convert to grayscale
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array

            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)

            # Apply threshold to get binary image
            _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            return cleaned

        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return image_array

    def _build_tesseract_config(self, request: OCRRequest) -> str:
        """Build Tesseract configuration string"""
        config_parts = []

        # Language configuration
        if request.languages:
            lang_string = '+'.join(request.languages)
            config_parts.append(f'-l {lang_string}')

        # Page segmentation mode
        config_parts.append('--psm 1')  # Automatic page segmentation with OSD

        # OCR Engine Mode
        config_parts.append('--oem 3')  # Default, based on what is available

        # Additional options
        if request.options:
            for key, value in request.options.items():
                if key.startswith('tesseract_'):
                    config_parts.append(f'--{key[10:]} {value}')

        return ' '.join(config_parts)

    async def _build_paragraphs(self, data: Dict, image_shape: tuple) -> List[OCRParagraph]:
        """Build paragraph structure from OCR data"""
        paragraphs = []

        try:
            # Group text by blocks (paragraphs)
            current_block = None
            current_lines = []

            for i in range(len(data['text'])):
                level = data['level'][i]
                text = data['text'][i].strip()
                conf = int(data['conf'][i])

                if level == 2:  # Paragraph level
                    # Save previous paragraph
                    if current_block is not None and current_lines:
                        paragraphs.append(self._create_paragraph(current_block, current_lines, image_shape))

                    # Start new paragraph
                    current_block = i
                    current_lines = []

                elif level == 4 and text and conf > 0:  # Line level
                    line_data = {
                        'text': text,
                        'conf': conf,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    }
                    current_lines.append(line_data)

            # Save last paragraph
            if current_block is not None and current_lines:
                paragraphs.append(self._create_paragraph(current_block, current_lines, image_shape))

        except Exception as e:
            logger.error(f"Paragraph building failed: {e}")

        return paragraphs

    def _create_paragraph(self, block_idx: int, lines_data: List[Dict], image_shape: tuple) -> OCRParagraph:
        """Create paragraph from lines data"""
        # Combine all line texts
        paragraph_text = ' '.join(line['text'] for line in lines_data)

        # Calculate paragraph confidence
        confidences = [line['conf'] for line in lines_data]
        paragraph_confidence = sum(confidences) / len(confidences) / 100.0

        # Create lines
        lines = []
        for line_data in lines_data:
            bounding_box = BoundingBox(
                x=float(line_data['left']),
                y=float(line_data['top']),
                width=float(line_data['width']),
                height=float(line_data['height'])
            )

            line = OCRLine(
                text=line_data['text'],
                confidence=line_data['conf'] / 100.0,
                bounding_box=bounding_box
            )
            lines.append(line)

        # Calculate paragraph bounding box
        if lines_data:
            min_x = min(line['left'] for line in lines_data)
            min_y = min(line['top'] for line in lines_data)
            max_x = max(line['left'] + line['width'] for line in lines_data)
            max_y = max(line['top'] + line['height'] for line in lines_data)

            paragraph_bbox = BoundingBox(
                x=float(min_x),
                y=float(min_y),
                width=float(max_x - min_x),
                height=float(max_y - min_y)
            )
        else:
            paragraph_bbox = None

        return OCRParagraph(
            text=paragraph_text,
            confidence=paragraph_confidence,
            bounding_box=paragraph_bbox,
            lines=lines
        )

    async def _extract_tables(self, image: np.ndarray, image_shape: tuple) -> List[OCRTable]:
        """Extract table structures from image"""
        tables = []

        try:
            # Simple table detection using line detection
            # This is a basic implementation - for production, consider using
            # specialized table detection libraries like table-transformer

            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

            horizontal_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(image, cv2.MORPH_OPEN, vertical_kernel)

            # Find contours for table detection
            contours, _ = cv2.findContours(
                horizontal_lines + vertical_lines,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            # Filter contours that might be tables
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Minimum table size
                    x, y, w, h = cv2.boundingRect(contour)

                    # Extract table region
                    table_region = image[y:y+h, x:x+w]

                    # Simple cell extraction (placeholder)
                    # In a real implementation, you'd use more sophisticated
                    # table parsing algorithms
                    cells = [["Cell data placeholder"]]

                    table = OCRTable(
                        row_count=1,
                        column_count=1,
                        cells=cells,
                        confidence=0.5,  # Placeholder confidence
                        bounding_box=BoundingBox(
                            x=float(x),
                            y=float(y),
                            width=float(w),
                            height=float(h)
                        )
                    )
                    tables.append(table)

        except Exception as e:
            logger.error(f"Table extraction failed: {e}")

        return tables

    def _get_mime_type(self, file_ext: str) -> str:
        """Get MIME type from file extension"""
        mime_types = {
            '.pdf': 'application/pdf',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(file_ext.lower(), 'application/octet-stream')

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get OCR service capabilities"""
        return {
            "provider": "local",
            "supported_formats": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"],
            "supported_languages": ["eng", "spa", "fra", "deu", "ita", "por", "rus", "chi_sim", "jpn", "kor"],
            "features": {
                "layout_extraction": True,
                "table_extraction": True,
                "confidence_scores": True,
                "bounding_boxes": True,
                "multi_language": True
            },
            "max_file_size": self.settings.max_file_size,
            "max_pages": None  # No limit for local processing
        }