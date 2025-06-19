# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Job Application Assistant built with Python, using Streamlit for the web interface and multi-agent architecture for different functionalities. The application helps users analyze CVs, search for jobs, analyze job postings, generate suitability reports, and create cover letters.

## Development Commands

### Setup and Running
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Set up environment variables
# Create a .env file with: OPENAI_API_KEY=your_openai_api_key_here

# Run the application
uv run streamlit run app.py

# Activate virtual environment (if needed)
source .venv/bin/activate
```

### Development Tools
```bash
# Run linting
uv run ruff check .
uv run ruff format .

# Run code formatting
uv run black .

# Run tests
uv run pytest
uv run pytest --cov  # with coverage
```

### Package Management
```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Update dependencies
uv sync --refresh

# Show installed packages
uv pip list
```

## Architecture

### Agent-Based Architecture
The application uses a multi-agent system with the following structure:
- **BaseAgent** (`agents/base_agent.py`): Abstract base class for all agents using Agno library
- Each agent inherits from BaseAgent and implements specific functionality:
  - `cv_analyzer.py`: Extracts structured information from PDF resumes
  - `job_searcher.py`: Searches LinkedIn jobs using Selenium web scraping
  - `job_analyzer.py`: Analyzes job postings from LinkedIn URLs
  - `suitability_reporter.py`: Compares CV data with job requirements
  - `cover_letter_writer.py`: Generates personalized cover letters

### UI Layer
- Built with Streamlit and streamlit-option-menu
- Each page in `pages/` corresponds to an agent and provides the UI for that functionality
- Main entry point is `app.py` which sets up the navigation menu

### Data Storage
- All data is stored as JSON files in the `data/` directory
- The directory is auto-created by `utils/config.py`

### Key Dependencies
- **Streamlit**: Web interface
- **OpenAI API**: LLM capabilities for agents
- **Agno**: Agent framework
- **Selenium + BeautifulSoup**: Web scraping for job searches
- **PyPDF2**: PDF parsing for CV analysis

### Configuration
- Environment variables loaded from `.env` file
- OpenAI API key required for agent functionality
- Configuration centralized in `utils/config.py`