import streamlit as st
import json
import hashlib
import hmac
import os
from datetime import datetime

st.set_page_config(page_title="CIAT Medical Governance Engine", layout="wide")
st.title("CIAT Medical Governance Engine")

def compute_sha256(data_dict):
    encoded = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

# Sidebar: Operator Config
st.sidebar.header("Practitioner Identity")
practitioner_id = st.sidebar.text_input("Practitioner ID", value="PRACTITIONER-01")
license_key = st.sidebar.text_input("License Key", value="LIC-SECURE-2026", type="password")

# 1. Load Anchor File
st.header("1. Medical Anchor Standard")
default_anchor_path = os.path.join("schemas", "anchor_standard.json")
anchor_data = None

uploaded_anchor = st.file_uploader("Upload Custom Anchor (.json)", type=["json"])

if uploaded_anchor is not None:
    anchor_data = json.load(uploaded_anchor)
    st.success(f"Custom Anchor Loaded: {uploaded_anchor.name}")
elif os.path.exists(default_anchor_path):
    with open(default_anchor_path, "r") as f:
        anchor_data = json.load(f)
    st.info("Loaded System Anchor: FDA/ICMJE/HIPAA Combined Framework")

# 2. Input Manuscript Content
st.header("2. Target Manuscript Text")
user_content = st.text_area("Paste manuscript or trial draft text here...", height=250)

if anchor_data and user_content.strip():
    if st.button("Execute Governance Audit"):
        doc_id = f"CIAT-DOC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Object 1: Identity Context
        obj1_identity = {
            "practitioner_id": practitioner_id,
            "session_id": f"SESS-{hashlib.md5(timestamp.encode()).hexdigest()[:8]}",
            "timestamp_utc": timestamp
        }
        hash1 = compute_sha256(obj1_identity)

        # Object 2: Source Hierarchy
        obj2_hierarchy = {
            "document_id": doc_id,
            "anchor_title": anchor_data.get("title", "Unknown Anchor"),
            "anchor_version": anchor_data.get("version", "1.0"),
            "content_length": len(user_content),
            "content_hash": hashlib.sha256(user_content.encode()).hexdigest()
        }
        hash2 = compute_sha256(obj2_hierarchy)

        # Audit Execution: Match text against anchor mandates
        detected_violations = []
        user_text_lower = user_content.lower()

        for mandate in anchor_data.get("regulatory_mandates", []):
            for pattern in mandate.get("trigger_patterns", []):
                if pattern in user_text_lower:
                    detected_violations.append({
                        "rule_id": mandate["rule_id"],
                        "reference": mandate["regulatory_reference"],
                        "category": mandate["category"],
                        "severity": mandate["severity"],
                        "flagged_term": pattern
                    })

        # Object 3: Phase 1 Gate
        obj3_gate1 = {
            "document_id": doc_id,
            "mandates_evaluated": len(anchor_data.get("regulatory_mandates", [])),
            "status": "INGESTED"
        }
        hash3 = compute_sha256(obj3_gate1)

        # Object 4: Phase 2 Gate
        obj4_gate2 = {
            "document_id": doc_id,
            "total_violations": len(detected_violations),
            "violations_matrix": detected_violations
        }
        hash4 = compute_sha256(obj4_gate2)

        # Object 5: Phase 3 Practitioner Gate
        sanitized_content = user_content
        for v in detected_violations:
            term = v["flagged_term"]
            sanitized_content = sanitized_content.replace(term, f"[VIOLATION-{v['rule_id']}: {term}]")

        obj5_gate3 = {
            "document_id": doc_id,
            "sanitized_payload": sanitized_content,
            "modifications_count": len(detected_violations)
        }
        hash5 = compute_sha256(obj5_gate3)

        # Object 6: Clinical Sovereign HMAC Ledger
        master_chain = f"{hash1}{hash2}{hash3}{hash4}{hash5}"
        sig = hmac.new(license_key.encode('utf-8'), master_chain.encode('utf-8'), hashlib.sha256).hexdigest()

        obj6_sovereign = {
            "document_id": doc_id,
            "practitioner_id": practitioner_id,
            "timestamp_utc": timestamp,
            "hash_chain": {
                "identity_context_hash": hash1,
                "source_hierarchy_hash": hash2,
                "phase1_gate_hash": hash3,
                "phase2_gate_hash": hash4,
                "phase3_practitioner_gate_hash": hash5
            },
            "hmac_sha256_signature": sig,
            "verification_status": "PASSED" if not detected_violations else "REJECTED"
        }

        # Results Display
        st.success("Audit Complete.")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Clinical Sovereign Ledger (Object 6)")
            st.json(obj6_sovereign)
            st.subheader("Regulatory Violations Breakdown")
            st.json(obj4_gate2)

        with col2:
            st.subheader("Sanitized Manuscript Output")
            st.text_area("Output Payload", sanitized_content, height=350)

        # Download Master Certificate
        master_export = {
            "CIAT_Practitioner_Identity_Context": obj1_identity,
            "CIAT_Source_Hierarchy_Schema": obj2_hierarchy,
            "CIAT_Phase1_Gate": obj3_gate1,
            "CIAT_Phase2_Gate": obj4_gate2,
            "CIAT_Phase3_Practitioner_Gate": obj5_gate3,
            "CIAT_Phase4_Clinical_Sovereign": obj6_sovereign
        }

        st.download_button(
            label="Download Master Audit Certificate (JSON)",
            data=json.dumps(master_export, indent=2),
            file_name=f"{doc_id}_audit.json",
            mime="application/json"
        )
