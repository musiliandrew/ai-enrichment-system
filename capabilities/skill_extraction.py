"""
capabilities/skill_extraction.py — Extracts skills from raw job text
"""
from typing import List, Dict, Any
from .base import Capability, EnrichmentResult

class SkillExtractionCapability(Capability):
    
    @property
    def name(self) -> str:
        return "skill_extraction"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def dependencies(self) -> List[str]:
        # Typically relies on 'normalization' being done first
        return ["normalization"]

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        description = job_data.get("description", "")
        
        # TODO: Implement actual LLM call (e.g., Gemini / Langchain) here
        # Mocked result for architecture demonstration
        extracted_skills = ["Python", "Machine Learning", "FastAPI"]
        
        return EnrichmentResult(
            result={"skills": extracted_skills},
            model_name="gemini-1.5-pro",
            model_version="001",
            prompt_version="prompt_v2",
            confidence_score=0.95
        )
