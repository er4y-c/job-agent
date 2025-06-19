import streamlit as st
import json
from datetime import datetime
from agents.cover_letter_writer import CoverLetterWriterAgent
from utils.mongodb import db

def show():
    st.header("✉️ Cover Letter Generator")
    st.write("Generate a personalized cover letter based on your CV and the job requirements.")
    
    # Get CV and Job analyses from MongoDB
    cv_analyses = db.get_cv_analyses()
    job_analyses = db.get_job_analyses()
    
    if not cv_analyses or not job_analyses:
        st.warning("Please analyze at least one CV and one job posting first.")
        return
    
    # Create display options for CV analyses
    cv_options = []
    for analysis in cv_analyses:
        created_at = analysis["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        name = analysis.get("personal_info", {}).get("name", "Unknown")
        option = f"{created_at} - {name}"
        cv_options.append((option, str(analysis["_id"]), analysis))
    
    # Create display options for job analyses
    job_options = []
    for analysis in job_analyses:
        created_at = analysis["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        job_title = analysis.get("job_title", "Unknown")
        company = analysis.get("company", "Unknown")
        option = f"{created_at} - {job_title} at {company}"
        job_options.append((option, str(analysis["_id"]), analysis))
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        selected_cv = st.selectbox(
            "Select CV Analysis:",
            cv_options,
            format_func=lambda x: x[0]
        )
    
    with col2:
        selected_job = st.selectbox(
            "Select Job Analysis:",
            job_options,
            format_func=lambda x: x[0]
        )
    
    with col3:
        tone = st.selectbox("Tone:", ["professional", "enthusiastic", "confident", "friendly"])
    
    if st.button("Generate Cover Letter", type="primary"):
        with st.spinner("Generating cover letter..."):
            try:
                # Get the full data from selected options
                cv_data = selected_cv[2]
                job_data = selected_job[2]
                
                # Remove MongoDB fields
                cv_data_clean = {k: v for k, v in cv_data.items() if k not in ["_id", "created_at", "type"]}
                job_data_clean = {k: v for k, v in job_data.items() if k not in ["_id", "created_at", "type"]}
                
                agent = CoverLetterWriterAgent()
                result = agent.run(cv_data_clean, job_data_clean, tone)
                
                # Add reference to source documents
                result["cv_id"] = selected_cv[1]
                result["job_id"] = selected_job[1]
                result["cv_name"] = cv_data.get("personal_info", {}).get("name", "Unknown")
                result["job_title"] = job_data.get("job_title", "Unknown")
                result["company"] = job_data.get("company", "Unknown")
                result["tone"] = tone
                
                # Save to MongoDB
                doc_id = db.save_cover_letter(result)
                
                st.success(f"Cover letter generated successfully! Document ID: {doc_id}")
                
                st.subheader("Generated Cover Letter")
                
                st.text_area("Cover Letter", value=result.get("full_text", ""), height=400)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download as TXT",
                        data=result.get("full_text", ""),
                        file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    st.download_button(
                        label="Download Full JSON",
                        data=json.dumps(result, indent=2),
                        file_name=f"cover_letter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with st.expander("📌 Key Points Highlighted"):
                    for point in result.get("key_points_highlighted", []):
                        st.write(f"• {point}")
                
                with st.expander("💪 Skills Emphasized"):
                    for skill in result.get("skills_emphasized", []):
                        st.write(f"• {skill}")
                
                with st.expander("🏢 Company Research Points"):
                    for point in result.get("company_research_points", []):
                        st.write(f"• {point}")
                
                st.info(f"**Call to Action:** {result.get('call_to_action', '')}")
                
            except Exception as e:
                st.error(f"Error generating cover letter: {str(e)}")
    
    st.markdown("---")
    st.subheader("📁 Previous Cover Letters")
    
    letters = db.get_cover_letters()
    if letters:
        # Create display options with timestamp and details
        options = []
        for letter in letters:
            created_at = letter["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            cv_name = letter.get("cv_name", "Unknown")
            job_title = letter.get("job_title", "Unknown")
            company = letter.get("company", "Unknown")
            tone = letter.get("tone", "professional")
            option = f"{created_at} - {cv_name} for {job_title} at {company} ({tone})"
            options.append((option, str(letter["_id"])))
        
        selected = st.selectbox(
            "Select a cover letter to view:",
            options,
            format_func=lambda x: x[0]
        )
        
        if st.button("Load Selected Letter"):
            doc_id = selected[1]
            data = db.get_cover_letter_by_id(doc_id)
            if data:
                st.text_area("Cover Letter", value=data.get("full_text", ""), height=400)