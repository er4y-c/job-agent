import streamlit as st
from datetime import datetime
from agents.suitability_reporter import SuitabilityReporterAgent
from utils.mongodb import db

def show():
    st.header("📊 Job Suitability Report")
    st.write("Generate a detailed suitability report by comparing your CV with a job posting.")
    
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
    
    col1, col2 = st.columns(2)
    
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
    
    if st.button("Generate Suitability Report", type="primary"):
        with st.spinner("Generating suitability report..."):
            try:
                # Get the full data from selected options
                cv_data = selected_cv[2]
                job_data = selected_job[2]
                
                # Remove MongoDB fields
                cv_data_clean = {k: v for k, v in cv_data.items() if k not in ["_id", "created_at", "type"]}
                job_data_clean = {k: v for k, v in job_data.items() if k not in ["_id", "created_at", "type"]}
                
                agent = SuitabilityReporterAgent()
                report = agent.run(cv_data_clean, job_data_clean)
                
                # Add reference to source documents
                report["cv_id"] = selected_cv[1]
                report["job_id"] = selected_job[1]
                report["cv_name"] = cv_data.get("personal_info", {}).get("name", "Unknown")
                report["job_title"] = job_data.get("job_title", "Unknown")
                report["company"] = job_data.get("company", "Unknown")
                
                # Save to MongoDB
                doc_id = db.save_suitability_report(report)
                
                st.success(f"Report generated successfully! Document ID: {doc_id}")
                
                st.subheader("Suitability Report")
                
                score = report.get("overall_match_score", 0)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.metric("Overall Match Score", f"{score}%")
                    if score >= 80:
                        st.success("Excellent match!")
                    elif score >= 60:
                        st.info("Good match with some gaps")
                    else:
                        st.warning("Consider improving key areas")
                
                st.write(f"**Summary:** {report.get('summary', '')}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("🌟 Strengths"):
                        for strength in report.get("strengths", []):
                            relevance_color = {
                                "high": "🟢",
                                "medium": "🟡",
                                "low": "🔵"
                            }
                            st.write(f"{relevance_color.get(strength.get('relevance', 'medium'))} **{strength.get('category', '')}**")
                            st.write(strength.get('description', ''))
                            st.write("---")
                
                with col2:
                    with st.expander("📈 Areas for Improvement"):
                        for gap in report.get("gaps", []):
                            st.write(f"**{gap.get('requirement', '')}**")
                            st.write(f"Current: {gap.get('current_level', '')}")
                            st.write(f"Required: {gap.get('required_level', '')}")
                            st.write(f"💡 {gap.get('improvement_suggestion', '')}")
                            st.write("---")
                
                with st.expander("🎯 Skill Analysis"):
                    skills = report.get("skill_matches", {})
                    tech_skills = skills.get("technical_skills", {})
                    soft_skills = skills.get("soft_skills", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write("**Matched Technical Skills:**")
                        for skill in tech_skills.get("matched", []):
                            st.write(f"✅ {skill}")
                    with col2:
                        st.write("**Missing Technical Skills:**")
                        for skill in tech_skills.get("missing", []):
                            st.write(f"❌ {skill}")
                    with col3:
                        st.write("**Additional Skills You Have:**")
                        for skill in tech_skills.get("additional", []):
                            st.write(f"➕ {skill}")
                
                with st.expander("💼 Experience Analysis"):
                    exp_analysis = report.get("experience_analysis", {})
                    st.write(f"**Years Required:** {exp_analysis.get('years_required', 'N/A')}")
                    st.write(f"**Years You Have:** {exp_analysis.get('years_possessed', 'N/A')}")
                    st.write("**Relevant Experience:**")
                    for exp in exp_analysis.get("relevant_experience", []):
                        st.write(f"• {exp}")
                
                with st.expander("🎓 Recommendations"):
                    for rec in report.get("recommendations", []):
                        priority_emoji = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }
                        st.write(f"{priority_emoji.get(rec.get('priority', 'medium'))} **{rec.get('action', '')}**")
                        st.write(f"Timeframe: {rec.get('timeframe', '')}")
                        st.write("---")
                
                with st.expander("🗣️ Interview Preparation"):
                    prep = report.get("interview_preparation", {})
                    
                    st.write("**Likely Questions:**")
                    for q in prep.get("likely_questions", []):
                        st.write(f"• {q}")
                    
                    st.write("\n**Key Talking Points:**")
                    for point in prep.get("talking_points", []):
                        st.write(f"• {point}")
                    
                    st.write("\n**Areas to Emphasize:**")
                    for area in prep.get("areas_to_emphasize", []):
                        st.write(f"• {area}")
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
    
    st.markdown("---")
    st.subheader("📁 Previous Reports")
    
    reports = db.get_suitability_reports()
    if reports:
        # Create display options with timestamp and details
        options = []
        for report in reports:
            created_at = report["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            cv_name = report.get("cv_name", "Unknown")
            job_title = report.get("job_title", "Unknown")
            company = report.get("company", "Unknown")
            score = report.get("overall_match_score", 0)
            option = f"{created_at} - {cv_name} for {job_title} at {company} ({score}%)"
            options.append((option, str(report["_id"])))
        
        selected = st.selectbox(
            "Select a report to view:",
            options,
            format_func=lambda x: x[0]
        )
        
        if st.button("Load Selected Report"):
            doc_id = selected[1]
            data = db.get_suitability_report_by_id(doc_id)
            if data:
                # Remove MongoDB specific fields for display
                data.pop("_id", None)
                data.pop("created_at", None)
                data.pop("type", None)
                st.json(data)
    else:
        st.info("No previous reports found.")