import json
from typing import Dict
from agents.base_agent import BaseAgent
from agno.agent import Function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

class JobAnalyzerAgent(BaseAgent):
    def __init__(self):
        self.analyze_job = Function(
            name="analyze_job",
            description="Analyze a job posting from LinkedIn URL",
            parameters={
                "type": "object",
                "properties": {
                    "job_url": {"type": "string", "description": "LinkedIn job posting URL"},
                    "job_content": {"type": "string", "description": "Job posting content"}
                },
                "required": ["job_content"]
            },
            handler=self.analyze_job_handler
        )
        
        super().__init__(
            name="Job Analyzer",
            description="Analyzes LinkedIn job postings from URL"
        )
    
    def setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def scrape_job_content(self, url: str) -> str:
        driver = self.setup_driver()
        content = ""
        
        try:
            driver.get(url)
            time.sleep(3)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            job_description = soup.find('div', class_='description__text')
            if job_description:
                content = job_description.get_text(strip=True, separator='\n')
            else:
                content = "Could not extract job description"
                
        except Exception as e:
            content = f"Error scraping job: {e}"
        finally:
            driver.quit()
        
        return content
    
    def analyze_job_handler(self, job_content: str) -> Dict:
        prompt = f"""
        Analyze the following job posting and extract structured information:
        
        {job_content}
        
        Extract and return a JSON object with the following structure:
        {{
            "job_title": "",
            "company": "",
            "location": "",
            "employment_type": "",
            "experience_level": "",
            "salary_range": "",
            "required_skills": {{
                "technical": [],
                "soft": []
            }},
            "nice_to_have_skills": [],
            "responsibilities": [],
            "requirements": [],
            "benefits": [],
            "company_culture": "",
            "application_deadline": "",
            "remote_options": "",
            "key_qualifications": [],
            "preferred_qualifications": []
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a job posting analyzer. Extract information accurately and return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def run(self, job_url: str) -> Dict:
        job_content = self.scrape_job_content(job_url)
        result = self.analyze_job_handler(job_content=job_content)
        result['job_url'] = job_url
        return result