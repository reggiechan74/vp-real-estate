"""
VP Real Estate Platform - Main Dashboard
Institutional Real Estate Command Center
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from utils.styling import inject_custom_css, create_metric_card
from utils.charts import create_portfolio_donut
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="VP Real Estate Platform",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()

# Initialize session state for portfolio data
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = {
        'total_gla': 2_400_000,
        'arr': 48_200_000,
        'occupancy': 94.2,
        'walt': 4.8,
        'expiries_12mo': 18,
        'defaults': 2,
        'properties': 12,
        'tenants': 47
    }

if 'recent_activity' not in st.session_state:
    st.session_state.recent_activity = [
        {"time": "2 hours ago", "action": "Effective Rent Analysis", "details": "Acme Corp Renewal - NER: $27.14/SF"},
        {"time": "4 hours ago", "action": "Credit Analysis", "details": "TechStart Inc - Score: 72/100 (B+)"},
        {"time": "Yesterday", "action": "Lease Abstraction", "details": "Warehouse 401K - 60 month term"},
        {"time": "2 days ago", "action": "Default Analysis", "details": "XYZ Tenant - 5 day cure period"}
    ]

if 'alerts' not in st.session_state:
    st.session_state.alerts = [
        {
            "severity": "critical",
            "icon": "🔴",
            "title": "Default Notice Due",
            "details": "Tenant XYZ (Building 5)",
            "deadline": "Nov 21, 2025"
        },
        {
            "severity": "warning",
            "icon": "🟡",
            "title": "Option Exercise Window",
            "details": "ABC Corp Renewal Option",
            "deadline": "Dec 1, 2025"
        },
        {
            "severity": "info",
            "icon": "🟢",
            "title": "Insurance Renewal",
            "details": "Portfolio Policy Review",
            "deadline": "Dec 15, 2025"
        }
    ]

# Header
st.markdown("""
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 2rem; border-radius: 0.5rem; margin-bottom: 2rem;">
    <h1 style="color: white; margin: 0; font-size: 2.5rem;">🏢 VP Real Estate Platform</h1>
    <p style="color: #cbd5e1; margin: 0.5rem 0 0 0; font-size: 1.1rem;">
        Institutional Real Estate Command Center
    </p>
</div>
""", unsafe_allow_html=True)

# 3-Column Layout for Dashboard
col1, col2, col3 = st.columns([1, 1.2, 1])

# ===== COLUMN 1: Portfolio Metrics =====
with col1:
    st.markdown("### 📊 Portfolio Overview")

    # Portfolio metrics
    create_metric_card(
        "Total GLA",
        f"{st.session_state.portfolio_data['total_gla']:,} SF",
        delta=None
    )

    create_metric_card(
        "Annual Rent Revenue",
        f"${st.session_state.portfolio_data['arr']:,}",
        delta="+4.2%"
    )

    create_metric_card(
        "Occupancy Rate",
        f"{st.session_state.portfolio_data['occupancy']}%",
        delta="+1.3%"
    )

    create_metric_card(
        "WALT",
        f"{st.session_state.portfolio_data['walt']} years",
        delta=None
    )

    create_metric_card(
        "Expiries (12 Months)",
        f"{st.session_state.portfolio_data['expiries_12mo']} leases",
        delta=None,
        delta_color="inverse"
    )

    create_metric_card(
        "Defaults",
        f"{st.session_state.portfolio_data['defaults']} tenants",
        delta=None,
        delta_color="inverse"
    )

    # Portfolio composition chart
    st.markdown("#### Property Type Mix")
    portfolio_mix = {
        "Industrial": 1_500_000,
        "Office": 600_000,
        "Retail": 200_000,
        "Mixed Use": 100_000
    }
    fig_donut = create_portfolio_donut(portfolio_mix, "Portfolio by Asset Type (SF)")
    st.plotly_chart(fig_donut, use_container_width=True)

# ===== COLUMN 2: Quick Actions & Recent Activity =====
with col2:
    st.markdown("### ⚡ Quick Actions")

    # Quick action buttons in 2x2 grid
    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("📤 Upload Lease Document", use_container_width=True):
            st.info("Navigate to 'Lease Abstraction' in the sidebar to upload and analyze lease documents.")

        if st.button("📊 Run Effective Rent", use_container_width=True):
            st.info("Navigate to 'Effective Rent Calculator' in the sidebar to analyze deal economics.")

    with btn_col2:
        if st.button("💬 Ask Reggie", use_container_width=True):
            st.info("Navigate to 'Team Room' in the sidebar to chat with Reggie, Adam, or Dennis.")

        if st.button("📋 Abstract New Lease", use_container_width=True):
            st.info("Navigate to 'Lease Abstraction' in the sidebar to extract lease terms.")

    st.markdown("---")

    # Recent Activity
    st.markdown("### 📈 Recent Activity")

    for activity in st.session_state.recent_activity:
        st.markdown(f"""
        <div style="
            background-color: #f8fafc;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-radius: 0.375rem;
        ">
            <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 0.25rem;">
                {activity['time']}
            </div>
            <div style="color: #0f172a; font-weight: 600; margin-bottom: 0.25rem;">
                {activity['action']}
            </div>
            <div style="color: #475569; font-size: 0.9rem;">
                {activity['details']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ===== COLUMN 3: Alerts & Insights =====
with col3:
    st.markdown("### ⚠️ Attention Required")

    for alert in st.session_state.alerts:
        # Set border color based on severity
        if alert['severity'] == 'critical':
            border_color = '#dc2626'
            bg_color = '#fee2e2'
        elif alert['severity'] == 'warning':
            border_color = '#f59e0b'
            bg_color = '#fef3c7'
        else:
            border_color = '#10b981'
            bg_color = '#d1fae5'

        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-left: 4px solid {border_color};
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 0.375rem;
        ">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">
                {alert['icon']}
            </div>
            <div style="color: #0f172a; font-weight: 700; margin-bottom: 0.5rem; font-size: 1.05rem;">
                {alert['title']}
            </div>
            <div style="color: #1e293b; margin-bottom: 0.5rem;">
                {alert['details']}
            </div>
            <div style="color: #64748b; font-size: 0.9rem;">
                <strong>Due:</strong> {alert['deadline']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # System status
    st.markdown("### 📡 System Status")
    st.markdown("""
    <div style="background-color: #d1fae5; padding: 1rem; border-radius: 0.375rem; border-left: 4px solid #10b981;">
        <div style="color: #0f172a; font-weight: 600; margin-bottom: 0.5rem;">
            ✅ All Systems Operational
        </div>
        <div style="color: #475569; font-size: 0.9rem;">
            • Financial Calculators: Online<br>
            • AI Personas: Ready<br>
            • Document Processing: Active<br>
            • Reports Vault: Synced
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer section
st.markdown("---")

# Platform statistics in 4 columns
stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

with stat_col1:
    st.metric("Properties", st.session_state.portfolio_data['properties'])

with stat_col2:
    st.metric("Tenants", st.session_state.portfolio_data['tenants'])

with stat_col3:
    st.metric("Reports Generated", "234")

with stat_col4:
    st.metric("Uptime", "99.9%")

# Welcome message and navigation instructions
st.markdown("""
---

### 👋 Welcome to Your Institutional Real Estate Platform

**Getting Started:**
1. **Chat with The Team** - Navigate to "Team Room" to get expert advice from Adam (fast analyst), Reggie (crisis specialist), or Dennis (strategic advisor)
2. **Run Financial Analysis** - Use our 10 calculators to analyze deals, credit, renewals, and portfolio performance
3. **Process Leases** - Abstract leases, compare documents, and extract critical dates
4. **Ensure Compliance** - Generate notices, analyze defaults, and manage assignments
5. **Browse Reports** - Access your complete report vault with search and filtering

**Quick Tips:**
- Use the sidebar navigation to access all 25+ tools
- All financial calculators include interactive visualizations
- Export results to Excel/PDF for stakeholder presentations
- Chat with personas for deal guidance and strategic advice

---

<div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 1rem;">
    VP Real Estate Platform v1.0 | Institutional-Grade Analysis Tools<br>
    Powered by Claude Code | <a href="https://github.com/anthropics/claude-code" style="color: #3b82f6;">Documentation</a>
</div>
""", unsafe_allow_html=True)
