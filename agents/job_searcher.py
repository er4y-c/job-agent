import json
from typing import Dict, List
from agents.base_agent import BaseAgent
from agno.agent import Function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

class JobSearchAgent(BaseAgent):
    def __init__(self):
        self.search_function = Function(
            name="search_jobs",
            description="Search LinkedIn jobs with filters",
            parameters={
                "type": "object",
                "properties": {
                    "job_title": {"type": "string", "description": "Job title to search"},
                    "location": {"type": "string", "description": "Job location"},
                    "experience_level": {"type": "string", "description": "Experience level filter"},
                    "posted_date": {"type": "string", "description": "When job was posted"}
                },
                "required": ["job_title"]
            },
            handler=self.search_jobs_handler
        )
        
        super().__init__(
            name="Job Search Agent",
            description="Searches for jobs on LinkedIn based on filters"
        )
    
    def setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def search_jobs_handler(self, job_title: str, location: str = "", 
                           experience_level: str = "", posted_date: str = "") -> List[Dict]:
        driver = self.setup_driver()
        jobs = []
        
        try:
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}"
            if location:
                search_url += f"&location={location}"
            
            driver.get(search_url)
            time.sleep(3)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            job_cards = soup.find_all('div', class_='base-card')[:10]
            
            for card in job_cards:
                job = {}
                
                title_elem = card.find('h3', class_='base-search-card__title')
                job['title'] = title_elem.text.strip() if title_elem else "N/A"
                
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                job['company'] = company_elem.text.strip() if company_elem else "N/A"
                
                location_elem = card.find('span', class_='job-search-card__location')
                job['location'] = location_elem.text.strip() if location_elem else "N/A"
                
                link_elem = card.find('a', class_='base-card__full-link')
                job['url'] = link_elem['href'] if link_elem else "N/A"
                
                job['posted_date'] = posted_date if posted_date else "Recent"
                job['experience_level'] = experience_level if experience_level else "Not specified"
                
                jobs.append(job)
                
        except Exception as e:
            print(f"Error searching jobs: {e}")
        finally:
            driver.quit()
        
        return jobs
    
    def run(self, filters: Dict) -> List[Dict]:
        # Directly call the handler since we're not using agno's execution
        return self.search_jobs_handler(
            job_title=filters.get('job_title', ''),
            location=filters.get('location', ''),
            experience_level=filters.get('experience_level', ''),
            posted_date=filters.get('posted_date', '')
        )