"""
Reports Vault
Browse, search, and export generated reports
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from utils.styling import inject_custom_css
import pandas as pd

# Page config
st.set_page_config(
    page_title="Reports Vault",
    page_icon="🗄️",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Header
st.title("🗄️ Reports Vault")
st.markdown("**Browse, Search, and Export Your Generated Reports**")
st.markdown("---")

# Search and filter section
st.markdown("### 🔍 Search & Filter")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    search_query = st.text_input("🔎 Search reports", placeholder="Enter keywords...")

with filter_col2:
    date_range = st.date_input(
        "📅 Date Range",
        value=(datetime.now() - timedelta(days=30), datetime.now()),
        help="Filter reports by date range"
    )

with filter_col3:
    report_type_filter = st.multiselect(
        "📊 Report Type",
        ["All", "Effective Rent", "Tenant Credit", "Lease Abstract", "MCDA", "Default Analysis", "Comparison"],
        default=["All"]
    )

with filter_col4:
    tag_filter = st.multiselect(
        "🏷️ Tags",
        ["High Risk", "Board Approval", "Renewal", "New Lease", "Amendment", "Default"],
        default=[]
    )

st.markdown("---")

# Mock reports data
mock_reports = pd.DataFrame({
    "Timestamp": [
        "2025-11-19 14:30:22",
        "2025-11-18 10:15:45",
        "2025-11-17 16:22:10",
        "2025-11-16 09:45:33",
        "2025-11-15 13:20:18",
        "2025-11-14 11:55:42",
        "2025-11-13 15:10:29",
        "2025-11-12 08:35:17",
    ],
    "Report Type": [
        "Effective Rent",
        "Tenant Credit",
        "Lease Abstract",
        "Relative Valuation",
        "Default Analysis",
        "Effective Rent",
        "Lease Abstract",
        "Tenant Credit"
    ],
    "Property/Tenant": [
        "Acme Corp Renewal (Warehouse 5)",
        "TechStart Inc (Office 301)",
        "Warehouse 401K (Industrial)",
        "2550 Main St Positioning",
        "XYZ Tenant (Building 5)",
        "ABC Manufacturing (Unit 12)",
        "Office Tower - Suite 2000",
        "Retail Corp Inc"
    ],
    "Tags": [
        "Renewal, Board Approval",
        "New Lease, High Risk",
        "New Lease",
        "New Lease",
        "Default, High Risk",
        "Renewal",
        "New Lease",
        "New Lease"
    ],
    "Size": [
        "142 KB",
        "98 KB",
        "256 KB",
        "189 KB",
        "76 KB",
        "135 KB",
        "298 KB",
        "87 KB"
    ]
})

# Display options
display_col1, display_col2, display_col3 = st.columns([2, 1, 1])

with display_col1:
    st.markdown(f"### 📋 Reports ({len(mock_reports)} found)")

with display_col2:
    view_mode = st.selectbox("View", ["List View", "Card View", "Timeline View"], label_visibility="collapsed")

with display_col3:
    sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Type", "Property"], label_visibility="collapsed")

st.markdown("---")

# Display reports based on view mode
if view_mode == "List View":
    # Table view with actions
    for idx, row in mock_reports.iterrows():
        with st.container():
            report_col1, report_col2, report_col3, report_col4 = st.columns([3, 2, 2, 2])

            with report_col1:
                st.markdown(f"**{row['Report Type']}**")
                st.markdown(f"<small style='color: #64748b;'>{row['Property/Tenant']}</small>", unsafe_allow_html=True)

            with report_col2:
                st.markdown(f"<small style='color: #64748b;'>📅 {row['Timestamp']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small style='color: #64748b;'>💾 {row['Size']}</small>", unsafe_allow_html=True)

            with report_col3:
                tags = row['Tags'].split(", ")
                for tag in tags:
                    if "High Risk" in tag or "Default" in tag:
                        st.markdown(f"<span style='background-color: #fee2e2; color: #dc2626; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;'>{tag}</span>", unsafe_allow_html=True)
                    elif "Board Approval" in tag:
                        st.markdown(f"<span style='background-color: #fef3c7; color: #f59e0b; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;'>{tag}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='background-color: #dbeafe; color: #3b82f6; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem;'>{tag}</span>", unsafe_allow_html=True)

            with report_col4:
                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    if st.button("👁️", key=f"view_{idx}", help="View report"):
                        st.info(f"Opening {row['Report Type']} report...")
                with action_col2:
                    if st.button("📥", key=f"download_{idx}", help="Download report"):
                        st.success(f"Downloading {row['Report Type']}...")
                with action_col3:
                    if st.button("🗑️", key=f"delete_{idx}", help="Delete report"):
                        st.warning("Delete functionality coming soon")

            st.markdown("<hr style='margin: 0.5rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

elif view_mode == "Card View":
    # Card grid view
    cards_per_row = 3
    for i in range(0, len(mock_reports), cards_per_row):
        cols = st.columns(cards_per_row)
        for j, col in enumerate(cols):
            if i + j < len(mock_reports):
                row = mock_reports.iloc[i + j]
                with col:
                    st.markdown(f"""
                    <div style="
                        background-color: white;
                        border: 1px solid #e2e8f0;
                        border-radius: 0.5rem;
                        padding: 1rem;
                        margin-bottom: 1rem;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    ">
                        <div style="color: #3b82f6; font-weight: 700; margin-bottom: 0.5rem;">
                            {row['Report Type']}
                        </div>
                        <div style="color: #1e293b; font-size: 0.9rem; margin-bottom: 0.5rem;">
                            {row['Property/Tenant']}
                        </div>
                        <div style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem;">
                            📅 {row['Timestamp']}<br>
                            💾 {row['Size']}
                        </div>
                        <div style="margin-bottom: 0.5rem;">
                            <small style="background-color: #dbeafe; color: #3b82f6; padding: 0.2rem 0.4rem; border-radius: 0.2rem; font-size: 0.7rem;">
                                {row['Tags'].split(", ")[0]}
                            </small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        st.button("View", key=f"card_view_{i+j}", use_container_width=True)
                    with btn_col2:
                        st.button("Download", key=f"card_download_{i+j}", use_container_width=True)

else:  # Timeline View
    st.markdown("### 📅 Timeline View")

    for idx, row in mock_reports.iterrows():
        st.markdown(f"""
        <div style="
            border-left: 3px solid #3b82f6;
            padding-left: 1rem;
            margin-bottom: 1.5rem;
        ">
            <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 0.25rem;">
                {row['Timestamp']}
            </div>
            <div style="color: #0f172a; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.25rem;">
                {row['Report Type']} - {row['Property/Tenant']}
            </div>
            <div style="color: #64748b; font-size: 0.9rem;">
                Tags: {row['Tags']} | Size: {row['Size']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Bulk actions
st.markdown("### 📦 Bulk Actions")

bulk_col1, bulk_col2, bulk_col3, bulk_col4 = st.columns(4)

with bulk_col1:
    if st.button("📥 Export All to ZIP", use_container_width=True):
        st.info("Bulk export coming soon - will create ZIP archive of all selected reports")

with bulk_col2:
    if st.button("🗑️ Delete Selected", use_container_width=True):
        st.warning("Bulk delete coming soon")

with bulk_col3:
    if st.button("🏷️ Add Tags", use_container_width=True):
        st.info("Bulk tagging coming soon")

with bulk_col4:
    if st.button("📊 Generate Summary", use_container_width=True):
        st.info("Portfolio summary report coming soon")

# Sidebar
with st.sidebar:
    st.markdown("### 📖 About Reports Vault")

    st.info("""
    **Reports Vault**

    Central repository for all generated analyses and reports.

    **Features:**
    - Full-text search
    - Date range filtering
    - Tag-based organization
    - Bulk export
    - Version history
    """)

    st.markdown("---")

    st.markdown("### 📊 Vault Statistics")

    st.metric("Total Reports", len(mock_reports))
    st.metric("This Month", f"{len(mock_reports)} reports")
    st.metric("Storage Used", "2.4 GB")
    st.metric("Tags", "12 active tags")

    st.markdown("---")

    st.markdown("### 💡 Tips")
    st.markdown("""
    **Best Practices:**
    - Tag reports for easy filtering
    - Export important analyses
    - Regular cleanup of old reports
    - Use search for quick access
    - Archive annually
    """)

    st.markdown("---")

    st.markdown("### 🔗 Quick Links")
    st.markdown("""
    - **Run New Analysis** - Go to calculators
    - **Upload Document** - Lease abstraction
    - **Chat with Team** - Get expert advice
    """)
