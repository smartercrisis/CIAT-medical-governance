import streamlit as st
import json
import hashlib
import hmac
import os
from datetime import datetime

st.set_page_config(page_title="CIAT Medical Governance Engine", layout="wide")
st.title("CIAT Medical Governance Engine")

def load_schema(filename):
    path = os.path.join("schemas", filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def compute_sha256(data_dict):
    encoded = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

# Load exact schemas from repository
schema_identity = load_schema("CIAT_Practitioner_Identity_Context.json")
schema_hierarchy = load_schema("CIAT_Source_Hierarchy_Schema.json")
schema_phase1 = load_schema("CIAT_Phase1_Gate.json")
schema_phase2 = load_schema("CIAT_Phase2_Gate.json")
schema_phase3 = load_schema("CIAT_Phase3_Practitioner_Gate.json")
schema_phase4 = load_schema("CIAT_Phase4_Clinical_Sovereign.json")

# Phase 0: Identity Lock
st.sidebar.header("Practitioner & System Identity")
practitioner_id = st.sidebar.text_input("Practitioner ID", value="PRACTITIONER-01")
license_key = st.sidebar.text_input("License Key", value="LIC-SECURE-2026", type="password")

# Document Ingestion Engine
st.header("Manuscript Ingestion")
uploaded_file = st.file_uploader("Upload Medical Manuscript (.txt, .md)", type=["txt", "md"])

if uploaded_file is not None:
    raw_text = uploaded_file.read().decode("utf-8")
    st.info(f"Ingested File: {uploaded_file.name} | {len(raw_text)} characters | {len(raw_text.split())} words")

    if st.button("Execute Governance Pipeline"):
        doc_id = f"CIAT-DOC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        # 1. Identity & Context Payload
        identity_payload = {
            "practitioner_id": practitioner_id,
            "session_id": f"SESS-{hashlib.md5(timestamp.encode()).hexdigest()[:8]}",
            "timestamp_utc": timestamp
        }
        hash_identity = compute_sha256(identity_payload)

        # 2. Source Hierarchy & Ingestion Payload
        hierarchy_payload = {
            "document_id": doc_id,
            "file_name": uploaded_file.name,
            "raw_text": raw_text
        }
        hash_hierarchy = compute_sha256(hierarchy_payload)

        # 3. Phase 1 Gate Audit
        phase1_payload = {
            "document_id": doc_id,
            "status": "INGESTED",
            "character_count": len(raw_text)
        }
        hash_phase1 = compute_sha256(phase1_payload)

        # 4. Phase 2 Gate (Claim Detection & Filtering)
        prohibited_terms = ["guaranteed", "100% cure", "instant result", "unverified"]
        flagged = [term for term in prohibited_terms if term in raw_text.lower()]
        
        phase2_payload = {
            "document_id": doc_id,
            "flagged_claims": flagged,
            "violation_count": len(flagged)
        }
        hash_phase2 = compute_sha256(phase2_payload)

        # 5. Phase 3 Practitioner Gate (Sanitization)
        sanitized_text = raw_text
        for term in flagged:
            sanitized_text = sanitized_text.replace(term, f"[FLAGGED: {term}]")

        phase3_payload = {
            "document_id": doc_id,
            "sanitized_payload": sanitized_text,
            "actions_taken": ["STRIPPED" if flagged else "NONE"]
        }
        hash_phase3 = compute_sha256(phase3_payload)

        # 6. Phase 4 Clinical Sovereign Output (Cryptographic Signature)
        master_string = f"{hash_identity}{hash_hierarchy}{hash_phase1}{hash_phase2}{hash_phase3}"
        sig = hmac.new(license_key.encode('utf-8'), master_string.encode('utf-8'), hashlib.sha256).hexdigest()

        phase4_payload = {
            "document_id": doc_id,
            "practitioner_id": practitioner_id,
            "timestamp_utc": timestamp,
            "hash_chain": {
                "identity_context_hash": hash_identity,
                "source_hierarchy_hash": hash_hierarchy,
                "phase1_gate_hash": hash_phase1,
                "phase2_gate_hash": hash_phase2,
                "phase3_practitioner_gate_hash": hash_phase3
            },
            "hmac_sha256_signature": sig,
            "verification_status": "PASSED" if not flagged else "REJECTED"
        }

        # Results Display
        st.success("Pipeline Execution Complete.")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Phase 4 Clinical Sovereign Ledger")
            st.json(phase4_payload)

        with col2:
            st.subheader("Sanitized Output Document")
            st.text_area("Sanitized Payload", sanitized_text, height=300)

        # Full Master Audit Bundle Export
        master_bundle = {
            "CIAT_Practitioner_Identity_Context": identity_payload,
            "CIAT_Source_Hierarchy_Schema": hierarchy_payload,
            "CIAT_Phase1_Gate": phase1_payload,
            "CIAT_Phase2_Gate": phase2_payload,
            "CIAT_Phase3_Practitioner_Gate": phase3_payload,
            "CIAT_Phase4_Clinical_Sovereign": phase4_payload
        }

        st.download_button(
            label="Download Master Audit Certificate (JSON)",
            data=json.dumps(master_bundle, indent=2),
            file_name=f"{doc_id}_master_audit.json",
            mime="application/json"
        )
