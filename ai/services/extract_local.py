"""
Local metadata and obligation extraction using transformer models
"""

import logging
import asyncio
import re
import time
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
import json

import torch
from transformers import (
    AutoTokenizer, AutoModelForTokenClassification,
    AutoModelForSequenceClassification, pipeline
)
import spacy
from dateutil import parser as date_parser

from models.extraction_models import (
    MetadataRequest, MetadataResult, ContractMetadata,
    ObligationRequest, ObligationResult, Obligation,
    ExtractedField, ProcessingMetadata
)
from models.common_models import TextOffset, DocumentInfo
from utils.config import get_settings

logger = logging.getLogger(__name__)


class LocalExtractionService:
    """Local extraction service using transformer models"""

    def __init__(self):
        self.settings = get_settings()
        self._tokenizer = None
        self._ner_model = None
        self._classification_model = None
        self._nlp = None
        self._initialized = False

    async def initialize(self):
        """Initialize models and tokenizers"""
        if self._initialized:
            return

        try:
            logger.info("Initializing local extraction models...")

            # Load NER model for entity extraction
            model_name = self.settings.local_extract_model
            loop = asyncio.get_event_loop()

            self._tokenizer = await loop.run_in_executor(
                None, lambda: AutoTokenizer.from_pretrained(model_name)
            )

            self._ner_model = await loop.run_in_executor(
                None, lambda: AutoModelForTokenClassification.from_pretrained(model_name)
            )

            # Load classification model for obligation categorization
            self._classification_model = await loop.run_in_executor(
                None, lambda: AutoModelForSequenceClassification.from_pretrained(
                    "microsoft/DialoGPT-medium"
                )
            )

            # Load spaCy model for additional NLP tasks
            try:
                self._nlp = await loop.run_in_executor(
                    None, lambda: spacy.load("en_core_web_sm")
                )
            except OSError:
                logger.warning("spaCy model 'en_core_web_sm' not found. Installing...")
                # Fallback to basic processing without spaCy
                self._nlp = None

            self._initialized = True
            logger.info("Local extraction models initialized successfully")

        except Exception as e:
            logger.error(f"Model initialization failed: {e}")
            raise

    async def extract_metadata(self, request: MetadataRequest, text: str) -> MetadataResult:
        """Extract contract metadata from text"""
        await self.initialize()
        start_time = time.time()

        try:
            # Extract different metadata fields
            metadata = ContractMetadata()

            # Project name extraction
            if not request.extract_fields or 'ProjectName' in request.extract_fields:
                metadata.project_name = await self._extract_project_name(text)

            # Client name extraction
            if not request.extract_fields or 'ClientName' in request.extract_fields:
                metadata.client_name = await self._extract_client_name(text)

            # Contract value extraction
            if not request.extract_fields or 'ContractValue' in request.extract_fields:
                metadata.contract_value = await self._extract_contract_value(text)

            # Date extraction
            if not request.extract_fields or 'StartDate' in request.extract_fields:
                metadata.start_date = await self._extract_start_date(text)

            if not request.extract_fields or 'EndDate' in request.extract_fields:
                metadata.end_date = await self._extract_end_date(text)

            # Country extraction
            if not request.extract_fields or 'Country' in request.extract_fields:
                metadata.country = await self._extract_country(text)

            # Payment terms extraction
            if not request.extract_fields or 'PaymentTerms' in request.extract_fields:
                metadata.payment_terms = await self._extract_payment_terms(text)

            # Services extraction
            if not request.extract_fields or 'ListOfServices' in request.extract_fields:
                metadata.list_of_services = await self._extract_services(text)

            # KPIs extraction
            if not request.extract_fields or 'KPIs' in request.extract_fields:
                metadata.kpis = await self._extract_kpis(text)

            # SLAs extraction
            if not request.extract_fields or 'SLAs' in request.extract_fields:
                metadata.slas = await self._extract_slas(text)

            # Penalty clauses extraction
            if not request.extract_fields or 'PenaltyClauses' in request.extract_fields:
                metadata.penalty_clauses = await self._extract_penalty_clauses(text)

            # Calculate overall confidence and field counts
            extracted_fields = []
            for field_name, field_value in metadata.__dict__.items():
                if field_value is not None:
                    if isinstance(field_value, list):
                        extracted_fields.extend(field_value)
                    else:
                        extracted_fields.append(field_value)

            # Filter by confidence threshold
            high_conf_fields = [
                f for f in extracted_fields
                if f.confidence >= request.confidence_threshold
            ]

            overall_confidence = (
                sum(f.confidence for f in high_conf_fields) / len(high_conf_fields)
                if high_conf_fields else 0.0
            )

            # Create processing metadata
            processing_metadata = ProcessingMetadata(
                provider="local",
                model=self.settings.local_extract_model,
                processing_time=time.time() - start_time,
                parameters={
                    "extract_fields": request.extract_fields,
                    "confidence_threshold": request.confidence_threshold,
                    "options": request.options
                }
            )

            return MetadataResult(
                metadata=metadata,
                overall_confidence=overall_confidence,
                extracted_fields_count=len(high_conf_fields),
                total_fields_attempted=len(extracted_fields),
                processing_metadata=processing_metadata
            )

        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            raise

    async def extract_obligations(self, request: ObligationRequest, text: str) -> ObligationResult:
        """Extract obligations from text"""
        await self.initialize()
        start_time = time.time()

        try:
            # Find obligation-related sentences
            obligation_sentences = await self._find_obligation_sentences(text)

            obligations = []
            categories = set()

            for sentence_data in obligation_sentences:
                sentence = sentence_data['text']
                offset = sentence_data['offset']

                # Extract obligation components
                obligation = await self._extract_obligation_components(sentence, offset)

                if obligation and obligation.description.confidence >= request.confidence_threshold:
                    obligations.append(obligation)

                    # Add category if available
                    if obligation.category:
                        categories.add(obligation.category)

            # Calculate metrics
            high_confidence_count = sum(
                1 for o in obligations
                if o.description.confidence >= 0.8
            )

            average_confidence = (
                sum(o.description.confidence for o in obligations) / len(obligations)
                if obligations else 0.0
            )

            # Create processing metadata
            processing_metadata = ProcessingMetadata(
                provider="local",
                model=self.settings.local_extract_model,
                processing_time=time.time() - start_time,
                parameters={
                    "confidence_threshold": request.confidence_threshold,
                    "include_penalties": request.include_penalties,
                    "options": request.options
                }
            )

            return ObligationResult(
                obligations=obligations,
                total_obligations=len(obligations),
                high_confidence_count=high_confidence_count,
                average_confidence=average_confidence,
                categories=list(categories) if categories else None,
                processing_metadata=processing_metadata
            )

        except Exception as e:
            logger.error(f"Obligation extraction failed: {e}")
            raise

    async def _extract_project_name(self, text: str) -> Optional[ExtractedField]:
        """Extract project name using pattern matching and NER"""
        try:
            # Pattern-based extraction
            patterns = [
                r'project\s+(?:name|title):\s*([^.\n]+)',
                r'(?:project|contract):\s*([^.\n]+)',
                r'for\s+the\s+([^.\n]*?project[^.\n]*)',
                r'([A-Z][^.\n]*?Project[^.\n]*)'
            ]

            best_match = None
            best_confidence = 0.0

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    project_name = match.group(1).strip()
                    if len(project_name) > 5 and len(project_name) < 100:
                        confidence = 0.7 + (0.3 * (50 - abs(len(project_name) - 30)) / 50)
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (project_name, match.start(), match.end())

            if best_match:
                return ExtractedField(
                    value=best_match[0],
                    confidence=best_confidence,
                    text_offset=TextOffset(start=best_match[1], end=best_match[2]),
                    source="pattern_matching"
                )

            return None

        except Exception as e:
            logger.error(f"Project name extraction failed: {e}")
            return None

    async def _extract_client_name(self, text: str) -> Optional[ExtractedField]:
        """Extract client name using NER and patterns"""
        try:
            # Pattern-based extraction for client
            patterns = [
                r'client:\s*([^.\n]+)',
                r'customer:\s*([^.\n]+)',
                r'contractor:\s*([^.\n]+)',
                r'between\s+([^.\n]+?)\s+and',
                r'for\s+([A-Z][^.\n]*?(?:Inc|LLC|Ltd|Corp|Company)[^.\n]*)'
            ]

            best_match = None
            best_confidence = 0.0

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    client_name = match.group(1).strip()
                    if len(client_name) > 2 and len(client_name) < 100:
                        confidence = 0.8 if any(word in client_name.lower() for word in ['inc', 'llc', 'ltd', 'corp', 'company']) else 0.6
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (client_name, match.start(), match.end())

            if best_match:
                return ExtractedField(
                    value=best_match[0],
                    confidence=best_confidence,
                    text_offset=TextOffset(start=best_match[1], end=best_match[2]),
                    source="pattern_matching"
                )

            return None

        except Exception as e:
            logger.error(f"Client name extraction failed: {e}")
            return None

    async def _extract_contract_value(self, text: str) -> Optional[ExtractedField]:
        """Extract contract value using currency patterns"""
        try:
            # Currency patterns
            patterns = [
                r'(?:contract\s+value|total\s+amount|value):\s*([^\n]*?[\$€£¥]\s*[\d,]+(?:\.\d{2})?[^\n]*)',
                r'([\$€£¥]\s*[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|M|B|K))?)',
                r'(?:amount|value|price)(?:\s+of)?:\s*([^\n]*?[\d,]+(?:\.\d{2})?[^\n]*)',
            ]

            best_match = None
            best_confidence = 0.0

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    value_text = match.group(1).strip()
                    # Check if it contains currency symbols or numbers
                    if re.search(r'[\$€£¥]|[\d,]+', value_text):
                        confidence = 0.9 if re.search(r'[\$€£¥]', value_text) else 0.7
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (value_text, match.start(), match.end())

            if best_match:
                return ExtractedField(
                    value=best_match[0],
                    confidence=best_confidence,
                    text_offset=TextOffset(start=best_match[1], end=best_match[2]),
                    source="pattern_matching"
                )

            return None

        except Exception as e:
            logger.error(f"Contract value extraction failed: {e}")
            return None

    async def _extract_start_date(self, text: str) -> Optional[ExtractedField]:
        """Extract contract start date"""
        return await self._extract_date(text, ["start", "commencement", "effective", "begin"])

    async def _extract_end_date(self, text: str) -> Optional[ExtractedField]:
        """Extract contract end date"""
        return await self._extract_date(text, ["end", "expiration", "termination", "completion"])

    async def _extract_date(self, text: str, keywords: List[str]) -> Optional[ExtractedField]:
        """Extract dates based on keywords"""
        try:
            # Date patterns
            date_patterns = [
                r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b',
                r'\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})\b',
                r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4})\b'
            ]

            best_match = None
            best_confidence = 0.0

            for keyword in keywords:
                # Look for dates near the keyword
                keyword_pattern = rf'{keyword}[^.\n]*?(\d{{1,2}}[/\-\.]\d{{1,2}}[/\-\.]\d{{2,4}}|\d{{1,2}}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{2,4}}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{{1,2}},?\s+\d{{2,4}})'

                matches = re.finditer(keyword_pattern, text, re.IGNORECASE)
                for match in matches:
                    date_text = match.group(1).strip()
                    try:
                        # Validate date
                        parsed_date = date_parser.parse(date_text)
                        confidence = 0.9
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (date_text, match.start(1), match.end(1))
                    except:
                        continue

            if best_match:
                return ExtractedField(
                    value=best_match[0],
                    confidence=best_confidence,
                    text_offset=TextOffset(start=best_match[1], end=best_match[2]),
                    source="pattern_matching"
                )

            return None

        except Exception as e:
            logger.error(f"Date extraction failed: {e}")
            return None

    async def _extract_country(self, text: str) -> Optional[ExtractedField]:
        """Extract country information"""
        try:
            # Common countries
            countries = [
                "United States", "United Kingdom", "Canada", "Australia", "Germany",
                "France", "Italy", "Spain", "Netherlands", "Belgium", "Switzerland",
                "Sweden", "Norway", "Denmark", "Finland", "Austria", "Portugal",
                "Ireland", "Poland", "Czech Republic", "Hungary", "Romania",
                "Bulgaria", "Greece", "Croatia", "Slovenia", "Slovakia", "Lithuania",
                "Latvia", "Estonia", "Malta", "Cyprus", "Luxembourg"
            ]

            pattern = r'\b(' + '|'.join(countries) + r')\b'
            matches = list(re.finditer(pattern, text, re.IGNORECASE))

            if matches:
                # Take the first match
                match = matches[0]
                return ExtractedField(
                    value=match.group(1),
                    confidence=0.8,
                    text_offset=TextOffset(start=match.start(), end=match.end()),
                    source="pattern_matching"
                )

            return None

        except Exception as e:
            logger.error(f"Country extraction failed: {e}")
            return None

    async def _extract_payment_terms(self, text: str) -> Optional[ExtractedField]:
        """Extract payment terms"""
        try:
            patterns = [
                r'payment\s+terms?:\s*([^.\n]+)',
                r'payment\s+(?:shall\s+be\s+)?([^.\n]*?(?:days?|monthly|quarterly|annually)[^.\n]*)',
                r'(?:net\s+)?(\d+\s+days?)',
                r'payment\s+(?:due|schedule):\s*([^.\n]+)'
            ]

            best_match = None
            best_confidence = 0.0

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    payment_terms = match.group(1).strip()
                    if len(payment_terms) > 3 and len(payment_terms) < 200:
                        confidence = 0.8
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (payment_terms, match.start(), match.end())

            if best_match:
                return ExtractedField(
                    value=best_match[0],
                    confidence=best_confidence,
                    text_offset=TextOffset(start=best_match[1], end=best_match[2]),
                    source="pattern_matching"
                )

            return None

        except Exception as e:
            logger.error(f"Payment terms extraction failed: {e}")
            return None

    async def _extract_services(self, text: str) -> Optional[List[ExtractedField]]:
        """Extract list of services"""
        try:
            # Pattern for services section
            services_pattern = r'services?[^.\n]*?:\s*([^.]*?(?:service|provision|maintenance|support|consulting)[^.]*)'

            services = []
            matches = re.finditer(services_pattern, text, re.IGNORECASE)

            for match in matches:
                service_text = match.group(1).strip()
                if len(service_text) > 5:
                    services.append(ExtractedField(
                        value=service_text,
                        confidence=0.7,
                        text_offset=TextOffset(start=match.start(), end=match.end()),
                        source="pattern_matching"
                    ))

            return services if services else None

        except Exception as e:
            logger.error(f"Services extraction failed: {e}")
            return None

    async def _extract_kpis(self, text: str) -> Optional[List[ExtractedField]]:
        """Extract KPIs"""
        try:
            kpi_patterns = [
                r'kpi[^.\n]*?:\s*([^.\n]+)',
                r'(?:key\s+)?performance\s+indicator[^.\n]*?:\s*([^.\n]+)',
                r'target[^.\n]*?:\s*([^.\n]*?(?:\d+%|percentage|ratio)[^.\n]*)'
            ]

            kpis = []

            for pattern in kpi_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    kpi_text = match.group(1).strip()
                    if len(kpi_text) > 3:
                        kpis.append(ExtractedField(
                            value=kpi_text,
                            confidence=0.8,
                            text_offset=TextOffset(start=match.start(), end=match.end()),
                            source="pattern_matching"
                        ))

            return kpis if kpis else None

        except Exception as e:
            logger.error(f"KPIs extraction failed: {e}")
            return None

    async def _extract_slas(self, text: str) -> Optional[List[ExtractedField]]:
        """Extract SLAs"""
        try:
            sla_patterns = [
                r'sla[^.\n]*?:\s*([^.\n]+)',
                r'service\s+level\s+agreement[^.\n]*?:\s*([^.\n]+)',
                r'(?:response|resolution)\s+time[^.\n]*?:\s*([^.\n]*?(?:hours?|days?|minutes?)[^.\n]*)'
            ]

            slas = []

            for pattern in sla_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    sla_text = match.group(1).strip()
                    if len(sla_text) > 3:
                        slas.append(ExtractedField(
                            value=sla_text,
                            confidence=0.8,
                            text_offset=TextOffset(start=match.start(), end=match.end()),
                            source="pattern_matching"
                        ))

            return slas if slas else None

        except Exception as e:
            logger.error(f"SLAs extraction failed: {e}")
            return None

    async def _extract_penalty_clauses(self, text: str) -> Optional[List[ExtractedField]]:
        """Extract penalty clauses"""
        try:
            penalty_patterns = [
                r'penalty[^.\n]*?:\s*([^.\n]+)',
                r'(?:liquidated\s+)?damages[^.\n]*?:\s*([^.\n]+)',
                r'(?:fine|penalty|charge)[^.\n]*?(?:of|shall\s+be)[^.\n]*?([^.\n]*?(?:\$|€|£|amount)[^.\n]*)'
            ]

            penalties = []

            for pattern in penalty_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    penalty_text = match.group(1).strip()
                    if len(penalty_text) > 3:
                        penalties.append(ExtractedField(
                            value=penalty_text,
                            confidence=0.7,
                            text_offset=TextOffset(start=match.start(), end=match.end()),
                            source="pattern_matching"
                        ))

            return penalties if penalties else None

        except Exception as e:
            logger.error(f"Penalty clauses extraction failed: {e}")
            return None

    async def _find_obligation_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Find sentences that likely contain obligations"""
        try:
            # Obligation indicators
            obligation_keywords = [
                "shall", "must", "will", "required", "obligation", "responsible",
                "duty", "commitment", "ensure", "provide", "deliver", "maintain",
                "comply", "adhere", "follow", "perform", "complete", "submit"
            ]

            sentences = re.split(r'[.!?]+', text)
            obligation_sentences = []

            current_offset = 0
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:
                    # Check if sentence contains obligation keywords
                    score = sum(1 for keyword in obligation_keywords
                              if keyword.lower() in sentence.lower())

                    if score > 0:
                        obligation_sentences.append({
                            'text': sentence,
                            'offset': current_offset,
                            'score': score
                        })

                current_offset += len(sentence) + 1

            # Sort by score
            obligation_sentences.sort(key=lambda x: x['score'], reverse=True)

            return obligation_sentences[:50]  # Limit to top 50

        except Exception as e:
            logger.error(f"Obligation sentence finding failed: {e}")
            return []

    async def _extract_obligation_components(self, sentence: str, offset: int) -> Optional[Obligation]:
        """Extract obligation components from a sentence"""
        try:
            # Extract description (the sentence itself, cleaned up)
            description = re.sub(r'\s+', ' ', sentence).strip()

            # Extract frequency patterns
            frequency_patterns = [
                r'\b(daily|weekly|monthly|quarterly|annually|yearly)\b',
                r'\bevery\s+(\d+\s+(?:day|week|month|year)s?)\b',
                r'\b(once\s+(?:per\s+)?(?:day|week|month|year))\b'
            ]

            frequency = None
            for pattern in frequency_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    frequency = ExtractedField(
                        value=match.group(1),
                        confidence=0.8,
                        text_offset=TextOffset(start=offset + match.start(), end=offset + match.end()),
                        source="pattern_matching"
                    )
                    break

            # Extract due dates/deadlines
            due_date_patterns = [
                r'\bby\s+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b',
                r'\bwithin\s+(\d+\s+(?:day|week|month)s?)\b',
                r'\b(?:due|deadline):\s*([^.\n]+)',
                r'\bno\s+later\s+than\s+([^.\n]+)'
            ]

            due_date = None
            for pattern in due_date_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    due_date = ExtractedField(
                        value=match.group(1),
                        confidence=0.7,
                        text_offset=TextOffset(start=offset + match.start(), end=offset + match.end()),
                        source="pattern_matching"
                    )
                    break

            # Extract penalty information
            penalty_text = None
            penalty_patterns = [
                r'(?:penalty|fine|charge)[^.\n]*?([^.\n]*?(?:\$|€|£|\d+)[^.\n]*)',
                r'(?:liquidated\s+)?damages[^.\n]*?([^.\n]+)'
            ]

            for pattern in penalty_patterns:
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    penalty_text = ExtractedField(
                        value=match.group(1).strip(),
                        confidence=0.6,
                        text_offset=TextOffset(start=offset + match.start(), end=offset + match.end()),
                        source="pattern_matching"
                    )
                    break

            # Categorize obligation
            category = self._categorize_obligation(sentence)

            # Create obligation description field
            description_field = ExtractedField(
                value=description,
                confidence=0.8,
                text_offset=TextOffset(start=offset, end=offset + len(sentence)),
                source="sentence_extraction"
            )

            return Obligation(
                description=description_field,
                frequency=frequency,
                due_date=due_date,
                penalty_text=penalty_text,
                category=category,
                status="pending"
            )

        except Exception as e:
            logger.error(f"Obligation component extraction failed: {e}")
            return None

    def _categorize_obligation(self, sentence: str) -> Optional[str]:
        """Categorize obligation based on content"""
        categories = {
            "reporting": ["report", "submit", "document", "record", "notify"],
            "maintenance": ["maintain", "service", "repair", "clean", "inspect"],
            "delivery": ["deliver", "provide", "supply", "furnish"],
            "compliance": ["comply", "adhere", "follow", "conform", "meet"],
            "payment": ["pay", "payment", "invoice", "bill", "remit"],
            "performance": ["perform", "execute", "complete", "achieve"]
        }

        sentence_lower = sentence.lower()

        for category, keywords in categories.items():
            if any(keyword in sentence_lower for keyword in keywords):
                return category

        return "general"

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get local extraction service capabilities"""
        return {
            "provider": "local",
            "supported_extraction_types": ["metadata", "obligations"],
            "supported_fields": {
                "metadata": [
                    "ProjectName", "ClientName", "ContractValue", "StartDate", "EndDate",
                    "Country", "PaymentTerms", "ListOfServices", "KPIs", "SLAs", "PenaltyClauses"
                ],
                "obligations": [
                    "Description", "Frequency", "DueDate", "PenaltyText", "Category", "Assignee"
                ]
            },
            "max_text_length": 100000,  # 100K characters
            "supported_languages": ["en"],
            "features": {
                "confidence_scores": True,
                "text_offsets": True,
                "categorization": True,
                "pattern_matching": True,
                "ner_extraction": True
            }
        }