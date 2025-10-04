import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="JV Partner Dashboard", layout="wide")
st.title("JV Partner Dashboard — Demo UI")

st.markdown("Interact with the backend to view and create deals.")

with st.expander("Create a deal"):
    name = st.text_input("Deal Name", "New Partnership")
    company = st.text_input("Company", "Example Co")
    product = st.text_input("Product", "Referral Program")
    value = st.number_input("Value (USD)", min_value=0.0, value=1000.0)
    if st.button("Create Deal"):
        payload = {
            "name": name,
            "company_name": company,
            "product_name": product,
            "value": value,
        }
        try:
            resp = requests.post(f"{API_URL}/deals/", json=payload, timeout=5)
            resp.raise_for_status()
            st.success("Deal created")
            st.json(resp.json())
        except Exception as e:
            st.error(f"Failed to create deal: {e}")

st.markdown("---")

if st.button("Refresh deals"):
    try:
        resp = requests.get(f"{API_URL}/deals/", timeout=5)
        resp.raise_for_status()
        deals = resp.json()
        st.write(f"Found {len(deals)} deals")
        for d in deals:
            st.card = st.expander(f"{d.get('name')} — {d.get('company_name')}")
            with st.card:
                st.write(d)
    except Exception as e:
        st.error(f"Failed to fetch deals: {e}")

st.info("Backend used: %s" % API_URL)
