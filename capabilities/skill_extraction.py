from typing import List, Dict, Any
from pydantic_ai import Agent
from pydantic import BaseModel, Field
from .base import Capability, EnrichmentResult

class ExtractedSkills(BaseModel):
    skills: List[str] = Field(..., description="List of technical skills, programming languages, libraries, frameworks, or tools extracted from the job description.")

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
        title = job_data.get("title", "")
        
        model_name = "gemini-2.0-flash"
        
        try:
            agent = Agent(
                f'google:{model_name}',
                output_type=ExtractedSkills,
                system_prompt=(
                    "You are an expert technical recruiter and talent analyst. "
                    "Analyze the job title and description to extract a clean list of required "
                    "or nice-to-have technical skills, tools, programming languages, libraries, databases, "
                    "cloud services, and architectures. Keep names standardized (e.g. 'Python', 'React', 'FastAPI', 'PostgreSQL')."
                )
            )
            
            prompt = f"Job Title: {title}\nJob Description:\n{description}"
            result = await agent.run(prompt)
            
            # AgentRunResult response has a response attribute containing the output or directly has the data depending on run
            if hasattr(result, "data") and hasattr(result.data, "skills"):
                extracted_skills = result.data.skills
            elif hasattr(result.response, "data") and hasattr(result.response.data, "skills"):
                extracted_skills = result.response.data.skills
            else:
                raise ValueError("Could not extract skills from agent response")
            
            return EnrichmentResult(
                result={"skills": extracted_skills},
                model_name=model_name,
                model_version="latest",
                prompt_version=self.version,
                confidence_score=0.95
            )
        except Exception as e:
            # Fallback heuristics if API call fails or user lacks credits
            import re
            
            SKILLS_MAP = {
                # Programming Languages
                "python": "Python",
                "javascript": "JavaScript",
                "typescript": "TypeScript",
                "java": "Java",
                "c++": "C++",
                "c#": "C#",
                "ruby": "Ruby",
                "php": "PHP",
                "swift": "Swift",
                "go": "Go",
                "golang": "Go",
                "rust": "Rust",
                "kotlin": "Kotlin",
                "scala": "Scala",
                "html": "HTML",
                "css": "CSS",
                "sass": "Sass",
                
                # Frameworks & Libraries
                "django": "Django",
                "fastapi": "FastAPI",
                "flask": "Flask",
                "react": "React",
                "angular": "Angular",
                "vue": "Vue",
                "next.js": "Next.js",
                "nextjs": "Next.js",
                "svelte": "Svelte",
                "express": "Express",
                "spring boot": "Spring Boot",
                "laravel": "Laravel",
                "rails": "Ruby on Rails",
                "tensorflow": "TensorFlow",
                "pytorch": "PyTorch",
                "keras": "Keras",
                "scikit-learn": "Scikit-Learn",
                "numpy": "NumPy",
                "pandas": "Pandas",
                
                # Databases & Data Stores
                "postgresql": "PostgreSQL",
                "postgres": "PostgreSQL",
                "mysql": "MySQL",
                "sqlite": "SQLite",
                "mongodb": "MongoDB",
                "redis": "Redis",
                "elasticsearch": "Elasticsearch",
                "cassandra": "Cassandra",
                "mariadb": "MariaDB",
                "dynamodb": "DynamoDB",
                "oracle": "Oracle",
                
                # Cloud & Infrastructure / DevOps
                "aws": "AWS",
                "amazon web services": "AWS",
                "gcp": "GCP",
                "google cloud": "GCP",
                "azure": "Azure",
                "docker": "Docker",
                "kubernetes": "Kubernetes",
                "k8s": "Kubernetes",
                "terraform": "Terraform",
                "ansible": "Ansible",
                "jenkins": "Jenkins",
                "github actions": "GitHub Actions",
                "ci/cd": "CI/CD",
                "nginx": "Nginx",
                "apache": "Apache",
                "linux": "Linux",
                "bash": "Bash",
                
                # Big Data & AI
                "spark": "Apache Spark",
                "hadoop": "Hadoop",
                "kafka": "Apache Kafka",
                "airflow": "Apache Airflow",
                "dbt": "dbt",
                "snowflake": "Snowflake",
                "tableau": "Tableau",
                "powerbi": "PowerBI",
                "machine learning": "Machine Learning",
                "deep learning": "Deep Learning",
                "nlp": "NLP",
                "llm": "LLM",
                "generative ai": "Generative AI",
                "genai": "Generative AI",
                "artificial intelligence": "AI",
                "data science": "Data Science",
                "data engineering": "Data Engineering",
                
                # Tools & Architecture
                "git": "Git",
                "graphql": "GraphQL",
                "rest api": "REST API",
                "microservices": "Microservices",
                "agile": "Agile",
                "scrum": "Scrum",
                "testing": "Testing",
                "jest": "Jest",
                "selenium": "Selenium",
                "cypress": "Cypress",
                "figma": "Figma",
                "ui/ux": "UI/UX",
                "product management": "Product Management",
                "project management": "Project Management"
            }
            
            fallback_skills = []
            desc_lower = (title + " " + description).lower()
            for key, val in SKILLS_MAP.items():
                escaped = re.escape(key)
                if re.search(r'\b' + escaped + r'\b', desc_lower):
                    if val not in fallback_skills:
                        fallback_skills.append(val)
            
            if not fallback_skills:
                # Add basic role inference
                if "frontend" in desc_lower or "react" in desc_lower:
                    fallback_skills = ["Frontend Development", "React", "JavaScript"]
                elif "backend" in desc_lower or "django" in desc_lower or "api" in desc_lower:
                    fallback_skills = ["Backend Development", "Python", "SQL"]
                elif "data" in desc_lower:
                    fallback_skills = ["Data Analysis", "SQL", "Python"]
                else:
                    fallback_skills = ["Software Engineering"]
                
            return EnrichmentResult(
                result={"skills": fallback_skills},
                model_name=model_name,
                model_version="fallback",
                prompt_version=self.version,
                confidence_score=0.5
            )
