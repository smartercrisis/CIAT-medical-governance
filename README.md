# CHIMERA CIAT: Medical Governance & Compliance Auditing Engine

## Overview

**CHIMERA CIAT** is a cryptographically secure, automated medical compliance and regulatory verification engine. It evaluates medical manuscripts, trial protocols, and healthcare marketing copy against established institutional standards (**FDA**, **ICMJE**, and **HIPAA**) to prevent regulatory breaches, unverified efficacy claims, and privacy violations.

---

## System Architecture & Workflow

The engine executes a 6-stage deterministic compliance pipeline mapped to structured JSON schemas:

* **Practitioner Identity Context:** Authenticates session metadata and operator credentials.
* **Source Hierarchy Schema:** Fingerprints and locks the compliance anchor against the target text.
* **Phase 1 Ingestion Gate:** Parses regulatory mandates from the master anchor standard.
* **Phase 2 Audit Matrix:** Scans target text character-by-character against mandate patterns, classifying violations by severity (`CRITICAL` vs `HIGH`).
* **Phase 3 Practitioner Gate:** Generates a sanitized version of the target manuscript with inline violation tags.
* **Phase 4 Clinical Sovereign Ledger:** Generates an immutable HMAC SHA-256 hash chain sealing the entire audit trail into a signed Master Certificate.

---

## Operating Guide: How to Use the App

### Step 1: Configure Operator Identity
* Launch the application via Streamlit.
* In the sidebar, enter your assigned Practitioner ID and License Key.

### Step 2: Load the Anchor Standard
* The system automatically loads the default regulatory baseline from `schemas/anchor_standard.json` (combining FDA 21 CFR Part 202, ICMJE citation guidelines, and HIPAA Safe Harbor rules).
* To use a custom protocol, upload a specific `.json` anchor file using the file uploader in Section 1.

### Step 3: Input the Target Manuscript
* Navigate to Section 2 (**Target Manuscript Text**).
* Paste the draft article, clinical protocol, or marketing copy into the text area.

### Step 4: Execute the Audit
* Click **"Execute Governance Audit"**.
* Review the live results and download the cryptographically signed `.json` audit certificate.

---

## Understanding the Outputs

* **Regulatory Violations Breakdown:** Displays a structured matrix detailing every violated rule ID, regulatory reference, severity level, and flagged term.
* **Sanitized Manuscript Output:** Provides the modified text with inline violation tags (e.g., `[VIOLATION-MANDATE_FDA_01: guaranteed recovery]`) to guide editors or authors on required corrections.
* **Master Audit Certificate (`.json`):** A downloadable, tamper-proof record containing the complete session metadata, hash chain, and HMAC SHA-256 cryptographic signature.
