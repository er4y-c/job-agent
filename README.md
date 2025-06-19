# Job Application Assistant

A multi-agent system built with Python, OpenAI, Agno, and Streamlit to streamline your job application process.

## Features

1. **CV Analysis**: Upload PDF resumes and extract structured information
2. **Job Search**: Search LinkedIn jobs with filters (title, location, experience, date)
3. **Job Analysis**: Analyze job postings from LinkedIn URLs
4. **Suitability Reports**: Compare CVs with job requirements for detailed matching reports
5. **Cover Letter Generation**: Create personalized cover letters based on CV and job data

## Setup

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install dependencies:
```bash
uv sync
```

3. Set up your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
uv run streamlit run app.py
```

## Project Structure

```
JobAgent/
├── agents/              # Agent implementations
│   ├── base_agent.py
│   ├── cv_analyzer.py
│   ├── job_searcher.py
│   ├── job_analyzer.py
│   ├── suitability_reporter.py
│   └── cover_letter_writer.py
├── pages/               # Streamlit page components
│   ├── cv_analyzer_page.py
│   ├── job_search_page.py
│   ├── job_analyzer_page.py
│   ├── suitability_report_page.py
│   └── cover_letter_page.py
├── utils/               # Utilities and configuration
│   └── config.py
├── data/                # Storage for JSON files
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

## Usage

1. Start by analyzing your CV in the CV Analyzer page
2. Search for jobs or analyze specific job postings
3. Generate suitability reports to see how well you match
4. Create tailored cover letters for your applications

All data is saved as JSON files in the `data/` directory for easy access and reuse.