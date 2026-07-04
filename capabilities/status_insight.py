import os
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from capabilities.base import Capability, EnrichmentResult

# Define the output structure
class StatusUpdateInsight(BaseModel):
    insight: str = Field(description="A concise, encouraging, and actionable insight about the status change.")
    action_items: List[str] = Field(description="List of 1-3 specific next steps for the user.")
    suggested_skill_to_learn: str = Field(description="If the rejection implies a specific technical skill is missing, output exactly that skill name here (e.g. 'Next.js'). Otherwise, leave empty.", default="")

class StatusInsightCapability(Capability):
    @property
    def name(self) -> str:
        return "status_insight"
        
    @property
    def version(self) -> str:
        return "v1.1"
        
    @property
    def dependencies(self) -> List[str]:
        return []

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        """
        Generates an AI insight for a job application status change.
        """
        company = job_data.get("company", "Unknown")
        role = job_data.get("role", "Unknown")
        old_status = job_data.get("old_status", "")
        new_status = job_data.get("new_status", "")
        notes = job_data.get("notes", "")
        tech_skills = job_data.get("tech_skills", [])
        learning_skills = job_data.get("learning_skills", [])
        recent_rejections = job_data.get("recent_rejections", 0)

        model_name = "gemini-1.5-flash"
        
        try:
            agent = Agent(
                f'google-gla:{model_name}',
                system_prompt=(
                    "You are an elite, highly strategic career coach acting as an AI Agent for a tech professional. The user just changed a job application's status. "
                    "Your goal is to provide a highly personalized, agentic insight correlating their current skills, what they want to learn, and their recent application track record.\n"
                    "If they were rejected and have a high rejection count, analyze their missing skills and suggest a pivot or specific learning goal. "
                    "If they moved to an interview, tell them which of their current skills to highlight.\n"
                    "Do not use generic cheerleading. Be concise, direct, and actionable."
                ),
                result_type=StatusUpdateInsight
            )

            prompt = (
                f"Company: {company}\nRole: {role}\nOld Status: {old_status}\nNew Status: {new_status}\nUser Notes: {notes}\n"
                f"User's Technical Skills: {', '.join(tech_skills) if tech_skills else 'None'}\n"
                f"User's Learning Goals: {', '.join(learning_skills) if learning_skills else 'None'}\n"
                f"User's Recent Rejections (last 14 days): {recent_rejections}"
            )

            result = await agent.run(prompt)

            return EnrichmentResult(
                result=result.data.model_dump(),
                model_name=model_name,
                model_version="latest",
                prompt_version=self.version
            )

        except Exception as e:
            print(f"Error generating AI insight: {e}")
            return EnrichmentResult(
                result={
                    "insight": f"Status updated to {new_status}. Good luck!",
                    "action_items": [],
                    "suggested_skill_to_learn": ""
                },
                model_name=model_name,
                model_version="error",
                prompt_version=self.version
            )
