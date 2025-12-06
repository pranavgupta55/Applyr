"""
Streamlit frontend for the Applyr internship bot.
Human-in-the-loop dashboard with Kanban board and action panels.
"""
import streamlit as st
from datetime import datetime
import time

from frontend.utils import (
    sync_jobs, add_manual_job, get_all_jobs, get_job,
    analyze_job, generate_assets, update_job, get_stats,
    discover_emails, draft_email, get_linkedin_search,
    copy_to_clipboard, open_url, open_resumes_folder,
    get_priority_badge, format_date
)

# Page config
st.set_page_config(
    page_title="Applyr - Internship Application Bot",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .job-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        margin-bottom: 0.5rem;
        background: white;
    }
    .priority-badge {
        font-weight: bold;
        font-size: 0.9em;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        border-radius: 0.3rem;
        background: #e0e0e0;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)


# ==================== SIDEBAR ====================

with st.sidebar:
    st.title("🎯 Applyr")
    st.caption("Human-in-the-Loop Internship Bot")

    st.divider()

    # Navigation
    page = st.radio(
        "Navigation",
        ["Dashboard", "Cold Emails", "Answer Bank", "Settings"],
        label_visibility="collapsed"
    )

    st.divider()

    # Quick stats
    stats = get_stats()
    if stats:
        st.metric("Total Jobs", stats.get("total_jobs", 0))
        st.metric("Penn Connections", stats.get("penn_connections", 0))

        with st.expander("📊 Breakdown"):
            for status, count in stats.get("by_status", {}).items():
                st.write(f"**{status}:** {count}")


# ==================== DASHBOARD PAGE ====================

if page == "Dashboard":
    st.title("Job Application Dashboard")

    # Top action bar
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("🔄 Sync Jobs from GitHub", use_container_width=True):
            with st.spinner("Syncing jobs..."):
                result = sync_jobs()
                if result:
                    st.success(f"✅ {result.get('message', 'Sync complete!')}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Sync failed. Check backend connection.")

    with col2:
        with st.expander("➕ Add Manual Job"):
            url = st.text_input("Job URL (Handshake or Company Page)")
            company = st.text_input("Company (optional)")
            role = st.text_input("Role (optional)")

            if st.button("Add Job"):
                if url:
                    with st.spinner("Processing..."):
                        result = add_manual_job(url, company, role)
                        if result:
                            st.success("✅ Job added!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Failed to add job")
                else:
                    st.warning("Please enter a URL")

    st.divider()

    # Kanban Board
    st.subheader("Application Pipeline")

    # Get all jobs
    all_jobs = get_all_jobs()

    if not all_jobs:
        st.info("No jobs yet. Click 'Sync Jobs' to get started!")
    else:
        # Group by status
        jobs_by_status = {
            "New": [],
            "Analyzed": [],
            "Ready to Apply": [],
            "Applied": [],
            "Rejected": [],
            "Interview": []
        }

        for job in all_jobs:
            status = job.get("status", "New")
            jobs_by_status[status].append(job)

        # Display Kanban columns
        cols = st.columns(4)

        # Column 1: New Jobs
        with cols[0]:
            st.markdown("### 🆕 New")
            st.caption(f"{len(jobs_by_status['New'])} jobs")

            for job in jobs_by_status['New']:
                with st.container():
                    st.markdown(f"**{job['company']}**")
                    st.caption(job['role'])
                    st.caption(get_priority_badge(job.get('priority_score', 3)))

                    if st.button("🔍 Analyze", key=f"analyze_{job['id']}"):
                        with st.spinner("Analyzing..."):
                            result = analyze_job(job['id'])
                            if result:
                                st.success("✅ Analysis complete!")
                                time.sleep(1)
                                st.rerun()

                    st.divider()

        # Column 2: Analyzed (Ready for Review)
        with cols[1]:
            st.markdown("### ✅ Analyzed")
            st.caption(f"{len(jobs_by_status['Analyzed'])} jobs")

            for job in jobs_by_status['Analyzed']:
                with st.container():
                    st.markdown(f"**{job['company']}**")
                    st.caption(job['role'])
                    st.caption(get_priority_badge(job.get('priority_score', 3)))

                    # Show tags
                    if job.get('tags'):
                        tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in job['tags']])
                        st.markdown(tags_html, unsafe_allow_html=True)

                    if st.button("🚀 Prepare", key=f"prepare_{job['id']}"):
                        st.session_state['selected_job'] = job['id']

                    st.divider()

        # Column 3: Applied
        with cols[2]:
            st.markdown("### 📤 Applied")
            st.caption(f"{len(jobs_by_status['Applied'])} jobs")

            for job in jobs_by_status['Applied']:
                with st.container():
                    st.markdown(f"**{job['company']}**")
                    st.caption(job['role'])
                    if job.get('date_applied'):
                        st.caption(f"Applied: {format_date(job['date_applied'])}")
                    st.divider()

        # Column 4: Interview/Rejected
        with cols[3]:
            st.markdown("### 🎯 Active")
            st.caption(f"{len(jobs_by_status['Interview'])} interviews")

            for job in jobs_by_status['Interview']:
                with st.container():
                    st.markdown(f"**{job['company']}**")
                    st.caption(job['role'])
                    st.divider()

    # Job Detail Panel (if selected)
    if 'selected_job' in st.session_state:
        st.divider()
        st.subheader("📋 Application Preparation")

        job_id = st.session_state['selected_job']
        job = get_job(job_id)

        if job:
            col1, col2 = st.columns([1, 1])

            with col1:
                st.markdown(f"### {job['company']}")
                st.markdown(f"**Role:** {job['role']}")
                st.markdown(f"**Priority:** {get_priority_badge(job.get('priority_score', 3))}")

                if job.get('penn_connection'):
                    st.info("🎓 Penn Connection Detected!")

                if job.get('tags'):
                    st.markdown("**Tags:**")
                    tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in job['tags']])
                    st.markdown(tags_html, unsafe_allow_html=True)

                st.markdown(f"**Resume Match:** {job.get('resume_match', 'N/A')}")

            with col2:
                st.markdown("### 'Why This Company' Paragraph")

                # Editable text area
                why_us = st.text_area(
                    "Edit if needed:",
                    value=job.get('why_us_text', ''),
                    height=150,
                    key="why_us_edit"
                )

                # Update button
                if st.button("💾 Update Text"):
                    update_job(job_id, {'why_us_text': why_us})
                    st.success("✅ Updated!")

            st.divider()

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📄 Generate PDF", use_container_width=True):
                    with st.spinner("Generating..."):
                        result = generate_assets(job_id)
                        if result:
                            st.success(f"✅ PDF created: {result['pdf_path']}")
                        else:
                            st.error("❌ Generation failed")

            with col2:
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    if copy_to_clipboard(why_us):
                        st.success("✅ Copied!")
                    else:
                        st.error("❌ Copy failed")

            with col3:
                if st.button("🔗 Open Application", use_container_width=True):
                    open_url(job['link'])
                    st.success("✅ Opened in browser!")

            with col4:
                if st.button("📂 Open Resumes", use_container_width=True):
                    open_resumes_folder()
                    st.success("✅ Finder opened!")

            st.divider()

            # Mark as applied
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**After submitting the application:**")
            with col2:
                if st.button("✅ Mark Applied", use_container_width=True):
                    update_job(job_id, {
                        'status': 'Applied',
                        'date_applied': datetime.now().isoformat()
                    })
                    st.success("✅ Marked as applied!")
                    del st.session_state['selected_job']
                    time.sleep(1)
                    st.rerun()


# ==================== COLD EMAILS PAGE ====================

elif page == "Cold Emails":
    st.title("Cold Email Outreach")

    st.markdown("""
    **Process:**
    1. Search LinkedIn for recruiter/engineer contacts
    2. Enter contact details below
    3. System generates email candidates and verifies them
    4. Draft email with AI
    5. You manually send the email
    """)

    st.divider()

    # LinkedIn search helper
    st.subheader("1️⃣ Find Contacts")

    col1, col2 = st.columns([2, 1])
    with col1:
        search_company = st.text_input("Company Name")
    with col2:
        search_role = st.selectbox("Role", ["recruiter", "engineer", "hiring manager", "founder"])

    if st.button("🔍 Open LinkedIn Search"):
        result = get_linkedin_search(search_company, search_role)
        if result:
            open_url(result['search_url'])
            st.success("✅ LinkedIn search opened in browser!")

    st.divider()

    # Email discovery
    st.subheader("2️⃣ Discover Email")

    col1, col2, col3 = st.columns(3)
    with col1:
        company = st.text_input("Company")
    with col2:
        first_name = st.text_input("First Name")
    with col3:
        last_name = st.text_input("Last Name")

    if st.button("🔍 Find Emails"):
        if company and first_name and last_name:
            with st.spinner("Discovering and verifying emails..."):
                result = discover_emails(company, first_name, last_name)

                if result and result.get('candidates'):
                    st.success("✅ Email candidates found!")

                    st.markdown(f"**Domain:** {result['domain']}")

                    for candidate in result['candidates']:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.code(candidate['email'])
                        with col2:
                            status = candidate.get('status', 'Unknown')
                            if 'Verified' in status or 'Valid' in status:
                                st.success(status)
                            elif 'Risky' in status:
                                st.warning(status)
                            else:
                                st.error(status)
                        with col3:
                            if st.button("📋 Copy", key=f"copy_{candidate['email']}"):
                                copy_to_clipboard(candidate['email'])
                                st.success("✅")

                    st.session_state['email_contact'] = {
                        'company': company,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': result['candidates'][0]['email']
                    }
                else:
                    st.error("❌ No candidates found")
        else:
            st.warning("Please fill in all fields")

    st.divider()

    # Draft email
    if 'email_contact' in st.session_state:
        st.subheader("3️⃣ Draft Email")

        contact = st.session_state['email_contact']

        recipient_name = f"{contact['first_name']} {contact['last_name']}"
        recipient_role = st.text_input("Recipient Role", value="Recruiter")

        if st.button("✍️ Generate Draft"):
            with st.spinner("Drafting email..."):
                result = draft_email(recipient_name, recipient_role, contact['company'])

                if result:
                    st.session_state['draft'] = result

        if 'draft' in st.session_state:
            draft = st.session_state['draft']

            st.markdown("**Subject:**")
            subject = st.text_input("Edit subject:", value=draft.get('subject', ''), key="subject_edit")

            st.markdown("**Body:**")
            body = st.text_area("Edit body:", value=draft.get('body', ''), height=200, key="body_edit")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("📋 Copy Email"):
                    full_email = f"To: {contact['email']}\nSubject: {subject}\n\n{body}"
                    copy_to_clipboard(full_email)
                    st.success("✅ Copied to clipboard!")

            with col2:
                if st.button("📧 Open in Mail"):
                    import urllib.parse
                    mailto_link = f"mailto:{contact['email']}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                    open_url(mailto_link)
                    st.success("✅ Mail app opened!")


# ==================== ANSWER BANK PAGE ====================

elif page == "Answer Bank":
    st.title("Behavioral Answer Bank")

    st.markdown("""
    Store reusable answers to common behavioral questions.
    The AI will use these as a reference when generating custom answers.
    """)

    st.divider()

    # Load existing answers
    from frontend.utils import get_answers, save_answers

    answers = get_answers() or {}

    # Add new answer
    st.subheader("➕ Add New Answer")

    new_question = st.text_input("Question")
    new_answer = st.text_area("Your Answer (STAR format recommended)", height=150)

    if st.button("💾 Save Answer"):
        if new_question and new_answer:
            answers[new_question] = new_answer
            save_answers(answers)
            st.success("✅ Answer saved!")
            time.sleep(1)
            st.rerun()

    st.divider()

    # Display existing answers
    st.subheader("📚 Stored Answers")

    if answers:
        for question, answer in answers.items():
            with st.expander(question):
                st.write(answer)

                if st.button("🗑️ Delete", key=f"delete_{question}"):
                    del answers[question]
                    save_answers(answers)
                    st.rerun()
    else:
        st.info("No answers stored yet. Add your first one above!")


# ==================== SETTINGS PAGE ====================

elif page == "Settings":
    st.title("Settings")

    st.markdown("### API Configuration")
    st.info("Set your OpenAI API key in the `.env` file in the project root.")

    st.code("OPENAI_API_KEY=your-key-here")

    st.divider()

    st.markdown("### Raycast Snippets Setup")

    st.markdown("""
    **Set up these snippets in Raycast:**

    - `cmd+1` → Your full name
    - `cmd+2` → Email address
    - `cmd+3` → Phone number
    - `cmd+4` → LinkedIn URL
    - `cmd+5` → GitHub URL
    - `cmd+6` → Portfolio URL

    This lets you quickly fill forms while the bot handles the heavy lifting.
    """)

    st.divider()

    st.markdown("### System Info")
    st.write(f"**API Base:** {API_BASE}")
    st.write(f"**Data Directory:** `data/`")
    st.write(f"**Temp Directory:** `temp/`")

    if st.button("🧪 Test Backend Connection"):
        try:
            import requests
            response = requests.get(f"{API_BASE}/")
            if response.status_code == 200:
                st.success("✅ Backend is running!")
            else:
                st.error("❌ Backend returned error")
        except:
            st.error("❌ Cannot connect to backend. Make sure it's running on port 8000.")


# ==================== FOOTER ====================

st.divider()
st.caption("Applyr v1.0 - Built with Streamlit & FastAPI")
