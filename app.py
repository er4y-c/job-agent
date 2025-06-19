import streamlit as st
from streamlit_option_menu import option_menu
import sys
sys.path.append('.')

st.set_page_config(
    page_title="Job Application Assistant",
    page_icon="💼",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        padding: 0rem 0rem;
        color: #71717a;
    }
    .stApp {
        background-color: #f5f5f5;
        color: #71717a;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #71717a;
    }
    p, span, label {
        color: #71717a;
    }
    div {
        color: #71717a;
    }
    .stMarkdown {
        color: #71717a;
    }
    .stButton > button {
        background-color: #3498db;
        color: white;
    }
    .stButton > button:hover {
        background-color: #2980b9;
    }
    /* Ensure text inputs and other form elements have dark text */
    .stTextInput > div > div > input {
        color: #71717a;
    }
    .stSelectbox > div > div > div {
        color: #71717a;
    }
    .stTextArea > div > div > textarea {
        color: #71717a;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Job Application Assistant")
st.markdown("---")

with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["CV Analyzer", "Job Search", "Job Analyzer", "Suitability Report", "Cover Letter"],
        icons=["file-person", "search", "briefcase", "graph-up", "envelope"],
        menu_icon="cast",
        default_index=0,
    )

if selected == "CV Analyzer":
    from pages import cv_analyzer_page
    cv_analyzer_page.show()
elif selected == "Job Search":
    from pages import job_search_page
    job_search_page.show()
elif selected == "Job Analyzer":
    from pages import job_analyzer_page
    job_analyzer_page.show()
elif selected == "Suitability Report":
    from pages import suitability_report_page
    suitability_report_page.show()
elif selected == "Cover Letter":
    from pages import cover_letter_page
    cover_letter_page.show()