import json
import PyPDF2
from typing import Dict
from agents.base_agent import BaseAgent
from agno.agent import Function

class CVAnalyzerAgent(BaseAgent):
    def __init__(self):
        self.analyze_cv = Function(
            name="analyze_cv",
            description="Extract and analyze information from CV",
            parameters={
                "type": "object",
                "properties": {
                    "cv_text": {"type": "string", "description": "The extracted text from CV PDF"}
                },
                "required": ["cv_text"]
            },
            handler=self.analyze_cv_handler
        )
        
        super().__init__(
            name="CV Analyzer",
            description="Analyzes CV/Resume PDFs and extracts structured information"
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def analyze_cv_handler(self, cv_text: str) -> Dict:
        prompt = f"""
        Analyze the following CV/Resume and extract structured information:
        
        {cv_text}
        
        Extract and return a JSON object with the following structure:
        {{
            "personal_info": {{
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": ""
            }},
            "summary": "",
            "skills": {{
                "technical": [],
                "soft": [],
                "languages": []
            }},
            "experience": [
                {{
                    "position": "",
                    "company": "",
                    "duration": "",
                    "location": "",
                    "responsibilities": []
                }}
            ],
            "education": [
                {{
                    "degree": "",
                    "institution": "",
                    "graduation_date": "",
                    "gpa": ""
                }}
            ],
            "projects": [
                {{
                    "name": "",
                    "description": "",
                    "technologies": [],
                    "link": ""
                }}
            ],
            "certifications": [],
            "achievements": []
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional CV analyzer. Extract information accurately and return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def run(self, pdf_path: str) -> Dict:
        extracted_text = self.extract_text_from_pdf(pdf_path)
        result = self.analyze_cv_handler(cv_text=extracted_text)
        return result