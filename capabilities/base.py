"""
capabilities/base.py — Abstract Capability Engine

Defines the contract for all AI Enrichment capabilities.
Capabilities are stateless, isolated, and versioned.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class EnrichmentResult(BaseModel):
    result: Any
    model_name: str
    model_version: str
    prompt_version: str
    confidence_score: Optional[float] = None


class Capability(ABC):
    """
    Abstract base class for all AI Enrichment capabilities.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The canonical name of the capability (e.g., 'skill_extraction')."""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """The current version of this capability logic (e.g., 'v1.0')."""
        pass
        
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """List of capability names that must be COMPLETED before this can run."""
        pass

    @abstractmethod
    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        """
        Executes the AI logic. 
        Must be completely stateless and idempotent.
        
        :param job_data: The raw or partially enriched job payload
        :return: An EnrichmentResult containing the versioned output
        """
        pass
