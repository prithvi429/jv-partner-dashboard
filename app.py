"""
Streamlit UI for JV Partner Identification Dashboard (Plotly-Free Version - Fixed Forms).
Guided 7-step workflow via tabs. Uses Streamlit charts.
Forms fixed: No buttons inside forms; research/enrich buttons outside.
Run: streamlit run app.py
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GOOGLE_SEARCH_KEY = os.getenv("GOOGLE_SEARCH_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Session state for workflow progress and mock data
if 'step_progress' not in st.session_state:
    st.session_state.step_progress = {
        'products': False, 'companies': False, 'stakeholders': False,
        'outreach': False, 'meetings': False, 'deals': False
    }
if 'data_store' not in st.session_state:
    st.session_state.data_store = {
        'products': [], 'companies': [], 'stakeholders': [], 'outreaches': [],
        'meetings': [], 'deals': []
    }
if 'gmail_connected' not in st.session_state:
    st.session_state.gmail_connected = False

# Helper: API call to backend (fallback to session state if backend not ready)
@st.cache_data(ttl=300)
def api_call(endpoint, method="GET", json_data=None):
    try:
        url = f"{BACKEND_URL}/api/v1{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=json_data)
        elif method == "PUT":
            response = requests.put(url, json=json_data)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        # Fallback to session state for MVP (no backend dependency)
        if method == "GET" and endpoint == "/products":
            return st.session_state.data_store['products']
        # Add more fallbacks as needed
        st.warning("Backend not available; using local mock data.")
        return []

# Helper: Google Custom Search for product research
def research_product_on_google(query):
    if not GOOGLE_SEARCH_KEY or not GOOGLE_CSE_ID:
        st.warning("Google Search API not configured in .env (add GOOGLE_SEARCH_KEY and GOOGLE_CSE_ID).")
        return []
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": GOOGLE_SEARCH_KEY, "cx": GOOGLE_CSE_ID, "q": query}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        items = response.json().get("items", [])
        return [item["snippet"] for item in items[:5]]
    except Exception as e:
        st.error(f"Google Search Error: {e}")
        return []

# Helper: Auto-enrich company (mock + Hunter if available)
def enrich_company(company_name):
    enriched = {"size": "medium", "revenue": "$10M", "domain": f"{company_name.lower().replace(' ', '')}.com"}
    try:
        from services.hunter_service import search_domain_emails
        hunter_data = search_domain_emails(enriched["domain"])
        if "data" in hunter_data and hunter_data["data"]:
            enriched["emails"] = [e["value"] for e in hunter_data["data"][:3]]
    except ImportError:
        st.info("Hunter service not available; using mock enrichment.")
    st.success("Company enriched! 👇")
    return enriched

# Helper: Verify stakeholder email (Hunter if available)
def verify_stakeholder_email(email):
    try:
        from services.hunter_service import verify_email
        result = verify_email(email)
        status = "✅ Deliverable" if result.get("result") == "deliverable" else "❌ Undeliverable"
        return status, result
    except ImportError:
        return "⚠️ Hunter not set up (mock: Valid)", {"result": "deliverable"}

# Helper: Connect Gmail (triggers OAuth if available)
def connect_gmail():
    if not st.session_state.gmail_connected:
        st.info("Click 'Test Send' in Outreach tab to connect Gmail (requires credentials.json).")
    try:
        from services.gmail_service import get_gmail_service
        service = get_gmail_service()
        st.session_state.gmail_connected = True
        st.success("Gmail connected! ✅")
    except ImportError:
        st.warning("Gmail service not set up; emails will be mocked.")
    except Exception as e:
        st.error(f"Gmail Connection Error: {e}")

# Helper: AI Outreach (OpenAI if available, else mock)
def generate_ai_outreach(stakeholder_name, company_name, product_name):
    try:
        from services.openai_service import generate_ai_email
        return generate_ai_email(stakeholder_name, company_name, product_name)
    except ImportError:
        return f"Dear {stakeholder_name},\n\nWe're excited about potential JV opportunities with {company_name} regarding our {product_name} technology.\n\nLet's discuss how we can collaborate.\n\nBest regards,\nYour JV Team"

# Sidebar: Navigation & Progress
st.sidebar.title("JV Workflow Progress")
progress_value = sum(st.session_state.step_progress.values()) / 6
st.sidebar.progress(progress_value)
for step, complete in st.session_state.step_progress.items():
    st.sidebar.checkbox(f"{step.title()}", value=complete, disabled=True)

# Main Title
st.title("🛡️ Joint Venture Partner Identification Dashboard")
st.markdown("Guided 7-Step Workflow: Follow the tabs to identify and engage JV partners.")

# Tabs for Steps
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["1. Products", "2. Companies", "3. Stakeholders", "4. Outreach", "5. Meetings", "6. Deals", "7. Analytics"])

with tab1:
    st.header("Step 1: Research & Add Products/Technologies")
    if not st.session_state.step_progress['products']:
        # Standalone Research Button (OUTSIDE form)
        research_query = st.text_input("Research Query (e.g., 'AI manufacturing tech')")
        if st.button("Research on Google"):
            results = research_product_on_google(research_query)
            if results:
                st.subheader("Research Results:")
                for result in results:
                    st.write(f"• {result}")
            else:
                st.info("No results found or API not configured.")

        # Form for Adding Product (button inside form only)
        with st.form("add_product"):
            name = st.text_input("Product Name", placeholder="e.g., AI Manufacturing Tech")
            description = st.text_area("Description", placeholder="Brief overview...")
            market_alignment = st.selectbox("Market Alignment", ["high", "medium", "low"])
            revenue_potential = st.text_input("Revenue Potential (e.g., $1M)")
            submitted = st.form_submit_button("Add Product")
            if submitted and name:
                new_product = {
                    "id": len(st.session_state.data_store['products']) + 1,
                    "name": name, "description": description,
                    "market_alignment": market_alignment, "revenue_potential": revenue_potential
                }
                st.session_state.data_store['products'].append(new_product)
                st.session_state.step_progress['products'] = True
                st.success("Product added! Next step unlocked. 🚀")
                st.rerun()
    else:
        st.success("✅ Products complete. View data below.")
    # Display products
    products = api_call("/products")  # Or from session state
    if products:
        st.dataframe(pd.DataFrame(products))

with tab2:
    st.header("Step 2: Identify & Enrich Companies")
    if st.session_state.step_progress['products']:
        # Standalone Enrich Button
        company_name_input = st.text_input("Company Name for Enrichment")
        if st.button("Enrich Company"):
            if company_name_input:
                enriched = enrich_company(company_name_input)
                st.json(enriched)
            else:
                st.warning("Enter a company name first.")

        # Form for Adding Company
        with st.form("add_company"):
            name = st.text_input("Company Name", placeholder="e.g., Tech Corp")
            industry = st.text_input("Industry", placeholder="e.g., Manufacturing")
            size = st.selectbox("Size", ["small", "medium", "large"])
            revenue = st.text_input("Revenue", placeholder="e.g., $10M")
            submitted = st.form_submit_button("Add Company")
            if submitted and name:
                new_company = {
                    "id": len(st.session_state.data_store['companies']) + 1,
                    "name": name, "industry": industry, "size": size, "revenue": revenue
                }
                st.session_state.data_store['companies'].append(new_company)
                st.session_state.step_progress['companies'] = True
                st.success("Company added & enriched! 👇")
                st.rerun()
    else:
        st.warning("Complete Products first.")
    # Display companies
    companies = api_call("/companies")
    if companies:
        st.dataframe(pd.DataFrame(companies))

with tab3:
    st.header("Step 3: Add & Verify Stakeholders")
    if st.session_state.step_progress['companies']:
        # Standalone Verify Button
        email_input = st.text_input("Email for Verification")
        linkedin_url = st.text_input("LinkedIn URL (optional)")
        if st.button("Verify Email & Enrich LinkedIn"):
            if email_input:
                status, result = verify_stakeholder_email(email_input)
                st.write(f"**Email Status:** {status}")
                if linkedin_url:
                    try:
                        from services.linkedin_service import fetch_profile
                        profile_data = fetch_profile(linkedin_url)
                        st.json(json.loads(profile_data) if profile_data else {"error": "No data"})
                    except ImportError:
                        st.info("LinkedIn service not available.")
            else:
                st.warning("Enter an email first.")

        # Form for Adding Stakeholder
        with st.form("add_stakeholder"):
            company_name = st.selectbox("Company", [c["name"] for c in st.session_state.data_store.get('companies', [])])
            name = st.text_input("Name", placeholder="e.g., John Doe")
            title = st.text_input("Title", placeholder="e.g., CEO")
            email = st.text_input("Email", placeholder="e.g., john@company.com")
            phone = st.text_input("Phone", placeholder="e.g., 123-456-7890")
            role = st.selectbox("Role", ["decision-maker", "influencer", "technical"])
            submitted = st.form_submit_button("Add Stakeholder")
            if submitted and name and email:
                status, _ = verify_stakeholder_email(email)
                new_stakeholder = {
                    "id": len(st.session_state.data_store['stakeholders']) + 1,
                    "name": name, "title": title, "email": email, "phone": phone,
                    "role": role, "company": company_name, "email_status": status
                }
                st.session_state.data_store['stakeholders'].append(new_stakeholder)
                st.success(f"Stakeholder added! Email: {status}")
                st.rerun()
    else:
        st.warning("Complete Companies first.")
    # Display stakeholders
    stakeholders = api_call("/stakeholders")
    if stakeholders:
        for s in stakeholders:
            st.write(f"**{s.get('name', '')}** ({s.get('title', '')}) - {s.get('email_status', 'Unknown')}")

with tab4:
    st.header("Step 4: Outreach & AI Assistance")
    connect_gmail()
    if st.session_state.step_progress['stakeholders'] and st.session_state.gmail_connected:
        # Standalone AI Generate Button
        stakeholder_name = st.selectbox("Stakeholder", [s["name"] for s in st.session_state.data_store.get('stakeholders', [])])
        product_name = st.text_input("Related Product", placeholder="e.g., AI Tech")
        if st.button("Generate AI Email"):
            if stakeholder_name and product_name:
                stakeholder = next((s for s in st.session_state.data_store.get('stakeholders', []) if s["name"] == stakeholder_name), {})
                company_name = stakeholder.get("company", "Unknown Co")
                email_body = generate_ai_outreach(stakeholder_name, company_name, product_name)
                st.text_area("AI-Generated Email", email_body, height=200, key="ai_email")
            else:
                st.warning("Select stakeholder and product first.")

        # Form for Sending Outreach
        with st.form("add_outreach"):
            message = st.text_area("Custom Message (or use AI above)", height=150)
            submitted = st.form_submit_button("Send Outreach")
            if submitted and message:
                # Mock send
                try:
                    from services.gmail_service import send_email
                    stakeholder = next((s for s in st.session_state.data_store.get('stakeholders', []) if s["name"] == stakeholder_name), {})
                    to_email = stakeholder.get("email", "")
                    subject = f"JV Opportunity: {product_name}"
                    if send_email(to_email, subject, message):
                        new_outreach = {"id": len(st.session_state.data_store['outreaches']) + 1, "message": message, "stakeholder": stakeholder_name}
                        st.session_state.data_store['outreaches'].append(new_outreach)
                        st.session_state.step_progress['outreach'] = True
                        st.success("Outreach sent! 📧")
                        st.rerun()
                    else:
                        st.error("Failed to send email.")
                except Exception as e:
                    st.error(f"Send Error: {e} (Mock sent for demo).")
                    # Still "send" for demo
                    st.session_state.step_progress['outreach'] = True
                    st.rerun()
    else:
        st.warning("Complete Stakeholders and connect Gmail first.")
    # Display outreaches with classification
    outreaches = st.session_state.data_store.get('outreaches', [])
    for o in outreaches:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**To:** {o['stakeholder']}")
        with col2:
            response_text = st.text_input("Response Text", key=f"resp_{o['id']}")
        if st.button("Classify Response (AI)", key=f"class_{o['id']}") and response_text:
            try:
                from services.openai_service import classify_response
                classification = classify_response(response_text)
                st.success(f"AI Classification: {classification}")
            except ImportError:
                st.success("AI Classification: Mock - Interested")

with tab5:
    st.header("Step 5: Schedule Meetings")
    if st.session_state.step_progress['outreach']:
        # Form for Adding Meeting
        with st.form("add_meeting"):
            outreach_stakeholder = st.selectbox("From Outreach", [o["stakeholder"] for o in st.session_state.data_store.get('outreaches', [])])
            scheduled_date = st.date_input("Scheduled Date")
            participants = st.text_input("Participants", placeholder="e.g., John Doe, Team Lead")
            agenda = st.text_area("Agenda", placeholder="Discuss JV opportunities...")
            submitted = st.form_submit_button("Schedule Meeting")
            if submitted:
                new_meeting = {
                    "id": len(st.session_state.data_store['meetings']) + 1,
                    "stakeholder": outreach_stakeholder, "date": scheduled_date.isoformat(),
                    "participants": participants, "agenda": agenda
                }
                st.session_state.data_store['meetings'].append(new_meeting)
                st.success("Meeting scheduled! (Calendly link would appear here in full integration.)")
                st.session_state.step_progress['meetings'] = True
                st.rerun()
    else:
        st.warning("Complete Outreach first.")
    # Display meetings
    meetings = api_call("/meetings")
    if meetings:
        st.dataframe(pd.DataFrame(meetings))

with tab6:
    st.header("Step 6: Deal Pipeline (Kanban View)")
    if st.session_state.step_progress['meetings']:
        # Mock deals if none
        if not st.session_state.data_store['deals']:
            st.session_state.data_store['deals'] = [{"id": 1, "stage": "intro", "notes": "Test Deal from Meeting", "assigned_to": "user@example.com"}]
        deals = st.session_state.data_store['deals']
        df = pd.DataFrame(deals)
        if not df.empty:
            col1, col2, col3, col4 = st.columns