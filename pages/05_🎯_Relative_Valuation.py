"""
Relative Valuation (MCDA)
Multi-Criteria Decision Analysis - 25-variable competitive positioning
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.styling import inject_custom_css
from utils.dummy_functions import calculate_relative_valuation as calculate_relative_valuation_dummy
from utils.charts import create_radar_chart, create_scatter_plot
from utils.calculator_integrations import calculate_relative_valuation_real, get_calculator_status
import pandas as pd
import numpy as np

# Page config
st.set_page_config(
    page_title="Relative Valuation (MCDA)",
    page_icon="🎯",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Header
st.title("🎯 Relative Valuation - MCDA")
st.markdown("**Multi-Criteria Decision Analysis** - 25-variable competitive positioning and strategic pricing")
st.markdown("---")

# Initialize session state for variables
if 'variables' not in st.session_state:
    st.session_state.variables = {}

# Instructions
with st.expander("ℹ️ **How to Use This Tool**", expanded=False):
    st.markdown("""
    **Relative Valuation analyzes competitive positioning using 25 weighted variables across 5 categories:**

    1. **Location Variables (30% weight)** - Highway access, transit, labor market, amenities, visibility
    2. **Building Variables (25% weight)** - Clear height, column spacing, loading, age, condition
    3. **Financial Variables (25% weight)** - Rent, opex, TI allowance, free rent, term
    4. **Operational Variables (15% weight)** - Parking, power, HVAC, truck access, yard
    5. **Market Variables (5% weight)** - Vacancy, growth, competition

    **Scoring:** Each variable rated 0-10 (10 = best, 0 = worst)

    **Output:** Overall score, category breakdowns, radar chart, competitive landscape PDF
    """)

st.markdown("---")

# Variable input form
st.markdown("### 📊 Variable Scoring")
st.markdown("*Rate each variable from 0-10 (10 = excellent, 0 = poor)*")

# Create tabs for variable categories
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Location (30%)",
    "🏭 Building (25%)",
    "💰 Financial (25%)",
    "⚙️ Operational (15%)",
    "📈 Market (5%)"
])

with tab1:
    st.markdown("#### Location Variables")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.variables['highway_access'] = st.slider(
            "Highway Access",
            0, 10, 7,
            help="Proximity and quality of highway access (10 = <1km to major highway)"
        )

        st.session_state.variables['transit_access'] = st.slider(
            "Transit Access",
            0, 10, 5,
            help="Public transportation options (10 = subway/train station <500m)"
        )

        st.session_state.variables['labor_market'] = st.slider(
            "Labor Market Depth",
            0, 10, 8,
            help="Available workforce and unemployment rate (10 = large pool, low unemployment)"
        )

    with col2:
        st.session_state.variables['amenities'] = st.slider(
            "Local Amenities",
            0, 10, 6,
            help="Nearby restaurants, services, retail (10 = comprehensive amenities)"
        )

        st.session_state.variables['visibility'] = st.slider(
            "Site Visibility",
            0, 10, 7,
            help="Property visibility from major roads (10 = excellent signage exposure)"
        )

with tab2:
    st.markdown("#### Building Variables")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.variables['clear_height'] = st.slider(
            "Clear Height",
            0, 10, 7,
            help="Ceiling height (10 = >32', 0 = <16')"
        )

        st.session_state.variables['column_spacing'] = st.slider(
            "Column Spacing",
            0, 10, 8,
            help="Bay spacing (10 = >50', 0 = <30')"
        )

        st.session_state.variables['loading_doors'] = st.slider(
            "Loading Doors",
            0, 10, 6,
            help="Dock doors & drive-in doors (10 = 1 door per 5,000 SF)"
        )

    with col2:
        st.session_state.variables['building_age'] = st.slider(
            "Building Age",
            0, 10, 5,
            help="Age of building (10 = <5 years, 0 = >40 years)"
        )

        st.session_state.variables['condition'] = st.slider(
            "Building Condition",
            0, 10, 7,
            help="Physical condition (10 = excellent/new, 0 = poor)"
        )

with tab3:
    st.markdown("#### Financial Variables")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.variables['rent_psf'] = st.slider(
            "Rent Competitiveness",
            0, 10, 6,
            help="Rent vs market (10 = significantly below market, 0 = above market)"
        )

        st.session_state.variables['opex_psf'] = st.slider(
            "Operating Expense Efficiency",
            0, 10, 7,
            help="Opex vs peers (10 = lowest opex, 0 = highest)"
        )

        st.session_state.variables['ti_allowance'] = st.slider(
            "TI Allowance Attractiveness",
            0, 10, 5,
            help="TI package (10 = generous allowance, 0 = minimal)"
        )

    with col2:
        st.session_state.variables['free_rent'] = st.slider(
            "Free Rent Offered",
            0, 10, 4,
            help="Rent abatement (10 = significant free rent, 0 = none)"
        )

        st.session_state.variables['term_length'] = st.slider(
            "Term Flexibility",
            0, 10, 7,
            help="Lease term options (10 = very flexible, 0 = rigid)"
        )

with tab4:
    st.markdown("#### Operational Variables")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.variables['parking_ratio'] = st.slider(
            "Parking Ratio",
            0, 10, 6,
            help="Parking spaces per 1,000 SF (10 = >3 spaces, 0 = <1 space)"
        )

        st.session_state.variables['power_capacity'] = st.slider(
            "Power Capacity",
            0, 10, 7,
            help="Electrical capacity (10 = >1,000 amps, 0 = minimal)"
        )

        st.session_state.variables['hvac_system'] = st.slider(
            "HVAC System Quality",
            0, 10, 6,
            help="Climate control (10 = zoned, efficient, 0 = basic/none)"
        )

    with col2:
        st.session_state.variables['truck_access'] = st.slider(
            "Truck Access",
            0, 10, 8,
            help="Truck maneuverability (10 = excellent, 0 = difficult)"
        )

        st.session_state.variables['yard_space'] = st.slider(
            "Yard/Staging Space",
            0, 10, 5,
            help="Exterior storage/staging (10 = ample, 0 = none)"
        )

with tab5:
    st.markdown("#### Market Variables")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.variables['vacancy_rate'] = st.slider(
            "Market Vacancy (Inverse)",
            0, 10, 7,
            help="Submarket vacancy (10 = <2% vacancy, 0 = >15%)"
        )

        st.session_state.variables['market_growth'] = st.slider(
            "Market Growth Trajectory",
            0, 10, 6,
            help="Market momentum (10 = strong growth, 0 = declining)"
        )

    with col2:
        st.session_state.variables['competition'] = st.slider(
            "Competitive Intensity (Inverse)",
            0, 10, 5,
            help="Competitive landscape (10 = limited competition, 0 = oversupplied)"
        )

st.markdown("---")

# Calculate button
if st.button("📊 Calculate Competitive Position", use_container_width=True, type="primary"):
    with st.spinner("Analyzing competitive positioning..."):
        # Check if real calculator is available
        calc_status = get_calculator_status()
        using_real_calc = calc_status.get('relative_valuation', False)

        # Calculate results - try real calculator first
        if using_real_calc:
            try:
                results = calculate_relative_valuation_real(st.session_state.variables)
                if not results.get('success', False):
                    results = calculate_relative_valuation_dummy(st.session_state.variables)
                    using_real_calc = False
            except Exception as e:
                results = calculate_relative_valuation_dummy(st.session_state.variables)
                using_real_calc = False
        else:
            results = calculate_relative_valuation_dummy(st.session_state.variables)
            using_real_calc = False

        st.markdown("---")
        st.markdown("## 📈 Competitive Positioning Analysis")

        # Top-level metrics
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)

        with metric_col1:
            st.metric("Overall Score", f"{results['overall_score']:.2f}/10")

        with metric_col2:
            st.metric("Market Position", results['market_position'])

        with metric_col3:
            st.metric("Location", f"{results['location_score']:.2f}/10")

        with metric_col4:
            st.metric("Building", f"{results['building_score']:.2f}/10")

        with metric_col5:
            st.metric("Financial", f"{results['financial_score']:.2f}/10")

        st.markdown("---")

        # Detailed category scores
        st.markdown("### 📊 Category Breakdown")

        score_col1, score_col2 = st.columns(2)

        with score_col1:
            st.markdown("#### Category Scores")

            category_df = pd.DataFrame({
                "Category": ["Location", "Building", "Financial", "Operational", "Market"],
                "Weight": ["30%", "25%", "25%", "15%", "5%"],
                "Score": [
                    f"{results['location_score']:.2f}/10",
                    f"{results['building_score']:.2f}/10",
                    f"{results['financial_score']:.2f}/10",
                    f"{results['operational_score']:.2f}/10",
                    f"{results['market_score']:.2f}/10"
                ],
                "Weighted Contribution": [
                    f"{results['location_score'] * 0.30:.2f}",
                    f"{results['building_score'] * 0.25:.2f}",
                    f"{results['financial_score'] * 0.25:.2f}",
                    f"{results['operational_score'] * 0.15:.2f}",
                    f"{results['market_score'] * 0.05:.2f}"
                ]
            })

            st.dataframe(category_df, use_container_width=True, hide_index=True)

        with score_col2:
            st.markdown("#### Strategic Positioning")

            if results['overall_score'] >= 8.0:
                st.success(f"""
                **Premium Property**

                Score: {results['overall_score']:.2f}/10

                This property is in the top tier of the market. Strong positioning across multiple categories allows for premium pricing and selective tenant choice.

                **Recommendation:** Command top-of-market rent, maintain high standards for tenant quality.
                """)
            elif results['overall_score'] >= 6.5:
                st.info(f"""
                **Above Average Property**

                Score: {results['overall_score']:.2f}/10

                This property competes well in the market with solid fundamentals. Good positioning for value-oriented tenants seeking quality.

                **Recommendation:** Price at or slightly above market, emphasize competitive advantages.
                """)
            elif results['overall_score'] >= 5.0:
                st.warning(f"""
                **Average Property**

                Score: {results['overall_score']:.2f}/10

                This property is mid-market with mixed strengths and weaknesses. Requires competitive pricing and concessions to attract tenants.

                **Recommendation:** Price at market, offer incentives, identify and fix weaknesses.
                """)
            else:
                st.error(f"""
                **Below Average Property**

                Score: {results['overall_score']:.2f}/10

                This property faces challenges in competing effectively. Significant improvements or pricing adjustments needed.

                **Recommendation:** Price below market, generous concessions, capital improvement plan required.
                """)

        st.markdown("---")

        # Radar chart visualization
        st.markdown("### 🎯 Property Fingerprint - Radar Chart")

        # Prepare data for radar chart
        variable_names = [
            "Highway", "Transit", "Labor", "Amenities", "Visibility",
            "Clear Ht", "Columns", "Loading", "Age", "Condition",
            "Rent", "OpEx", "TI", "Free Rent", "Term",
            "Parking", "Power", "HVAC", "Truck", "Yard",
            "Vacancy", "Growth", "Competition"
        ]

        variable_scores = [
            st.session_state.variables.get('highway_access', 5),
            st.session_state.variables.get('transit_access', 5),
            st.session_state.variables.get('labor_market', 5),
            st.session_state.variables.get('amenities', 5),
            st.session_state.variables.get('visibility', 5),
            st.session_state.variables.get('clear_height', 5),
            st.session_state.variables.get('column_spacing', 5),
            st.session_state.variables.get('loading_doors', 5),
            st.session_state.variables.get('building_age', 5),
            st.session_state.variables.get('condition', 5),
            st.session_state.variables.get('rent_psf', 5),
            st.session_state.variables.get('opex_psf', 5),
            st.session_state.variables.get('ti_allowance', 5),
            st.session_state.variables.get('free_rent', 5),
            st.session_state.variables.get('term_length', 5),
            st.session_state.variables.get('parking_ratio', 5),
            st.session_state.variables.get('power_capacity', 5),
            st.session_state.variables.get('hvac_system', 5),
            st.session_state.variables.get('truck_access', 5),
            st.session_state.variables.get('yard_space', 5),
            st.session_state.variables.get('vacancy_rate', 5),
            st.session_state.variables.get('market_growth', 5),
            st.session_state.variables.get('competition', 5)
        ]

        fig_radar = create_radar_chart(
            variable_names[:15],  # Show first 15 for readability
            variable_scores[:15],
            "Property Competitive Profile"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        # Scatter plot - Price vs Quality
        st.markdown("### 📉 Competitive Landscape - Price vs Quality")

        # Create mock competitive set
        comp_data = pd.DataFrame({
            'Property': ['Subject', 'Comp A', 'Comp B', 'Comp C', 'Comp D', 'Comp E'],
            'Quality_Score': [
                results['overall_score'],
                np.random.uniform(5, 9),
                np.random.uniform(5, 9),
                np.random.uniform(4, 8),
                np.random.uniform(6, 8.5),
                np.random.uniform(5.5, 8)
            ],
            'Price_Index': [100, 95, 105, 85, 110, 92],  # Subject = 100
            'Type': ['Subject', 'Comparable', 'Comparable', 'Comparable', 'Comparable', 'Comparable']
        })

        fig_scatter = create_scatter_plot(
            comp_data,
            'Quality_Score',
            'Price_Index',
            'Type',
            "Competitive Positioning Matrix"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("---")

        # Export options
        st.markdown("### 📥 Export Competitive Analysis")

        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            if st.button("📄 Generate Landscape PDF", use_container_width=True):
                st.info("PDF landscape report coming soon - includes all charts, rankings, and recommendations")

        with export_col2:
            if st.button("📊 Export to Excel", use_container_width=True):
                st.info("Excel export coming soon - detailed scoring matrix")

        with export_col3:
            if st.button("💾 Save to Vault", use_container_width=True):
                st.info("Reports Vault integration coming soon")

        # Show which calculator was used
        calc_badge = "🔬 Real Calculator" if using_real_calc else "🧪 Demo Mode"
        st.info(f"ℹ️ Analysis performed using: {calc_badge}")

# Sidebar
with st.sidebar:
    st.markdown("### 📖 About MCDA")

    st.info("""
    **Multi-Criteria Decision Analysis**

    Systematic framework for evaluating properties using 25 weighted variables.

    **Category Weights:**
    - Location: 30%
    - Building: 25%
    - Financial: 25%
    - Operational: 15%
    - Market: 5%

    **Scoring Scale:**
    - 8-10: Premium/Excellent
    - 6.5-8: Above Average
    - 5-6.5: Average
    - <5: Below Average
    """)

    st.markdown("---")

    st.markdown("### 💡 Use Cases")
    st.markdown("""
    **Applications:**
    - Acquisition evaluation
    - Pricing strategy
    - Portfolio benchmarking
    - Competitive positioning
    - Capital improvement prioritization
    - Tenant marketing
    """)

    st.markdown("---")

    st.markdown("### 🔗 Related Tools")
    st.markdown("""
    - **Effective Rent** - Price optimization
    - **Market Comparison** - Comp analysis
    - **Renewal Economics** - Tenant retention
    """)
