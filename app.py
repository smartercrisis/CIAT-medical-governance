import streamlit as st
import json
from datetime import datetime

# ==========================================
# 1. MUST BE THE VERY FIRST STREAMLIT COMMAND
# ==========================================
st.set_page_config(
    page_title="CIAT Medical Governance Engine",
    page_layout="wide"
)

# ==========================================
# 2. APPLICATION HEADER & DESCRIPTION
# ==========================================
st.title("CHIMERA CIAT: Medical Content Governance Engine")
st.markdown("### Execution Layer & Deterministic Validation Gate")

# ==========================================
# 3. SESSION STATE INITIALIZATION
# ==========================================
if "phase" not in st.session_state:
    st.session_state.phase = 0
if "identity_confirmed" not in st.session_state:
    st.session_state.identity_confirmed = False
if "audit_log" not in st.session_state:
    st.session_state.audit_log = {}

# ==========================================
# 4. SIDEBAR: PRACTITIONER IDENTITY CONTRACT (OBJECT 1)
# ==========================================
st.sidebar.header("Phase 0: Identity & Source Lock")
practitioner_name = st.sidebar.text_input("Practitioner Full Name", value="Dr. ")
professional_title = st.sidebar.text_input("Professional Title", value="Consultant / GP")
license_type = st.sidebar.selectbox("License Type", ["Doctor", "Pharmacist", "Medical_Content_Specialist"])
specialty = st.sidebar.text_input("Specialty", value="General Practice")
platform = st.sidebar.selectbox("Target Platform", ["Instagram", "LinkedIn", "Patient Handout", "Website"])

uploaded_sources = st.sidebar.file_uploader("Upload Tier 1/2 Source Documents (PDF/TXT)", accept_multiple_files=True)

if st.sidebar.button("Lock Identity & Sources (Phase 0)"):
    if practitioner_name and len(uploaded_sources) > 0:
        st.session_state.phase = 1
        st.success("Source Hierarchy Lock confirmed. Clinical governance active.")
    else:
        st.error("Phase 0 failed: Practitioner name and at least one source document are required.")

# ==========================================
# 5. MAIN WORKFLOW INTERFACE (PHASE 1 & 2)
# ==========================================
if st.session_state.phase >= 1:
    st.markdown("---")
    st.header("Phase 1 & 2: Claim Validation & Tier Scanning")
    
    content_draft = st.text_area("Paste Content Draft for Governance Scan", height=150)
    
    if st.button("Run Deterministic Claim Audit"):
        st.warning("Scanning text against Five-Tier Source Hierarchy...")
        
        # Mock audit findings for demonstration
        st.session_state.flags = [
            {"id": 1, "sentence": "Reduces chronic hypertension within 48 hours completely.", "category": "TIER_5_UNVERIFIED_SOURCE"},
            {"id": 2, "sentence": "Safe to stop prescription medication if symptoms subside.", "category": "SELF_TREATMENT_RISK"}
        ]
        st.session_state.phase = 3

# ==========================================
# 6. PHASE 3: PRACTITIONER IDENTITY GATE (OBJECT 5)
# ==========================================
if st.session_state.phase >= 3:
    st.markdown("---")
    st.header("Phase 3: Human-in-the-Loop Practitioner Identity Gate")
    st.info("Phase 3 cannot be completed by a content manager, assistant, or AI tool.")
    
    auth_check = st.checkbox(f"I verify that I am {practitioner_name}, licensed as a {license_type}, and personally reviewing these flags.")
    
    if auth_check:
        st.session_state.identity_confirmed = True
        st.markdown("### Flag Resolution Interface")
        
        resolutions = {}
        for flag in st.session_state.get("flags", []):
            st.write(f"**Flag #{flag['id']} [{flag['category']}]**: *{flag['sentence']}*")
            action = st.selectbox(f"Instruction for Flag #{flag['id']}", ["REMOVE", "REWRITE", "SOURCE", "APPROVE_WITH_DISCLOSURE"], key=f"act_{flag['id']}")
            input_text = st.text_input(f"Practitioner Input / Correction for #{flag['id']}", key=f"inp_{flag['id']}")
            resolutions[flag['id']] = {"action": action, "input": input_text}
            
        if st.button("Generate Correction Audit Log (Object 6)"):
            audit_log = {
                "document_id": f"CIAT-MED-{datetime.utcnow().strftime('%Y%m%d')}-{platform}",
                "practitioner_name": practitioner_name,
                "license_type": license_type,
                "specialty": specialty,
                "phase_gates_passed": ["Phase_1", "Phase_2", "Phase_3"],
                "resolutions": resolutions,
                "audit_trail_complete": True,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            st.session_state.audit_log = audit_log
            st.session_state.phase = 4
            st.success("Audit log generated successfully.")

# ==========================================
# 7. PHASE 4: CLINICAL SOVEREIGNTY GATE (OBJECT 6)
# ==========================================
if st.session_state.phase == 4:
    st.markdown("---")
    st.header("Phase 4: Clinical Sovereignty Gate & Scorecard")
    
    p1_score = st.slider("Pillar 1: Clinical Accuracy (Prompts 01, 02)", 0, 10, 9)
    p2_score = st.slider("Pillar 2: Patient Safety (Prompt 03)", 0, 10, 10)
    p3_score = st.slider("Pillar 3: Ethics & Compliance (Prompt 04)", 0, 10, 9)
    p4_score = st.slider("Pillar 4: Professional Accountability (Prompts 05, 06)", 0, 10, 9)
    
    total_score = p1_score + p2_score + p3_score + p4_score
    st.metric("Medical Content Integrity Score", f"{total_score} / 40")
    
    if total_score >= 36 and st.session_state.audit_log.get("audit_trail_complete", False):
        st.success("SOVEREIGN - APPROVED FOR PUBLICATION")
        st.json(st.session_state.audit_log)
    elif 28 <= total_score <= 35:
        st.warning("CLINICAL REVIEW REQUIRED - Return to flagged prompts.")
    else:
        st.error("DO NOT PUBLISH - Score below threshold or audit trail incomplete.")
