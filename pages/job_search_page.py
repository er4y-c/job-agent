import streamlit as st
from datetime import datetime
from agents.job_searcher import JobSearchAgent
from utils.mongodb import db

def show():
    st.header("🔍 LinkedIn Job Search")
    st.write("Search for jobs on LinkedIn using various filters.")
    
    with st.form("job_search_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title*", placeholder="e.g., Software Engineer")
            location = st.text_input("Location", placeholder="e.g., New York, NY")
        
        with col2:
            experience_level = st.selectbox(
                "Experience Level",
                ["", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"]
            )
            posted_date = st.selectbox(
                "Posted Date",
                ["", "Past 24 hours", "Past week", "Past month", "Any time"]
            )
        
        submitted = st.form_submit_button("Search Jobs", type="primary")
    
    if submitted and job_title:
        with st.spinner("Searching for jobs..."):
            try:
                filters = {
                    "job_title": job_title,
                    "location": location,
                    "experience_level": experience_level,
                    "posted_date": posted_date
                }
                
                agent = JobSearchAgent()
                results = agent.run(filters)
                
                if results:
                    # Save to MongoDB
                    search_data = {
                        "filters": filters,
                        "results": results,
                        "job_count": len(results)
                    }
                    doc_id = db.save_job_search(search_data)
                    
                    st.success(f"Found {len(results)} jobs! Document ID: {doc_id}")
                    
                    st.subheader("Search Results")
                    
                    for idx, job in enumerate(results, 1):
                        with st.expander(f"{idx}. {job.get('title', 'N/A')} at {job.get('company', 'N/A')}"):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**Location:** {job.get('location', 'N/A')}")
                                st.write(f"**Posted:** {job.get('posted_date', 'N/A')}")
                                st.write(f"**Experience Level:** {job.get('experience_level', 'N/A')}")
                            with col2:
                                if job.get('url') != 'N/A':
                                    st.link_button("View Job", job.get('url'))
                else:
                    st.warning("No jobs found. Try adjusting your search criteria.")
                    
            except Exception as e:
                st.error(f"Error searching jobs: {str(e)}")
    elif submitted:
        st.warning("Please enter a job title to search.")
    
    st.markdown("---")
    st.subheader("📁 Previous Job Searches")
    
    job_searches = db.get_job_searches()
    if job_searches:
        # Create display options with timestamp and search criteria
        options = []
        for search in job_searches:
            created_at = search["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            job_title = search.get("filters", {}).get("job_title", "Unknown")
            job_count = search.get("job_count", 0)
            option = f"{created_at} - {job_title} ({job_count} jobs)"
            options.append((option, str(search["_id"])))
        
        selected = st.selectbox(
            "Select a job search to view:",
            options,
            format_func=lambda x: x[0]
        )
        
        if st.button("Load Selected Search"):
            doc_id = selected[1]
            data = db.get_job_search_by_id(doc_id)
            if data:
                results = data.get("results", [])
                st.write(f"Found {len(results)} jobs in this search:")
                for idx, job in enumerate(results, 1):
                    st.write(f"{idx}. **{job.get('title')}** at {job.get('company')} - {job.get('location')}")
    else:
        st.info("No previous job searches found.")