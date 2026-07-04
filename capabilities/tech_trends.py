from typing import Any, Dict, List
from pydantic_ai import Agent
from capabilities.base import Capability, EnrichmentResult

class TechTrendsCapability(Capability):
    @property
    def name(self) -> str:
        return "tech_trends_commentary"
        
    @property
    def version(self) -> str:
        return "v1.0"
        
    @property
    def dependencies(self) -> List[str]:
        return []

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        trends = job_data.get("trends", [])
        news = job_data.get("news", [])

        model_name = "gemini-1.5-flash"
        
        try:
            agent = Agent(
                f'google-gla:{model_name}',
                system_prompt=(
                    "Write a short, punchy 'What's Hot' summary (2-3 sentences) about what developers are talking about RIGHT NOW. "
                    "Mention social sentiment and emerging technologies."
                )
            )

            prompt = (
                f"Analyze these current tech trends: {', '.join(trends)}.\n"
                f"Based on these recent headlines: {'; '.join(news)}."
            )

            result = await agent.run(prompt)

            return EnrichmentResult(
                result={"commentary": result.data},
                model_name=model_name,
                model_version="latest",
                prompt_version=self.version
            )
        except Exception as e:
            return EnrichmentResult(
                result={"commentary": f"The community is buzzing about {', '.join(trends[:3])}."},
                model_name=model_name,
                model_version="error",
                prompt_version=self.version
            )
