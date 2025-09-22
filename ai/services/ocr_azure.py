"""
Azure Document Intelligence OCR service
"""

import logging
import asyncio
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

import aiohttp
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat
from azure.core.credentials import AzureKeyCredential

from models.ocr_models import (
    OCRRequest, OCRResult, OCRPage, OCRParagraph, OCRLine, OCRTable,
    BoundingBox, DocumentInfo, ProcessingMetadata
)
from utils.config import get_settings

logger = logging.getLogger(__name__)


class AzureOCRService:
    """Azure Document Intelligence OCR service"""

    def __init__(self):
        self.settings = get_settings()
        self._client = None

    async def _get_client(self) -> DocumentIntelligenceClient:
        """Get Azure Document Intelligence client"""
        if not self._client:
            if not self.settings.azure_docintel_endpoint or not self.settings.azure_docintel_key:
                raise ValueError("Azure Document Intelligence credentials not configured")

            self._client = DocumentIntelligenceClient(
                endpoint=self.settings.azure_docintel_endpoint,
                credential=AzureKeyCredential(self.settings.azure_docintel_key)
            )

        return self._client

    async def extract_text(self, request: OCRRequest, file_content: bytes, filename: str) -> OCRResult:
        """Extract text from document using Azure Document Intelligence"""
        start_time = time.time()

        try:
            client = await self._get_client()

            # Determine model to use based on request
            model_id = "prebuilt-read"  # General OCR model
            if request.extract_tables:
                model_id = "prebuilt-layout"  # Layout model for tables

            # Prepare analyze request
            analyze_request = AnalyzeDocumentRequest(bytes_source=file_content)

            # Start analysis
            async with client:
                poller = await client.begin_analyze_document(
                    model_id=model_id,
                    analyze_request=analyze_request,
                    content_type="application/octet-stream"
                )

                # Wait for completion
                result = await poller.result()

            # Process the result
            ocr_result = await self._process_azure_result(
                result, request, filename, file_content, start_time
            )

            return ocr_result

        except Exception as e:
            logger.error(f"Azure OCR extraction failed: {e}")
            raise

    async def _process_azure_result(
        self,
        result: Any,
        request: OCRRequest,
        filename: str,
        file_content: bytes,
        start_time: float
    ) -> OCRResult:
        """Process Azure Document Intelligence result"""

        try:
            # Extract pages
            ocr_pages = []
            full_text = ""

            if hasattr(result, 'pages') and result.pages:
                for page_idx, page in enumerate(result.pages):
                    ocr_page = await self._process_azure_page(page, page_idx + 1, request)
                    ocr_pages.append(ocr_page)
                    full_text += ocr_page.text + "\n"

            # Calculate overall confidence
            if ocr_pages:
                overall_confidence = sum(page.confidence for page in ocr_pages) / len(ocr_pages)
            else:
                overall_confidence = 0.0

            # Detect language
            detected_language = "en"  # Default
            if hasattr(result, 'languages') and result.languages:
                detected_language = result.languages[0].locale

            # Create document info
            document_info = DocumentInfo(
                filename=filename,
                file_size=len(file_content),
                mime_type=self._get_mime_type(filename),
                page_count=len(ocr_pages),
                language=detected_language
            )

            # Create processing metadata
            processing_metadata = ProcessingMetadata(
                provider="azure",
                model="document-intelligence",
                processing_time=time.time() - start_time,
                parameters={
                    "model_id": "prebuilt-read" if not request.extract_tables else "prebuilt-layout",
                    "extract_layout": request.extract_layout,
                    "extract_tables": request.extract_tables,
                    "options": request.options
                }
            )

            return OCRResult(
                text=full_text.strip(),
                confidence=overall_confidence,
                pages=ocr_pages,
                language=detected_language,
                document_info=document_info,
                processing_metadata=processing_metadata
            )

        except Exception as e:
            logger.error(f"Azure result processing failed: {e}")
            raise

    async def _process_azure_page(self, page: Any, page_num: int, request: OCRRequest) -> OCRPage:
        """Process a single page from Azure result"""

        try:
            # Extract page text
            page_text = ""
            paragraphs = []
            page_confidence = 0.0

            # Process lines
            if hasattr(page, 'lines') and page.lines:
                current_paragraph_lines = []
                current_paragraph_text = ""

                for line in page.lines:
                    line_text = line.content if hasattr(line, 'content') else ""
                    line_confidence = getattr(line, 'confidence', 1.0)

                    page_text += line_text + "\n"

                    # Create OCR line
                    bounding_box = None
                    if hasattr(line, 'polygon') and line.polygon:
                        bounding_box = self._create_bounding_box_from_polygon(line.polygon)

                    ocr_line = OCRLine(
                        text=line_text,
                        confidence=line_confidence,
                        bounding_box=bounding_box
                    )

                    current_paragraph_lines.append(ocr_line)
                    current_paragraph_text += line_text + " "

                    # Group lines into paragraphs (simple heuristic)
                    if line_text.endswith('.') or len(current_paragraph_lines) >= 5:
                        if current_paragraph_lines:
                            paragraph = self._create_paragraph_from_lines(
                                current_paragraph_lines, current_paragraph_text.strip()
                            )
                            paragraphs.append(paragraph)

                        current_paragraph_lines = []
                        current_paragraph_text = ""

                # Add remaining lines as final paragraph
                if current_paragraph_lines:
                    paragraph = self._create_paragraph_from_lines(
                        current_paragraph_lines, current_paragraph_text.strip()
                    )
                    paragraphs.append(paragraph)

                # Calculate page confidence
                confidences = [line.confidence for line in page.lines if hasattr(line, 'confidence')]
                if confidences:
                    page_confidence = sum(confidences) / len(confidences)

            # Extract tables if requested
            tables = []
            if request.extract_tables and hasattr(page, 'tables'):
                for table in page.tables:
                    ocr_table = await self._process_azure_table(table)
                    tables.append(ocr_table)

            # Get page dimensions
            page_width = getattr(page, 'width', 0.0)
            page_height = getattr(page, 'height', 0.0)

            return OCRPage(
                page_number=page_num,
                text=page_text.strip(),
                confidence=page_confidence,
                width=page_width,
                height=page_height,
                paragraphs=paragraphs,
                tables=tables
            )

        except Exception as e:
            logger.error(f"Azure page processing failed: {e}")
            raise

    def _create_bounding_box_from_polygon(self, polygon: List) -> BoundingBox:
        """Create bounding box from polygon coordinates"""
        try:
            # Extract x and y coordinates
            x_coords = [point['x'] for point in polygon]
            y_coords = [point['y'] for point in polygon]

            min_x = min(x_coords)
            min_y = min(y_coords)
            max_x = max(x_coords)
            max_y = max(y_coords)

            return BoundingBox(
                x=min_x,
                y=min_y,
                width=max_x - min_x,
                height=max_y - min_y
            )

        except Exception as e:
            logger.error(f"Bounding box creation failed: {e}")
            return None

    def _create_paragraph_from_lines(self, lines: List[OCRLine], text: str) -> OCRParagraph:
        """Create paragraph from list of lines"""
        try:
            # Calculate paragraph confidence
            confidences = [line.confidence for line in lines]
            paragraph_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            # Calculate paragraph bounding box
            bounding_boxes = [line.bounding_box for line in lines if line.bounding_box]
            paragraph_bbox = None

            if bounding_boxes:
                min_x = min(bbox.x for bbox in bounding_boxes)
                min_y = min(bbox.y for bbox in bounding_boxes)
                max_x = max(bbox.x + bbox.width for bbox in bounding_boxes)
                max_y = max(bbox.y + bbox.height for bbox in bounding_boxes)

                paragraph_bbox = BoundingBox(
                    x=min_x,
                    y=min_y,
                    width=max_x - min_x,
                    height=max_y - min_y
                )

            return OCRParagraph(
                text=text,
                confidence=paragraph_confidence,
                bounding_box=paragraph_bbox,
                lines=lines
            )

        except Exception as e:
            logger.error(f"Paragraph creation failed: {e}")
            return OCRParagraph(
                text=text,
                confidence=0.0,
                bounding_box=None,
                lines=lines
            )

    async def _process_azure_table(self, table: Any) -> OCRTable:
        """Process table from Azure result"""
        try:
            # Get table dimensions
            row_count = getattr(table, 'row_count', 0)
            column_count = getattr(table, 'column_count', 0)

            # Initialize cells matrix
            cells = [['' for _ in range(column_count)] for _ in range(row_count)]

            # Fill cells
            if hasattr(table, 'cells'):
                for cell in table.cells:
                    row_index = getattr(cell, 'row_index', 0)
                    column_index = getattr(cell, 'column_index', 0)
                    content = getattr(cell, 'content', '')

                    if row_index < row_count and column_index < column_count:
                        cells[row_index][column_index] = content

            # Calculate table confidence
            table_confidence = 1.0  # Azure doesn't provide table-level confidence
            if hasattr(table, 'confidence'):
                table_confidence = table.confidence

            # Create bounding box
            bounding_box = None
            if hasattr(table, 'bounding_regions') and table.bounding_regions:
                region = table.bounding_regions[0]
                if hasattr(region, 'polygon'):
                    bounding_box = self._create_bounding_box_from_polygon(region.polygon)

            return OCRTable(
                row_count=row_count,
                column_count=column_count,
                cells=cells,
                confidence=table_confidence,
                bounding_box=bounding_box
            )

        except Exception as e:
            logger.error(f"Table processing failed: {e}")
            return OCRTable(
                row_count=0,
                column_count=0,
                cells=[],
                confidence=0.0,
                bounding_box=None
            )

    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_types = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'tiff': 'image/tiff',
            'bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'application/octet-stream')

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get Azure OCR service capabilities"""
        return {
            "provider": "azure",
            "supported_formats": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"],
            "supported_languages": [
                "en", "es", "fr", "de", "it", "pt", "ru", "zh-Hans", "ja", "ko",
                "ar", "hi", "th", "vi", "tr", "pl", "nl", "sv", "da", "no", "fi"
            ],
            "features": {
                "layout_extraction": True,
                "table_extraction": True,
                "confidence_scores": True,
                "bounding_boxes": True,
                "multi_language": True,
                "form_recognition": True,
                "key_value_pairs": True
            },
            "max_file_size": 500 * 1024 * 1024,  # 500MB for Azure
            "max_pages": 2000
        }

    async def close(self):
        """Close the Azure client"""
        if self._client:
            await self._client.close()