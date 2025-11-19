"""
Styling utilities for VP Real Estate Platform
Navy & Slate Professional Theme
"""

import streamlit as st


def inject_custom_css():
    """
    Inject custom CSS for institutional real estate aesthetic
    Design: Professional Bloomberg Terminal meets modern SaaS
    """
    st.markdown("""
    <style>
    /* ============================================
       VP REAL ESTATE PLATFORM - CUSTOM THEME
       Navy & Slate Professional
       ============================================ */

    /* Color Variables */
    :root {
        --primary-navy: #0f172a;
        --gold-accent: #d97706;
        --steel-blue: #3b82f6;
        --sage-green: #059669;
        --background: #f8fafc;
        --card-bg: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --danger: #dc2626;
        --warning: #f59e0b;
        --success: #10b981;
    }

    /* ============================================
       SIDEBAR STYLING
       ============================================ */

    /* Sidebar background - use stable data-testid selector */
    section[data-testid="stSidebar"] {
        background-color: var(--primary-navy) !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: var(--primary-navy) !important;
    }

    /* Sidebar text colors */
    section[data-testid="stSidebar"] .element-container {
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }

    section[data-testid="stSidebar"] p {
        color: #cbd5e1 !important;
    }

    /* Sidebar links */
    section[data-testid="stSidebar"] a {
        color: #93c5fd !important;
    }

    section[data-testid="stSidebar"] a:hover {
        color: #60a5fa !important;
    }

    /* ============================================
       MAIN CONTENT AREA
       ============================================ */

    .main {
        background-color: var(--background);
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-navy) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-weight: 700 !important;
    }

    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }

    h2 {
        font-size: 2rem !important;
        margin-top: 2rem !important;
        margin-bottom: 0.75rem !important;
    }

    h3 {
        font-size: 1.5rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Body Text */
    p, li, span {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: var(--text-primary) !important;
    }

    /* ============================================
       METRIC CARDS
       ============================================ */

    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        padding: 1.25rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }

    div[data-testid="stMetric"] label {
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: var(--text-secondary) !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: var(--primary-navy) !important;
        font-family: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', monospace !important;
    }

    /* ============================================
       BUTTONS
       ============================================ */

    .stButton > button {
        background-color: var(--steel-blue);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.375rem;
        padding: 0.5rem 1.5rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    .stButton > button:hover {
        background-color: #2563eb;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }

    .stButton > button:active {
        transform: translateY(0px);
    }

    /* Primary Button Variant */
    .stButton.primary > button {
        background-color: var(--primary-navy);
    }

    .stButton.primary > button:hover {
        background-color: #1e293b;
    }

    /* Success Button Variant */
    .stButton.success > button {
        background-color: var(--success);
    }

    .stButton.success > button:hover {
        background-color: #059669;
    }

    /* Danger Button Variant */
    .stButton.danger > button {
        background-color: var(--danger);
    }

    .stButton.danger > button:hover {
        background-color: #b91c1c;
    }

    /* ============================================
       INPUTS & FORMS
       ============================================ */

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 1px solid #cbd5e1;
        border-radius: 0.375rem;
        padding: 0.5rem;
        font-size: 0.95rem;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--steel-blue);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* Number inputs - monospace for financial data */
    .stNumberInput > div > div > input {
        font-family: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', monospace !important;
    }

    /* ============================================
       TABLES & DATAFRAMES
       ============================================ */

    .dataframe {
        border: 1px solid #e2e8f0 !important;
        border-radius: 0.5rem !important;
        overflow: hidden !important;
    }

    .dataframe thead tr th {
        background-color: var(--primary-navy) !important;
        color: white !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.05em !important;
        padding: 0.75rem !important;
    }

    .dataframe tbody tr:nth-child(even) {
        background-color: #f8fafc !important;
    }

    .dataframe tbody tr:hover {
        background-color: #f1f5f9 !important;
    }

    .dataframe tbody td {
        padding: 0.75rem !important;
        font-family: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', monospace !important;
        font-size: 0.875rem !important;
    }

    /* ============================================
       ALERTS & MESSAGES
       ============================================ */

    .stAlert {
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }

    div[data-baseweb="notification"] {
        border-radius: 0.5rem;
    }

    /* Success alerts */
    .stSuccess {
        background-color: #d1fae5;
        border-left: 4px solid var(--success);
    }

    /* Warning alerts */
    .stWarning {
        background-color: #fef3c7;
        border-left: 4px solid var(--warning);
    }

    /* Error alerts */
    .stError {
        background-color: #fee2e2;
        border-left: 4px solid var(--danger);
    }

    /* Info alerts */
    .stInfo {
        background-color: #dbeafe;
        border-left: 4px solid var(--steel-blue);
    }

    /* ============================================
       TABS
       ============================================ */

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 0.375rem 0.375rem 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: var(--text-secondary);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--steel-blue);
        color: white;
    }

    /* ============================================
       EXPANDERS
       ============================================ */

    .streamlit-expanderHeader {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.375rem;
        font-weight: 600;
        color: var(--primary-navy);
        padding: 0.75rem 1rem;
    }

    .streamlit-expanderHeader:hover {
        background-color: #f1f5f9;
    }

    .streamlit-expanderContent {
        border: 1px solid #e2e8f0;
        border-top: none;
        padding: 1rem;
        background-color: white;
    }

    /* ============================================
       FILE UPLOADER
       ============================================ */

    .stFileUploader {
        border: 2px dashed #cbd5e1;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background-color: #f8fafc;
        transition: all 0.2s ease;
    }

    .stFileUploader:hover {
        border-color: var(--steel-blue);
        background-color: #f1f5f9;
    }

    /* ============================================
       PROGRESS BARS
       ============================================ */

    .stProgress > div > div > div {
        background-color: var(--steel-blue);
        border-radius: 0.25rem;
    }

    /* ============================================
       CHAT MESSAGES
       ============================================ */

    .stChatMessage {
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* User messages */
    .stChatMessage[data-testid*="user"] {
        background-color: #dbeafe;
        border-left: 4px solid var(--steel-blue);
    }

    /* Assistant messages */
    .stChatMessage[data-testid*="assistant"] {
        background-color: #f8fafc;
        border-left: 4px solid var(--text-secondary);
    }

    /* ============================================
       CARDS & CONTAINERS
       ============================================ */

    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background-color: var(--card-bg);
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }

    /* ============================================
       PERSONA-SPECIFIC COLORS
       ============================================ */

    /* Adam (Analyst) - Blue Theme */
    .persona-adam {
        border-left: 4px solid var(--steel-blue);
        background-color: #eff6ff;
    }

    /* Reggie (VP) - Gold Theme */
    .persona-reggie {
        border-left: 4px solid var(--gold-accent);
        background-color: #fffbeb;
    }

    /* Dennis (Advisor) - Sage Theme */
    .persona-dennis {
        border-left: 4px solid var(--sage-green);
        background-color: #f0fdf4;
    }

    /* ============================================
       UTILITY CLASSES
       ============================================ */

    .text-center {
        text-align: center;
    }

    .text-right {
        text-align: right;
    }

    .font-mono {
        font-family: 'JetBrains Mono', 'SF Mono', 'Roboto Mono', monospace !important;
    }

    .text-danger {
        color: var(--danger) !important;
    }

    .text-warning {
        color: var(--warning) !important;
    }

    .text-success {
        color: var(--success) !important;
    }

    .bg-danger {
        background-color: #fee2e2 !important;
    }

    .bg-warning {
        background-color: #fef3c7 !important;
    }

    .bg-success {
        background-color: #d1fae5 !important;
    }

    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */

    @media (max-width: 768px) {
        h1 {
            font-size: 1.75rem !important;
        }

        h2 {
            font-size: 1.5rem !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
    }

    /* ============================================
       SCROLLBAR STYLING
       ============================================ */

    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }

    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }

    </style>
    """, unsafe_allow_html=True)


def apply_persona_theme(persona):
    """
    Apply persona-specific styling

    Args:
        persona: "adam", "reggie", or "dennis"
    """
    themes = {
        "adam": {
            "color": "#3b82f6",  # Steel Blue
            "bg": "#eff6ff",
            "name": "Adam - Senior Analyst"
        },
        "reggie": {
            "color": "#d97706",  # Gold
            "bg": "#fffbeb",
            "name": "Reggie Chan - VP"
        },
        "dennis": {
            "color": "#059669",  # Sage Green
            "bg": "#f0fdf4",
            "name": "Dennis - Strategic Advisor"
        }
    }

    if persona in themes:
        return themes[persona]
    return themes["adam"]  # Default to Adam


def create_metric_card(label, value, delta=None, delta_color="normal"):
    """
    Create a styled metric card

    Args:
        label: Metric label
        value: Metric value
        delta: Optional change value
        delta_color: "normal", "inverse", or "off"
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def create_alert_box(message, alert_type="info"):
    """
    Create a styled alert box

    Args:
        message: Alert message
        alert_type: "success", "warning", "error", or "info"
    """
    if alert_type == "success":
        st.success(message)
    elif alert_type == "warning":
        st.warning(message)
    elif alert_type == "error":
        st.error(message)
    else:
        st.info(message)
