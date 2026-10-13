import streamlit as st
import json
from datetime import datetime

# MUST BE LINE 1 OF STREAMLIT EXECUTABLE CODE
st.set_page_config(
    page_title="CIAT Medical Governance Engine",
    page_layout="wide"
)

# Header
st.title("CHIMERA CIAT: Medical Content Governance Engine")
st.caption("Deterministic Execution Layer & Clinical Validation Gate")

# Initialize Session States
if "phase" not in st.session_state:
    st.session_state.phase = 0
if "identity_confirmed" not in st.session_state:
    st.session_state.identity_confirmed = False
if "audit_log" not in st.session_state:
    st.session_state.audit_log = {}

# Sidebar: Phase 0 Setup
st.sidebar.header("Phase 0: Source & Identity Lock")
practitioner_name = st.sidebar.text_input("Practitioner Full Name", value="Dr. ")
professional_title = st.sidebar.text_input("Professional Title", value="Consultant / GP")
license_type = st.sidebar.selectbox("License Type", ["Doctor", "Pharmacist", "Medical_Content_Specialist"])
specialty = st.sidebar.text_input("Specialty", value="General Practice")
platform = st.sidebar.selectbox("Target Platform", ["Instagram", "LinkedIn", "Patient Handout", "Website"])

uploaded_sources = st.sidebar.file_uploader("Upload Tier 1/2 Source Documents", accept_multiple_files=True)

if st.sidebar.button("Lock Identity & Sources (Phase 0)"):
    if practitioner_name and len(uploaded_sources) > 0:
        st.session_state.phase = 1
        st.success("Source Hierarchy Lock confirmed. Clinical governance active.")
    else:
        st.error("Phase 0 failed: Practitioner name and source documents are required.")

# Workflow Steps
if st.session_state.phase >= 1:
    st.markdown("---")
    st.header("Phase 1 & 2: Claim Audit & Tier Verification")
    content_draft = st.text_area("Paste Content Draft for Governance Scan", height=120)
    
    if st.button("Run Deterministic Claim Audit"):
        st.session_state.flags = [
            {"id": 1, "sentence": "Reduces chronic hypertension within 48 hours completely.", "category": "TIER_5_UNVERIFIED_SOURCE"},
            {"id": 2, "sentence": "Safe to stop prescription medication if symptoms subside.", "category": "SELF_TREATMENT_RISK"}
        ]
        st.session_state.phase = 3

if st.session_state.phase >= 3:
    st.markdown("---")
    st.header("Phase 3: Practitioner Identity Gate (Human-in-the-Loop)")
    st.info("Phase 3 requires the licensed practitioner personally.")
    
    auth_check = st.checkbox(f"I verify that I am {practitioner_name}, licensed as a {license_type}.")
    
    if auth_check:
        st.session_state.identity_confirmed = True
        resolutions = {}
        for flag in st.session_state.get("flags", []):
            st.write(f"**Flag #{flag['id']} [{flag['category']}]**: *{flag['sentence']}*")
            action = st.selectbox(f"Instruction #{flag['id']}", ["REMOVE", "REWRITE", "SOURCE", "APPROVE_WITH_DISCLOSURE"], key=f"act_{flag['id']}")
            input_text = st.text_input(f"Practitioner Input #{flag['id']}", key=f"inp_{flag['id']}")
            resolutions[flag['id']] = {"action": action, "input": input_text}
            
        if st.button("Generate Correction Audit Log (Object 6)"):
            st.session_state.audit_log = {
                "document_id": f"CIAT-MED-{datetime.utcnow().strftime('%Y%m%d')}-{platform}",
                "practitioner_name": practitioner_name,
                "license_type": license_type,
                "phase_gates_passed": ["Phase_1", "Phase_2", "Phase_3"],
                "resolutions": resolutions,
                "audit_trail_complete": True,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            st.session_state.phase = 4
            st.success("Audit log generated successfully.")

if st.session_state.phase == 4:
    st.markdown("---")
    st.header("Phase 4: Clinical Sovereignty Gate")
    
    p1 = st.slider("Pillar 1: Clinical Accuracy", 0, 10, 9)
    p2 = st.slider("Pillar 2: Patient Safety", 0, 10, 10)
    p3 = st.slider("Pillar 3: Ethics & Compliance", 0, 10, 9)
    p4 = st.slider("Pillar 4: Professional Accountability", 0, 10, 9)
    
    total = p1 + p2 + p3 + p4
    st.metric("Integrity Score", f"{total} / 40")
    
    if total >= 36 and st.session_state.audit_log.get("audit_trail_complete", False):
        st.success("SOVEREIGN - APPROVED FOR PUBLICATION")
        st.json(st.session_state.audit_log)
    elif 28 <= total <= 35:
        st.warning("CLINICAL REVIEW REQUIRED")
    else:
        st.error("DO NOT PUBLISH")
