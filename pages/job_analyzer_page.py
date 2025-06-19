import streamlit as st
from datetime import datetime
from agents.job_analyzer import JobAnalyzerAgent
from utils.mongodb import db

def show():
    st.header("🔬 Job Posting Analysis")
    st.write("Analyze a LinkedIn job posting by entering its URL.")
    
    job_url = st.text_input("LinkedIn Job URL", placeholder="https://www.linkedin.com/jobs/view/...")
    
    if st.button("Analyze Job Posting", type="primary"):
        if job_url:
            with st.spinner("Analyzing job posting..."):
                try:
                    agent = JobAnalyzerAgent()
                    result = agent.run(job_url)
                    
                    # Save to MongoDB
                    result["job_url"] = job_url
                    doc_id = db.save_job_analysis(result)
                    
                    st.success(f"Job analyzed successfully! Document ID: {doc_id}")
                    
                    st.subheader("Analysis Results")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Job Title:** {result.get('job_title', 'N/A')}")
                        st.write(f"**Company:** {result.get('company', 'N/A')}")
                        st.write(f"**Location:** {result.get('location', 'N/A')}")
                    with col2:
                        st.write(f"**Employment Type:** {result.get('employment_type', 'N/A')}")
                        st.write(f"**Experience Level:** {result.get('experience_level', 'N/A')}")
                        st.write(f"**Remote Options:** {result.get('remote_options', 'N/A')}")
                    
                    with st.expander("Required Skills"):
                        skills = result.get("required_skills", {})
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Technical Skills:**")
                            for skill in skills.get("technical", []):
                                st.write(f"• {skill}")
                        with col2:
                            st.write("**Soft Skills:**")
                            for skill in skills.get("soft", []):
                                st.write(f"• {skill}")
                    
                    with st.expander("Responsibilities"):
                        for resp in result.get("responsibilities", []):
                            st.write(f"• {resp}")
                    
                    with st.expander("Requirements"):
                        for req in result.get("requirements", []):
                            st.write(f"• {req}")
                    
                    with st.expander("Benefits"):
                        for benefit in result.get("benefits", []):
                            st.write(f"• {benefit}")
                    
                    with st.expander("Key Qualifications"):
                        for qual in result.get("key_qualifications", []):
                            st.write(f"• {qual}")
                    
                    with st.expander("Full JSON Data"):
                        st.json(result)
                        
                except Exception as e:
                    st.error(f"Error analyzing job: {str(e)}")
        else:
            st.warning("Please enter a LinkedIn job URL.")
    
    st.markdown("---")
    st.subheader("📁 Previously Analyzed Jobs")
    
    job_analyses = db.get_job_analyses()
    if job_analyses:
        # Create display options with timestamp and job details
        options = []
        for analysis in job_analyses:
            created_at = analysis["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            job_title = analysis.get("job_title", "Unknown")
            company = analysis.get("company", "Unknown")
            option = f"{created_at} - {job_title} at {company}"
            options.append((option, str(analysis["_id"])))
        
        selected = st.selectbox(
            "Select a job analysis to view:",
            options,
            format_func=lambda x: x[0]
        )
        
        if st.button("Load Selected Analysis"):
            doc_id = selected[1]
            data = db.get_job_analysis_by_id(doc_id)
            if data:
                # Remove MongoDB specific fields for display
                data.pop("_id", None)
                data.pop("created_at", None)
                data.pop("type", None)
                st.json(data)
    else:
        st.info("No previous job analyses found.")