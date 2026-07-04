import os
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from capabilities.base import Capability, EnrichmentResult

class CourseRecommendation(BaseModel):
    title: str
    provider: str
    url: str
    description: str

class LearningRecommendationsCapability(Capability):
    @property
    def name(self) -> str:
        return "learning_recommendations"
        
    @property
    def version(self) -> str:
        return "v1.1"
        
    @property
    def dependencies(self) -> List[str]:
        return []

    def _heuristic(self, skills: List[str]) -> List[Dict[str, Any]]:
        s = " ".join([x.lower() for x in skills])
        recs = []
        if any(k in s for k in ["python", "django"]):
            recs.append({
                "title": "Django for Beginners",
                "provider": "Udemy",
                "url": "https://www.udemy.com/course/django-for-beginners/",
                "description": "Build powerful web applications with Python and Django."
            })
        if any(k in s for k in ["react", "javascript"]):
            recs.append({
                "title": "The Complete React Developer",
                "provider": "Coursera",
                "url": "https://www.coursera.org/specializations/react",
                "description": "Master React.js from scratch to advanced patterns."
            })
        if not recs:
            recs.append({
                "title": "Computer Science 101",
                "provider": "edX",
                "url": "https://www.edx.org/course/cs101-building-a-search-engine",
                "description": "A great foundation for any technical career."
            })
        return recs

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        skills = job_data.get("skills", [])

        model_name = "gemini-1.5-flash"

        try:
            agent = Agent(
                f'google-gla:{model_name}',
                system_prompt=(
                    "Suggest 3 specific online courses from Coursera, Udemy, or edX for these skills."
                ),
                result_type=List[CourseRecommendation]
            )

            result = await agent.run(f"Skills: {', '.join(skills)}")
            
            return EnrichmentResult(
                result=[c.model_dump() for c in result.data],
                model_name=model_name,
                model_version="latest",
                prompt_version=self.version
            )
        except Exception:
            return EnrichmentResult(
                result=self._heuristic(skills),
                model_name=model_name,
                model_version="error",
                prompt_version=self.version
            )
