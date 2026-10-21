"""Streamlit user interface. The UI calls FastAPI instead of reading SQLite."""

import json
from pathlib import Path

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
EXAMPLE_FILE = Path(__file__).resolve().parent / "data" / "new_tickets_example.json"

st.set_page_config(page_title="Support Ticket Assistant", page_icon="🎫", layout="wide")
st.title("🎫 Support Ticket Similarity Assistant")
st.write(
    "Find previously resolved support issues that may help with a new customer ticket. "
    "Suggestions are clues for the agent, not automatic answers to the customer."
)

# Check the backend early and explain what to do if it has not been started.
try:
    health = requests.get(f"{API_URL}/health", timeout=3)
    health.raise_for_status()
    st.caption("Backend status: connected to FastAPI")
except requests.RequestException:
    st.error("FastAPI is not running. Open a second terminal and run: uvicorn api:app --reload")
    st.stop()

with st.sidebar:
    st.header("Try an example")
    st.write("Load one of the four sample incoming tickets.")
    try:
        with EXAMPLE_FILE.open("r", encoding="utf-8") as file:
            examples = json.load(file).get("new_tickets", [])
        selected_example = st.selectbox(
            "Sample ticket", examples,
            format_func=lambda ticket: f"{ticket['ticket_id']} — {ticket['subject']}"
        )
        use_example = st.button("Load selected example", use_container_width=True)
    except (OSError, json.JSONDecodeError, KeyError):
        examples = []
        selected_example = None
        use_example = False

    st.divider()
    st.subheader("Matching setting")
    threshold = st.slider(
        "Minimum similarity", min_value=0.0, max_value=0.30,
        value=0.08, step=0.01,
        help="Higher means fewer, stricter suggestions. Lower means more suggestions, including weaker ones."
    )
    result_limit = st.number_input("Maximum results", min_value=1, max_value=10, value=3)

# Keep the text fields in session state so the example button can fill them in.
if "subject" not in st.session_state:
    st.session_state.subject = ""
if "description" not in st.session_state:
    st.session_state.description = ""
if use_example and selected_example:
    st.session_state.subject = selected_example.get("subject", "")
    st.session_state.description = selected_example.get("description", "")

st.subheader("New incoming ticket")
subject = st.text_input("Subject", key="subject", placeholder="Example: Password reset email never arrives")
description = st.text_area(
    "Description", key="description", height=130,
    placeholder="Describe what the customer reported and what they have tried."
)

if st.button("Find similar tickets", type="primary"):
    if not subject.strip() or not description.strip():
        st.warning("Enter both a subject and a description before searching.")
    else:
        try:
            response = requests.post(
                f"{API_URL}/search",
                json={
                    "subject": subject,
                    "description": description,
                    "limit": int(result_limit),
                    "threshold": threshold,
                },
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()

            st.subheader("Search result")
            st.write(result["message"])
            st.caption(f"Compared against {result['historical_ticket_count']} historical tickets.")

            if not result["match_found"]:
                st.info("No result passed the minimum similarity setting. Do not force a match; investigate as a new issue.")
            else:
                for match in result["matches"]:
                    score_percent = int(match["similarity_score"] * 100)
                    with st.expander(
                        f"{match['ticket_id']} — {match['subject']} | Similarity: {score_percent}%",
                        expanded=True,
                    ):
                        st.write("**Original issue**")
                        st.write(match["description"])
                        st.write("**What resolved it**")
                        st.write(match["resolution_notes"] or "No resolution notes were recorded.")
                        st.write(f"**Category:** {match['category']}")
                        st.write("**Words in common:** " + (", ".join(match["shared_terms"]) or "None listed"))
                        st.caption("Similarity is a simple word-overlap score, not a probability of being the same issue.")
        except requests.RequestException as error:
            st.error(f"Could not contact the API: {error}")

st.divider()
st.subheader("Historical ticket store")
if st.button("Show historical ticket count"):
    try:
        tickets_response = requests.get(f"{API_URL}/tickets", timeout=5)
        tickets_response.raise_for_status()
        tickets_data = tickets_response.json()
        st.success(f"SQLite currently contains {tickets_data['count']} historical tickets.")
        st.dataframe(
            [
                {"Ticket ID": ticket["ticket_id"], "Subject": ticket["subject"],
                 "Category": ticket["category"], "Created": ticket["created_date"]}
                for ticket in tickets_data["tickets"]
            ],
            use_container_width=True,
        )
    except requests.RequestException as error:
        st.error(f"Could not load historical tickets: {error}")
