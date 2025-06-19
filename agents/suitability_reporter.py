import json
from typing import Dict
from agents.base_agent import BaseAgent
from agno.agent import Function

class SuitabilityReporterAgent(BaseAgent):
    def __init__(self):
        self.generate_report = Function(
            name="generate_report",
            description="Generate suitability report for job application",
            parameters={
                "type": "object",
                "properties": {
                    "cv_data": {"type": "string", "description": "JSON string of CV analysis"},
                    "job_data": {"type": "string", "description": "JSON string of job analysis"}
                },
                "required": ["cv_data", "job_data"]
            },
            handler=self.generate_report_handler
        )
        
        super().__init__(
            name="Suitability Reporter",
            description="Generates job suitability reports by comparing CV and job requirements"
        )
    
    def generate_report_handler(self, cv_data: str, job_data: str) -> Dict:
        cv = json.loads(cv_data)
        job = json.loads(job_data)
        
        prompt = f"""
        Generate a comprehensive job suitability report by comparing the candidate's CV with the job requirements.
        
        CV Data:
        {json.dumps(cv, indent=2)}
        
        Job Data:
        {json.dumps(job, indent=2)}
        
        Return a JSON object with the following structure:
        {{
            "overall_match_score": 0-100,
            "summary": "Brief summary of the match",
            "strengths": [
                {{
                    "category": "",
                    "description": "",
                    "relevance": "high/medium/low"
                }}
            ],
            "gaps": [
                {{
                    "requirement": "",
                    "current_level": "",
                    "required_level": "",
                    "improvement_suggestion": ""
                }}
            ],
            "skill_matches": {{
                "technical_skills": {{
                    "matched": [],
                    "missing": [],
                    "additional": []
                }},
                "soft_skills": {{
                    "matched": [],
                    "missing": []
                }}
            }},
            "experience_analysis": {{
                "years_required": "",
                "years_possessed": "",
                "relevant_experience": [],
                "transferable_skills": []
            }},
            "education_match": {{
                "meets_requirements": true/false,
                "details": ""
            }},
            "recommendations": [
                {{
                    "priority": "high/medium/low",
                    "action": "",
                    "timeframe": ""
                }}
            ],
            "interview_preparation": {{
                "likely_questions": [],
                "talking_points": [],
                "areas_to_emphasize": []
            }}
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a career advisor generating detailed job suitability reports."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def run(self, cv_analysis: Dict, job_analysis: Dict) -> Dict:
        cv_data = json.dumps(cv_analysis)
        job_data = json.dumps(job_analysis)
        
        result = self.generate_report_handler(cv_data=cv_data, job_data=job_data)
        return result