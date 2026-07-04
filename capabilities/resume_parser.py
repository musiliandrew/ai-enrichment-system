import os
import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from capabilities.base import Capability, EnrichmentResult

# Define schema for the resume extraction (matches backend/agents/models.py Profile)
class ExtractedSkill(BaseModel):
    name: str = Field(description="Name of the skill")
    proficiency: int = Field(description="Skill proficiency from 1 to 5", default=3)
    category: str = Field(description="Category of the skill (e.g., Languages, Frameworks, Tools)")

class ExtractedEducation(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: str
    description: str

class ExtractedWorkExperience(BaseModel):
    company: str
    position: str
    start_date: str
    end_date: str
    description: str

class ExtractedProject(BaseModel):
    name: str
    description: str
    technologies_used: List[str]
    link: str

class ExtractedProfile(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    github_url: str
    linkedin_url: str
    portfolio_url: str
    summary: str
    skills: List[ExtractedSkill]
    education: List[ExtractedEducation]
    experience: List[ExtractedWorkExperience]
    projects: List[ExtractedProject]

class ResumeParserCapability(Capability):
    @property
    def name(self) -> str:
        return "resume_parser"
        
    @property
    def version(self) -> str:
        return "v1.1"
        
    @property
    def dependencies(self) -> List[str]:
        return []

    async def execute(self, job_data: Dict[str, Any]) -> EnrichmentResult:
        markdown_text = job_data.get("markdown", "")

        model_name = "gemini-1.5-pro"

        agent = Agent(
            f'google-gla:{model_name}',
            system_prompt=(
                "You are an expert ATS (Applicant Tracking System). Extract all relevant information from the provided resume text into a highly structured JSON format."
            ),
            result_type=ExtractedProfile
        )

        result = await agent.run(f"Resume Text:\n{markdown_text}")

        return EnrichmentResult(
            result=result.data.model_dump(),
            model_name=model_name,
            model_version="latest",
            prompt_version=self.version
        )
