import streamlit as st
import os
import tempfile
from datetime import datetime
from agents.cv_analyzer import CVAnalyzerAgent
from utils.mongodb import db

def show():
    st.header("📄 CV Analysis")
    st.write("Upload your CV in PDF format to analyze and extract structured information.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"File uploaded: {uploaded_file.name}")
        
        with col2:
            if st.button("Analyze CV", type="primary"):
                with st.spinner("Analyzing your CV..."):
                    try:
                        # Create temporary file for PDF processing
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getbuffer())
                            temp_path = tmp_file.name
                        
                        agent = CVAnalyzerAgent()
                        result = agent.run(temp_path)
                        
                        # Clean up temp file
                        os.unlink(temp_path)
                        
                        # Save to MongoDB
                        doc_id = db.save_cv_analysis(result)
                        
                        st.success(f"CV analyzed successfully! Document ID: {doc_id}")
                        
                        st.subheader("Analysis Results")
                        
                        with st.expander("Personal Information"):
                            st.json(result.get("personal_info", {}))
                        
                        with st.expander("Summary"):
                            st.write(result.get("summary", ""))
                        
                        with st.expander("Skills"):
                            skills = result.get("skills", {})
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("**Technical Skills:**")
                                for skill in skills.get("technical", []):
                                    st.write(f"• {skill}")
                            with col2:
                                st.write("**Soft Skills:**")
                                for skill in skills.get("soft", []):
                                    st.write(f"• {skill}")
                            with col3:
                                st.write("**Languages:**")
                                for lang in skills.get("languages", []):
                                    st.write(f"• {lang}")
                        
                        with st.expander("Experience"):
                            for exp in result.get("experience", []):
                                st.write(f"**{exp.get('position', '')}** at {exp.get('company', '')}")
                                st.write(f"📅 {exp.get('duration', '')} | 📍 {exp.get('location', '')}")
                                for resp in exp.get("responsibilities", []):
                                    st.write(f"• {resp}")
                                st.write("---")
                        
                        with st.expander("Education"):
                            for edu in result.get("education", []):
                                st.write(f"**{edu.get('degree', '')}**")
                                st.write(f"{edu.get('institution', '')} | {edu.get('graduation_date', '')}")
                                if edu.get("gpa"):
                                    st.write(f"GPA: {edu.get('gpa')}")
                                st.write("---")
                        
                        with st.expander("Full JSON Data"):
                            st.json(result)
                        
                    except Exception as e:
                        st.error(f"Error analyzing CV: {str(e)}")
    
    st.markdown("---")
    st.subheader("📁 Previously Analyzed CVs")
    
    cv_analyses = db.get_cv_analyses()
    if cv_analyses:
        # Create display options with timestamp and name
        options = []
        for analysis in cv_analyses:
            created_at = analysis["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            name = analysis.get("personal_info", {}).get("name", "Unknown")
            option = f"{created_at} - {name}"
            options.append((option, str(analysis["_id"])))
        
        selected = st.selectbox(
            "Select a CV analysis to view:",
            options,
            format_func=lambda x: x[0]
        )
        
        if st.button("Load Selected Analysis"):
            doc_id = selected[1]
            data = db.get_cv_analysis_by_id(doc_id)
            if data:
                # Remove MongoDB specific fields for display
                data.pop("_id", None)
                data.pop("created_at", None)
                data.pop("type", None)
                st.json(data)
    else:
        st.info("No previous CV analyses found.")