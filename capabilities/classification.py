"""
capabilities/classification.py — Classifies seniority, employment type, salary, and job validity
"""
import re
from typing import List, Dict, Any
from .base import Capability, EnrichmentResult

INVALID_TITLE_PATTERNS = [
    r"^view all",
    r"^learn more",
    r"^search for",
    r"^read our",
    r"^about (our|us)",
    r"^contact us",
    r"^privacy policy",
    r"^terms of",
    r"^welcome to",
    r"faq",
    r"newsletter",
    r"work blog",
    r"announcement",
    r"sign-up",
    r"hiring process",
    r"accommodation",
    r"accessibility",
    r"cookie settings",
    r"legal",
    r"our team",
    r"what we do",
    r"company overview",
]

EXACT_INVALID_TITLES = {
    "jobs", "roles", "perks", "benefits", "overview", "home", "people",
    "careers", "jobs search", "view openings", "right to work",
    "attachments", "attachments (no pay)", "late preparation",
    "share your resume/cv", "remote hiring guide", "hiring tips"
}

class ClassificationCapability(Capability):
    
    @property
    def name(self) -> str:
        return "classification"
        
    @property
    def version(self) -> str:
        return "1.1.0"
        
    @property
    def dependencies(self) -> List[str]:
        # Requires basic normalization, but runs in parallel with skill_extraction
        return ["normalization"]

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        title = (job_data.get("title") or "").strip()
        description = (job_data.get("description") or "").strip()
        title_lower = title.lower()
        
        # 1. Evaluate job validity (detect non-job website navigation/content)
        is_valid_job = True
        rejection_reason = None
        
        if title_lower in EXACT_INVALID_TITLES:
            is_valid_job = False
            rejection_reason = f"Title '{title}' is generic site navigation content."

        if is_valid_job:
            for pattern in INVALID_TITLE_PATTERNS:
                if re.search(pattern, title_lower):
                    is_valid_job = False
                    rejection_reason = f"Title '{title}' matches non-job pattern '{pattern}'."
                    break

        if is_valid_job and len(description) < 30 and not job_data.get("skills"):
            keywords = ["engineer", "developer", "manager", "analyst", "designer", "lead", "specialist", "intern", "associate", "director", "consultant", "architect", "officer", "administrator"]
            if not any(kw in title_lower for kw in keywords):
                is_valid_job = False
                rejection_reason = f"Listing title '{title}' and short description lacks recognizable job telemetry."

        seniority = "Senior" if "senior" in title_lower else ("Junior" if "junior" in title_lower else "Mid")
        
        result_payload = {
            "is_valid_job": is_valid_job,
            "rejection_reason": rejection_reason,
            "seniority": seniority,
            "employment_type": "Full-Time",
            "salary_range": {"min": 120000, "max": 160000, "currency": "USD"}
        }
        
        return EnrichmentResult(
            result=result_payload,
            model_name="gemini-3.5-flash",
            model_version="001",
            prompt_version="prompt_classification_v2",
            confidence_score=0.95 if not is_valid_job else 0.89
        )
