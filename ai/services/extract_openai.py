"""
OpenAI/Azure OpenAI extraction service for metadata and obligations
"""

import logging
import asyncio
import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

import openai
from openai import AsyncOpenAI, AsyncAzureOpenAI

from models.extraction_models import (
    MetadataRequest, MetadataResult, ContractMetadata,
    ObligationRequest, ObligationResult, Obligation,
    ExtractedField, ProcessingMetadata
)
from models.common_models import TextOffset, DocumentInfo
from utils.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIExtractionService:
    """OpenAI/Azure OpenAI extraction service"""

    def __init__(self):
        self.settings = get_settings()
        self._client = None

    async def _get_client(self):
        """Get OpenAI client (Azure or regular OpenAI)"""
        if self._client:
            return self._client

        # Prefer Azure OpenAI if configured
        if self.settings.azure_openai_api_key and self.settings.azure_openai_endpoint:
            self._client = AsyncAzureOpenAI(
                api_key=self.settings.azure_openai_api_key,
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=self.settings.azure_openai_endpoint
            )
            logger.info("Using Azure OpenAI client")

        elif self.settings.openai_api_key:
            self._client = AsyncOpenAI(
                api_key=self.settings.openai_api_key
            )
            logger.info("Using OpenAI client")

        else:
            raise ValueError("No OpenAI API credentials configured")

        return self._client

    async def extract_metadata(self, request: MetadataRequest, text: str) -> MetadataResult:
        """Extract contract metadata using OpenAI"""
        start_time = time.time()

        try:
            client = await self._get_client()

            # Create extraction prompt
            prompt = self._create_metadata_prompt(text, request)

            # Get model name
            model = (self.settings.azure_openai_deployment_name
                    if hasattr(self.settings, 'azure_openai_deployment_name')
                    else self.settings.openai_model)

            # Call OpenAI API
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting structured information from legal contracts. Extract the requested metadata and return it as valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )

            # Parse response
            result_text = response.choices[0].message.content
            metadata_dict = await self._parse_metadata_response(result_text, text)

            # Create metadata object
            metadata = ContractMetadata(**metadata_dict)

            # Calculate metrics
            extracted_fields = []
            for field_name, field_value in metadata.__dict__.items():
                if field_value is not None:
                    if isinstance(field_value, list):
                        extracted_fields.extend(field_value)
                    else:
                        extracted_fields.append(field_value)

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
                provider="openai",
                model=model,
                processing_time=time.time() - start_time,
                parameters={
                    "extract_fields": request.extract_fields,
                    "confidence_threshold": request.confidence_threshold,
                    "temperature": 0.1,
                    "max_tokens": 2000
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
            logger.error(f"OpenAI metadata extraction failed: {e}")
            raise

    async def extract_obligations(self, request: ObligationRequest, text: str) -> ObligationResult:
        """Extract obligations using OpenAI"""
        start_time = time.time()

        try:
            client = await self._get_client()

            # Create extraction prompt
            prompt = self._create_obligations_prompt(text, request)

            # Get model name
            model = (self.settings.azure_openai_deployment_name
                    if hasattr(self.settings, 'azure_openai_deployment_name')
                    else self.settings.openai_model)

            # Call OpenAI API
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying and extracting contractual obligations from legal documents. Extract all obligations with their details and return as valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=3000
            )

            # Parse response
            result_text = response.choices[0].message.content
            obligations_list = await self._parse_obligations_response(result_text, text)

            # Filter by confidence threshold
            filtered_obligations = [
                o for o in obligations_list
                if o.description.confidence >= request.confidence_threshold
            ]

            # Calculate metrics
            high_confidence_count = sum(
                1 for o in filtered_obligations
                if o.description.confidence >= 0.8
            )

            average_confidence = (
                sum(o.description.confidence for o in filtered_obligations) / len(filtered_obligations)
                if filtered_obligations else 0.0
            )

            # Get categories
            categories = list(set(o.category for o in filtered_obligations if o.category))

            # Create processing metadata
            processing_metadata = ProcessingMetadata(
                provider="openai",
                model=model,
                processing_time=time.time() - start_time,
                parameters={
                    "confidence_threshold": request.confidence_threshold,
                    "include_penalties": request.include_penalties,
                    "temperature": 0.1,
                    "max_tokens": 3000
                }
            )

            return ObligationResult(
                obligations=filtered_obligations,
                total_obligations=len(filtered_obligations),
                high_confidence_count=high_confidence_count,
                average_confidence=average_confidence,
                categories=categories if categories else None,
                processing_metadata=processing_metadata
            )

        except Exception as e:
            logger.error(f"OpenAI obligation extraction failed: {e}")
            raise

    def _create_metadata_prompt(self, text: str, request: MetadataRequest) -> str:
        """Create metadata extraction prompt"""

        # Truncate text if too long
        if len(text) > 10000:
            text = text[:10000] + "..."

        fields_to_extract = request.extract_fields or [
            "ProjectName", "ClientName", "ContractValue", "StartDate", "EndDate",
            "Country", "PaymentTerms", "ListOfServices", "KPIs", "SLAs", "PenaltyClauses"
        ]

        prompt = f"""
Extract the following contract metadata from the provided text. Return the results as a JSON object with the specified structure.

Fields to extract: {', '.join(fields_to_extract)}

For each field, provide:
1. The extracted value
2. A confidence score (0.0 to 1.0)
3. The approximate text location where it was found

Expected JSON structure:
{{
  "project_name": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "client_name": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "contract_value": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "start_date": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "end_date": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "country": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "payment_terms": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
  "list_of_services": [{{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}}],
  "kpis": [{{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}}],
  "slas": [{{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}}],
  "penalty_clauses": [{{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}}]
}}

If a field is not found or cannot be determined with reasonable confidence, set it to null.

Contract text:
{text}
"""
        return prompt

    def _create_obligations_prompt(self, text: str, request: ObligationRequest) -> str:
        """Create obligations extraction prompt"""

        # Truncate text if too long
        if len(text) > 12000:
            text = text[:12000] + "..."

        penalty_instruction = (
            "Include penalty information if available."
            if request.include_penalties
            else "Do not extract penalty information."
        )

        prompt = f"""
Extract all contractual obligations from the provided text. An obligation is a duty, requirement, or commitment that one or more parties must fulfill.

{penalty_instruction}

For each obligation, provide:
1. Description: Clear description of what must be done
2. Frequency: How often it must be done (if specified)
3. Due date or deadline (if specified)
4. Penalty information (if applicable and requested)
5. Category: Type of obligation (reporting, maintenance, delivery, compliance, payment, performance, etc.)
6. Confidence score (0.0 to 1.0)

Return results as a JSON array:
[
  {{
    "description": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}},
    "frequency": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}} or null,
    "due_date": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}} or null,
    "penalty_text": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}} or null,
    "category": "string",
    "assignee": {{"value": "string", "confidence": 0.0-1.0, "source_text": "relevant excerpt"}} or null
  }}
]

Look for obligations indicated by words like: shall, must, will, required, responsible, duty, ensure, provide, deliver, maintain, comply, etc.

Contract text:
{text}
"""
        return prompt

    async def _parse_metadata_response(self, response_text: str, original_text: str) -> Dict[str, Any]:
        """Parse metadata extraction response"""
        try:
            # Clean up response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Parse JSON
            parsed = json.loads(response_text)

            # Convert to ExtractedField objects
            result = {}

            for field_name, field_data in parsed.items():
                if field_data is None:
                    result[field_name] = None
                    continue

                if isinstance(field_data, list):
                    # Handle list fields (services, KPIs, etc.)
                    extracted_list = []
                    for item in field_data:
                        if isinstance(item, dict) and 'value' in item:
                            text_offset = self._find_text_offset(
                                item.get('source_text', ''), original_text
                            )
                            extracted_list.append(ExtractedField(
                                value=item['value'],
                                confidence=item.get('confidence', 0.8),
                                text_offset=text_offset,
                                source="openai"
                            ))
                    result[field_name] = extracted_list if extracted_list else None

                elif isinstance(field_data, dict) and 'value' in field_data:
                    # Handle single field
                    text_offset = self._find_text_offset(
                        field_data.get('source_text', ''), original_text
                    )
                    result[field_name] = ExtractedField(
                        value=field_data['value'],
                        confidence=field_data.get('confidence', 0.8),
                        text_offset=text_offset,
                        source="openai"
                    )
                else:
                    result[field_name] = None

            return result

        except Exception as e:
            logger.error(f"Metadata response parsing failed: {e}")
            # Return empty result
            return {
                "project_name": None,
                "client_name": None,
                "contract_value": None,
                "start_date": None,
                "end_date": None,
                "country": None,
                "payment_terms": None,
                "list_of_services": None,
                "kpis": None,
                "slas": None,
                "penalty_clauses": None
            }

    async def _parse_obligations_response(self, response_text: str, original_text: str) -> List[Obligation]:
        """Parse obligations extraction response"""
        try:
            # Clean up response text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Parse JSON
            parsed = json.loads(response_text)

            obligations = []

            for item in parsed:
                if not isinstance(item, dict) or 'description' not in item:
                    continue

                # Extract description
                desc_data = item['description']
                if not isinstance(desc_data, dict) or 'value' not in desc_data:
                    continue

                desc_offset = self._find_text_offset(
                    desc_data.get('source_text', ''), original_text
                )
                description = ExtractedField(
                    value=desc_data['value'],
                    confidence=desc_data.get('confidence', 0.8),
                    text_offset=desc_offset,
                    source="openai"
                )

                # Extract optional fields
                frequency = None
                if item.get('frequency') and isinstance(item['frequency'], dict):
                    freq_data = item['frequency']
                    freq_offset = self._find_text_offset(
                        freq_data.get('source_text', ''), original_text
                    )
                    frequency = ExtractedField(
                        value=freq_data['value'],
                        confidence=freq_data.get('confidence', 0.8),
                        text_offset=freq_offset,
                        source="openai"
                    )

                due_date = None
                if item.get('due_date') and isinstance(item['due_date'], dict):
                    due_data = item['due_date']
                    due_offset = self._find_text_offset(
                        due_data.get('source_text', ''), original_text
                    )
                    due_date = ExtractedField(
                        value=due_data['value'],
                        confidence=due_data.get('confidence', 0.8),
                        text_offset=due_offset,
                        source="openai"
                    )

                penalty_text = None
                if item.get('penalty_text') and isinstance(item['penalty_text'], dict):
                    penalty_data = item['penalty_text']
                    penalty_offset = self._find_text_offset(
                        penalty_data.get('source_text', ''), original_text
                    )
                    penalty_text = ExtractedField(
                        value=penalty_data['value'],
                        confidence=penalty_data.get('confidence', 0.8),
                        text_offset=penalty_offset,
                        source="openai"
                    )

                assignee = None
                if item.get('assignee') and isinstance(item['assignee'], dict):
                    assignee_data = item['assignee']
                    assignee_offset = self._find_text_offset(
                        assignee_data.get('source_text', ''), original_text
                    )
                    assignee = ExtractedField(
                        value=assignee_data['value'],
                        confidence=assignee_data.get('confidence', 0.8),
                        text_offset=assignee_offset,
                        source="openai"
                    )

                obligation = Obligation(
                    description=description,
                    frequency=frequency,
                    due_date=due_date,
                    penalty_text=penalty_text,
                    category=item.get('category', 'general'),
                    assignee=assignee,
                    status="pending"
                )

                obligations.append(obligation)

            return obligations

        except Exception as e:
            logger.error(f"Obligations response parsing failed: {e}")
            return []

    def _find_text_offset(self, source_text: str, original_text: str) -> Optional[TextOffset]:
        """Find text offset in original document"""
        if not source_text or not original_text:
            return None

        try:
            # Clean and normalize text for matching
            source_clean = source_text.strip()[:50]  # Use first 50 chars for matching

            # Find approximate position
            start_pos = original_text.find(source_clean)
            if start_pos == -1:
                # Try case-insensitive search
                start_pos = original_text.lower().find(source_clean.lower())

            if start_pos != -1:
                return TextOffset(
                    start=start_pos,
                    end=start_pos + len(source_clean)
                )

            return None

        except Exception as e:
            logger.error(f"Text offset finding failed: {e}")
            return None

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get OpenAI extraction service capabilities"""
        model = (self.settings.azure_openai_deployment_name
                if hasattr(self.settings, 'azure_openai_deployment_name')
                else self.settings.openai_model)

        return {
            "provider": "openai",
            "model": model,
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
            "max_text_length": 15000,  # Accounting for prompt overhead
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko"],
            "features": {
                "confidence_scores": True,
                "text_offsets": True,
                "categorization": True,
                "natural_language_understanding": True,
                "context_awareness": True,
                "multi_language": True
            }
        }

    async def close(self):
        """Close the OpenAI client"""
        if self._client:
            await self._client.close()