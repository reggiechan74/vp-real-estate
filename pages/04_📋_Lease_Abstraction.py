"""
Lease Abstraction Tool
24-Section lease abstraction for Industrial and Office properties
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.styling import inject_custom_css
from utils.dummy_functions import run_lease_abstraction
import json

# Page config
st.set_page_config(
    page_title="Lease Abstraction",
    page_icon="📋",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Header
st.title("📋 Lease Abstraction")
st.markdown("**24-Section Comprehensive Lease Analysis** - Industrial & Office lease abstraction using BOMA standards")
st.markdown("---")

# Upload section
st.markdown("### 📤 Upload Lease Document")

col_upload1, col_upload2 = st.columns([2, 1])

with col_upload1:
    uploaded_file = st.file_uploader(
        "Drag & Drop PDF or DOCX lease document",
        type=['pdf', 'docx', 'doc'],
        help="Upload the lease agreement for abstraction"
    )

with col_upload2:
    lease_type = st.radio(
        "Property Type",
        ["Industrial", "Office"],
        help="Select property type for appropriate measurement standards"
    )

    if st.button("🔍 Run Abstraction", use_container_width=True, disabled=uploaded_file is None):
        st.session_state.run_abstraction = True

# Show abstraction results
if uploaded_file and st.session_state.get('run_abstraction', False):
    with st.spinner(f"Abstracting {lease_type} lease document..."):
        # Run abstraction (dummy function)
        abstract = run_lease_abstraction(uploaded_file, lease_type)

        st.success(f"✅ Lease abstraction complete! Extracted {len(abstract)} sections from {uploaded_file.name}")

        st.markdown("---")
        st.markdown("## 📄 Lease Abstract")

        # Display abstract in two columns
        col_left, col_right = st.columns(2)

        sections = list(abstract.items())
        mid_point = len(sections) // 2

        with col_left:
            for section_name, section_data in sections[:mid_point]:
                with st.expander(f"**{section_name}**", expanded=False):
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if isinstance(value, list):
                                st.markdown(f"**{key}:**")
                                for item in value:
                                    st.markdown(f"  - {item}")
                            else:
                                st.markdown(f"**{key}:** {value}")
                    else:
                        st.markdown(section_data)

        with col_right:
            for section_name, section_data in sections[mid_point:]:
                with st.expander(f"**{section_name}**", expanded=False):
                    if isinstance(section_data, dict):
                        for key, value in section_data.items():
                            if isinstance(value, list):
                                st.markdown(f"**{key}:**")
                                for item in value:
                                    st.markdown(f"  - {item}")
                            else:
                                st.markdown(f"**{key}:** {value}")
                    else:
                        st.markdown(section_data)

        st.markdown("---")

        # Summary metrics
        st.markdown("### 📊 Quick Summary")

        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

        with summary_col1:
            st.metric("Property Type", lease_type)

        with summary_col2:
            st.metric("Rentable Area", abstract["2. Premises"]["Rentable Area"])

        with summary_col3:
            st.metric("Lease Term", abstract["1. Basic Information"]["Lease Term"])

        with summary_col4:
            st.metric("Renewal Options", abstract["8. Renewal Options"]["Number of Options"])

        st.markdown("---")

        # Export options
        st.markdown("### 📥 Export Abstract")

        export_col1, export_col2, export_col3, export_col4 = st.columns(4)

        with export_col1:
            if st.button("📊 Export to Excel", use_container_width=True):
                st.info("Excel export coming soon - will include all 24 sections in structured format")

        with export_col2:
            if st.button("📄 Export to PDF", use_container_width=True):
                st.info("PDF export coming soon - formatted lease abstract report")

        with export_col3:
            # JSON export (functional)
            json_str = json.dumps(abstract, indent=2)
            st.download_button(
                label="📦 Download JSON",
                data=json_str,
                file_name=f"lease_abstract_{uploaded_file.name.split('.')[0]}.json",
                mime="application/json",
                use_container_width=True
            )

        with export_col4:
            if st.button("💾 Save to Vault", use_container_width=True):
                st.info("Reports Vault integration coming soon")

        st.markdown("---")

        # Critical dates callout
        st.markdown("### 📅 Critical Dates")

        critical_dates = abstract["22. Critical Dates"]

        dates_col1, dates_col2 = st.columns(2)

        with dates_col1:
            for key, value in list(critical_dates.items())[:3]:
                st.info(f"**{key}:** {value}")

        with dates_col2:
            for key, value in list(critical_dates.items())[3:]:
                st.info(f"**{key}:** {value}")

        # Special provisions highlight
        if "23. Special Provisions (Schedule G)" in abstract:
            st.markdown("---")
            st.markdown("### ⚠️ Special Provisions (Schedule G)")

            st.warning("""
            **Important Custom Terms:**

            These provisions modify or override standard lease terms. Review carefully!
            """)

            special_provisions = abstract["23. Special Provisions (Schedule G)"]["Custom Terms"]
            for provision in special_provisions:
                st.markdown(f"- {provision}")

else:
    # Instructions when no file uploaded
    st.info("""
    👆 **Upload a lease document to begin abstraction**

    This tool will extract all key lease terms into a standardized 24-section format.
    """)

    st.markdown("---")

    st.markdown("### 📖 The 24-Section Lease Abstract")

    col_sections1, col_sections2 = st.columns(2)

    with col_sections1:
        st.markdown("""
        **Core Terms:**
        1. Basic Information
        2. Premises
        3. Rent Schedule
        4. Additional Rent
        5. Proportionate Share
        6. Security Deposit
        7. Tenant Improvements
        8. Renewal Options
        9. Expansion Options
        10. Termination Options
        11. Assignment & Subletting
        12. Use Restrictions
        """)

    with col_sections2:
        st.markdown("""
        **Rights & Obligations:**
        13. Exclusivity Clauses
        14. Parking
        15. Signage
        16. Insurance Requirements
        17. Environmental Obligations
        18. Default Provisions
        19. Remedies
        20. Indemnification
        21. SNDA (Subordination, Non-Disturbance, Attornment)
        22. Critical Dates
        23. Special Provisions (Schedule G)
        24. Exhibits/Schedules
        """)

    st.markdown("---")

    st.markdown("### 🎯 What Gets Extracted")

    feature_col1, feature_col2, feature_col3 = st.columns(3)

    with feature_col1:
        st.markdown("""
        **Financial Terms:**
        - Base rent & escalations
        - Operating expenses
        - Additional rent
        - Security deposit
        - TI allowance
        - Proportionate share
        """)

    with feature_col2:
        st.markdown("""
        **Rights & Options:**
        - Renewal options
        - Expansion rights
        - Termination clauses
        - Assignment/subletting
        - ROFR/ROFO
        - Exclusivity
        """)

    with feature_col3:
        st.markdown("""
        **Obligations:**
        - Insurance requirements
        - Environmental compliance
        - Default & remedies
        - Use restrictions
        - Parking & signage
        - Critical dates
        """)

# Sidebar
with st.sidebar:
    st.markdown("### 📖 About This Tool")

    st.info("""
    **Lease Abstraction**

    Comprehensive 24-section lease analysis using institutional standards.

    **Measurement Standards:**
    - Industrial: BOMA Method A
    - Office: BOMA Office Buildings Standard

    **Supports:**
    - PDF documents
    - Word documents (.docx)
    - Multi-tenant leases
    - Net & gross leases
    """)

    st.markdown("---")

    st.markdown("### 💡 Tips")
    st.markdown("""
    **Best Practices:**
    - Upload final executed lease
    - Include all amendments
    - Review Schedule G carefully
    - Verify critical dates
    - Export to Excel for database
    - Save to Reports Vault
    """)

    st.markdown("---")

    st.markdown("### 🔗 Related Tools")
    st.markdown("""
    - **Critical Dates** - Extract timeline
    - **Compare Amendment** - Track changes
    - **Effective Rent** - Analyze economics
    - **Default Analysis** - Review remedies
    """)

    st.markdown("---")

    if uploaded_file and st.session_state.get('run_abstraction', False):
        st.markdown("### 📄 Document Info")
        st.markdown(f"""
        **Filename:** {uploaded_file.name}

        **Type:** {uploaded_file.type}

        **Size:** {uploaded_file.size:,} bytes

        **Property:** {lease_type}
        """)
