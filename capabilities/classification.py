"""
capabilities/classification.py — Classifies seniority, employment type, and salary
"""
from typing import List, Dict, Any
from .base import Capability, EnrichmentResult

class ClassificationCapability(Capability):
    
    @property
    def name(self) -> str:
        return "classification"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def dependencies(self) -> List[str]:
        # Requires basic normalization, but runs in parallel with skill_extraction
        return ["normalization"]

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        description = job_data.get("description", "")
        
        # TODO: Call LLM to extract structured classification
        result_payload = {
            "seniority": "Senior",
            "employment_type": "Full-Time",
            "salary_range": {"min": 120000, "max": 160000, "currency": "USD"}
        }
        
        return EnrichmentResult(
            result=result_payload,
            model_name="gemini-1.5-pro",
            model_version="001",
            prompt_version="prompt_classification_v1",
            confidence_score=0.89
        )
