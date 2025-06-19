import json
from typing import Dict
from agents.base_agent import BaseAgent
from agno.agent import Function

class CoverLetterWriterAgent(BaseAgent):
    def __init__(self):
        self.write_cover_letter = Function(
            name="write_cover_letter",
            description="Generate a tailored cover letter",
            parameters={
                "type": "object",
                "properties": {
                    "cv_data": {"type": "string", "description": "JSON string of CV analysis"},
                    "job_data": {"type": "string", "description": "JSON string of job analysis"},
                    "tone": {"type": "string", "description": "Tone of the letter (professional, enthusiastic, etc.)"}
                },
                "required": ["cv_data", "job_data"]
            },
            handler=self.write_cover_letter_handler
        )
        
        super().__init__(
            name="Cover Letter Writer",
            description="Generates personalized cover letters based on CV and job requirements"
        )
    
    def write_cover_letter_handler(self, cv_data: str, job_data: str, 
                                 tone: str = "professional") -> Dict:
        cv = json.loads(cv_data)
        job = json.loads(job_data)
        
        prompt = f"""
        Write a compelling cover letter for the following job application.
        
        Candidate CV Data:
        {json.dumps(cv, indent=2)}
        
        Job Posting Data:
        {json.dumps(job, indent=2)}
        
        Tone: {tone}
        
        Create a cover letter that:
        1. Shows enthusiasm for the specific role and company
        2. Highlights relevant experience and skills that match job requirements
        3. Demonstrates knowledge of the company and role
        4. Explains why the candidate is a great fit
        5. Includes specific examples from their experience
        6. Has a strong opening and closing
        7. Is concise (350-400 words)
        
        Return a JSON object with:
        {{
            "cover_letter": {{
                "salutation": "",
                "opening_paragraph": "",
                "body_paragraph_1": "",
                "body_paragraph_2": "",
                "body_paragraph_3": "",
                "closing_paragraph": "",
                "sign_off": ""
            }},
            "key_points_highlighted": [],
            "skills_emphasized": [],
            "company_research_points": [],
            "call_to_action": "",
            "full_text": ""
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer creating compelling, personalized cover letters."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        sections = result['cover_letter']
        full_text = f"{sections['salutation']}\n\n"
        full_text += f"{sections['opening_paragraph']}\n\n"
        full_text += f"{sections['body_paragraph_1']}\n\n"
        full_text += f"{sections['body_paragraph_2']}\n\n"
        full_text += f"{sections['body_paragraph_3']}\n\n"
        full_text += f"{sections['closing_paragraph']}\n\n"
        full_text += sections['sign_off']
        
        result['full_text'] = full_text
        
        return result
    
    def run(self, cv_analysis: Dict, job_analysis: Dict, tone: str = "professional") -> Dict:
        cv_data = json.dumps(cv_analysis)
        job_data = json.dumps(job_analysis)
        
        result = self.write_cover_letter_handler(cv_data=cv_data, job_data=job_data, tone=tone)
        return result