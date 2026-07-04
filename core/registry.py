"""
core/registry.py — Enrichment Registry

Dynamically loads and provides access to all registered AI Capabilities.
"""
import logging
from typing import Dict, List

from capabilities.base import Capability

logger = logging.getLogger(__name__)

class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, Capability] = {}
        
    def register(self, capability: Capability):
        if capability.name in self._capabilities:
            logger.warning(f"Overwriting existing capability: {capability.name}")
        self._capabilities[capability.name] = capability
        logger.info(f"Registered Capability: {capability.name} (v{capability.version})")
        
    def get(self, name: str) -> Capability:
        if name not in self._capabilities:
            raise KeyError(f"Capability '{name}' not found in registry.")
        return self._capabilities[name]
        
    def get_all(self) -> List[Capability]:
        return list(self._capabilities.values())
        
    def get_downstream_capabilities(self, completed_capability: str) -> List[Capability]:
        """
        Returns a list of capabilities whose dependencies are now satisfied 
        (or partially satisfied, the router will do a full check) by the completion 
        of `completed_capability`.
        """
        downstream = []
        for cap in self._capabilities.values():
            if completed_capability in cap.dependencies:
                downstream.append(cap)
        return downstream

# Global Singleton Registry
registry = CapabilityRegistry()

def init_registry():
    """Import and register all capability modules."""
    from capabilities.skill_extraction import SkillExtractionCapability
    from capabilities.classification import ClassificationCapability
    from capabilities.status_insight import StatusInsightCapability
    from capabilities.resume_parser import ResumeParserCapability
    from capabilities.learning_recommendations import LearningRecommendationsCapability
    from capabilities.tech_trends import TechTrendsCapability
    
    # We instantiate and register them here
    registry.register(SkillExtractionCapability())
    registry.register(ClassificationCapability())
    registry.register(StatusInsightCapability())
    registry.register(ResumeParserCapability())
    registry.register(LearningRecommendationsCapability())
    registry.register(TechTrendsCapability())
    
    logger.info(f"Registry initialized with {len(registry.get_all())} capabilities.")
