"""
Effective Rent Calculator
NER, GER, NPV, IRR, Breakeven Analysis (Ponzi Rental Rate Framework)
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.styling import inject_custom_css
from utils.dummy_functions import calculate_effective_rent as calculate_effective_rent_dummy, generate_cash_flow_data
from utils.charts import create_cash_flow_chart, create_sensitivity_heatmap, create_waterfall_chart
from utils.calculator_integrations import calculate_effective_rent_real, get_calculator_status
import pandas as pd

# Page config
st.set_page_config(
    page_title="Effective Rent Calculator",
    page_icon="💰",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Header
st.title("💰 Effective Rent Calculator")
st.markdown("**Net Effective Rent (NER), NPV, and Breakeven Analysis** - Ponzi Rental Rate Framework")
st.markdown("---")

# Two-column layout: Input Form | Results
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### 📝 Input Parameters")

    with st.form("effective_rent_form"):
        # Deal Parameters
        st.markdown("#### Deal Parameters")
        base_rent = st.number_input("Base Rent ($/SF/Year)", value=30.00, min_value=0.0, step=0.25, help="Annual base rent per square foot")
        area = st.number_input("Rentable Area (SF)", value=10000, min_value=1, step=100, help="Total rentable square footage")
        term = st.number_input("Lease Term (Months)", value=60, min_value=1, max_value=360, step=12, help="Total lease term in months")

        st.markdown("---")

        # Tenant Incentives
        st.markdown("#### Tenant Incentives")
        free_rent = st.number_input("Free Rent (Months)", value=3, min_value=0, max_value=24, step=1, help="Number of months of rent abatement")
        ti_allowance = st.number_input("TI Allowance ($/SF)", value=25.00, min_value=0.0, step=1.0, help="Tenant improvement allowance per SF")
        moving_allowance = st.number_input("Moving Allowance ($)", value=10000, min_value=0, step=1000, help="One-time moving allowance")
        commission_pct = st.number_input("Leasing Commission (%)", value=5.0, min_value=0.0, max_value=10.0, step=0.25, help="Commission as % of total rent")

        st.markdown("---")

        # Landlord Economics
        st.markdown("#### Landlord Economics")
        discount_rate = st.number_input("Discount Rate (%)", value=6.5, min_value=0.0, max_value=20.0, step=0.25, help="Required rate of return")
        property_tax = st.number_input("Property Tax ($/SF)", value=4.50, min_value=0.0, step=0.25, help="Annual property tax per SF")
        opex = st.number_input("Operating Expenses ($/SF)", value=8.00, min_value=0.0, step=0.25, help="Annual operating expenses per SF")
        mgmt_fee = st.number_input("Management Fee (%)", value=5.0, min_value=0.0, max_value=10.0, step=0.25, help="Property management fee %")

        submitted = st.form_submit_button("📊 Calculate NER", use_container_width=True)

with col_right:
    st.markdown("### 📊 Results")

    if submitted:
        with st.spinner("Calculating effective rent..."):
            # Check if real calculator is available
            calc_status = get_calculator_status()
            using_real_calc = calc_status.get('effective_rent', False)

            # Calculate results - try real calculator first
            if using_real_calc:
                try:
                    results = calculate_effective_rent_real(
                        base_rent, area, term, free_rent, ti_allowance,
                        moving_allowance, commission_pct, discount_rate,
                        property_tax, opex, mgmt_fee
                    )
                    if not results.get('success', False):
                        st.warning(f"Real calculator error: {results.get('error', 'Unknown')}. Using fallback.")
                        results = calculate_effective_rent_dummy(
                            base_rent, area, term, free_rent, ti_allowance,
                            moving_allowance, commission_pct, discount_rate,
                            property_tax, opex, mgmt_fee
                        )
                        using_real_calc = False
                except Exception as e:
                    st.warning(f"Error with real calculator: {e}. Using fallback.")
                    results = calculate_effective_rent_dummy(
                        base_rent, area, term, free_rent, ti_allowance,
                        moving_allowance, commission_pct, discount_rate,
                        property_tax, opex, mgmt_fee
                    )
                    using_real_calc = False
            else:
                results = calculate_effective_rent_dummy(
                    base_rent, area, term, free_rent, ti_allowance,
                    moving_allowance, commission_pct, discount_rate,
                    property_tax, opex, mgmt_fee
                )
                using_real_calc = False

            # Display key metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)

            with metric_col1:
                st.metric(
                    "Net Effective Rent",
                    f"${results['ner']:.2f}/SF",
                    delta=f"{((results['ner']/base_rent - 1) * 100):.1f}% of base",
                    delta_color="inverse"
                )

            with metric_col2:
                st.metric(
                    "Gross Effective Rent",
                    f"${results['ger']:.2f}/SF",
                    delta=f"{((results['ger']/base_rent - 1) * 100):.1f}% of base"
                )

            with metric_col3:
                st.metric(
                    "NPV (Landlord)",
                    f"${results['npv']:,.0f}",
                    delta=None
                )

            metric_col4, metric_col5, metric_col6 = st.columns(3)

            with metric_col4:
                st.metric(
                    "IRR",
                    f"{results['irr']:.2f}%",
                    delta=f"+{(results['irr'] - discount_rate):.1f}% vs discount rate"
                )

            with metric_col5:
                st.metric(
                    "Breakeven Rent",
                    f"${results['breakeven']:.2f}/SF",
                    delta=None
                )

            with metric_col6:
                st.metric(
                    "Total Incentives",
                    f"${results['total_incentives']:,.0f}",
                    delta=None,
                    delta_color="inverse"
                )

            st.markdown("---")

            # Deal Summary
            st.markdown("#### 📋 Deal Summary")

            summary_data = {
                "Metric": [
                    "Total Base Rent (5 years)",
                    "Less: Free Rent",
                    "Less: TI Allowance",
                    "Less: Moving Allowance",
                    "Less: Leasing Commission",
                    "Net Cash to Landlord",
                    "Effective Months",
                    "Net Effective Rent ($/SF/year)"
                ],
                "Value": [
                    f"${base_rent * area * (term / 12):,.0f}",
                    f"${base_rent * area * (free_rent / 12):,.0f}",
                    f"${ti_allowance * area:,.0f}",
                    f"${moving_allowance:,.0f}",
                    f"${results['total_incentives'] * (commission_pct / 100):,.0f}",
                    f"${results['npv']:,.0f}",
                    f"{results['effective_months']} months",
                    f"${results['ner']:.2f}"
                ]
            }

            st.dataframe(
                pd.DataFrame(summary_data),
                use_container_width=True,
                hide_index=True
            )

            # Show which calculator was used
            calc_badge = "🔬 Real Calculator" if using_real_calc else "🧪 Demo Mode"
            st.success(f"✅ Analysis Complete [{calc_badge}] - Deal is {'profitable' if results['irr'] > discount_rate else 'below target'} at {results['irr']:.2f}% IRR")

    else:
        st.info("👈 Enter deal parameters in the form and click 'Calculate NER' to see results")

        # Show example metrics (placeholder)
        st.markdown("#### Example Results")
        st.markdown("""
        Once you run the calculation, you'll see:
        - **Net Effective Rent** - True economic rent after all concessions
        - **Gross Effective Rent** - Rent before operating expenses
        - **NPV** - Net present value of the deal to landlord
        - **IRR** - Internal rate of return
        - **Breakeven Rent** - Minimum rent to cover costs
        - **Interactive Charts** - Cash flow analysis and sensitivity
        """)

# Full-width sections below
st.markdown("---")

if submitted:
    # Generate visualizations
    st.markdown("### 📈 Cash Flow Analysis")

    # Generate cash flow data - use from results if available
    if 'cash_flow_data' in results:
        cash_flow_df = results['cash_flow_data']
    else:
        cash_flow_df = generate_cash_flow_data(base_rent, area, term, free_rent)

    # Create and display cash flow chart
    fig_cash_flow = create_cash_flow_chart(cash_flow_df)
    st.plotly_chart(fig_cash_flow, use_container_width=True)

    st.markdown("---")

    # Sensitivity Analysis
    st.markdown("### 🔥 Sensitivity Analysis")
    st.markdown("**Impact of Base Rent and TI Allowance on Net Effective Rent**")

    fig_sensitivity = create_sensitivity_heatmap(
        rent_range=(base_rent * 0.8, base_rent * 1.2),
        ti_range=(ti_allowance * 0.5, ti_allowance * 1.5)
    )
    st.plotly_chart(fig_sensitivity, use_container_width=True)

    st.markdown("---")

    # Deal Economics Waterfall
    st.markdown("### 💧 Deal Economics Breakdown")

    waterfall_data = {
        "categories": ["Base Rent", "Free Rent", "TI Allowance", "Moving", "Commission", "Net to Landlord"],
        "values": [
            base_rent * area * (term / 12),
            -(base_rent * area * (free_rent / 12)),
            -(ti_allowance * area),
            -moving_allowance,
            -(base_rent * area * (term / 12) * commission_pct / 100),
            0  # Will be calculated as total
        ]
    }

    fig_waterfall = create_waterfall_chart(
        waterfall_data["categories"],
        waterfall_data["values"],
        "Landlord Cash Flow Waterfall"
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

    st.markdown("---")

    # Export options
    st.markdown("### 📥 Export Results")

    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            st.info("Excel export functionality coming soon")

    with export_col2:
        if st.button("📄 Generate PDF Report", use_container_width=True):
            st.info("PDF report generation coming soon")

    with export_col3:
        if st.button("💾 Save to Reports Vault", use_container_width=True):
            st.info("Report vault integration coming soon")

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 📖 About This Calculator")

    st.info("""
    **Ponzi Rental Rate Framework**

    This calculator uses institutional-grade methodology to calculate true economic returns.

    **Key Metrics:**
    - **NER**: Net Effective Rent - true economic rent
    - **GER**: Gross Effective Rent - before opex
    - **NPV**: Net Present Value of cash flows
    - **IRR**: Internal Rate of Return
    - **Breakeven**: Minimum rent to cover costs
    """)

    st.markdown("---")

    st.markdown("### 💡 Tips")
    st.markdown("""
    **Best Practices:**
    - Include all tenant incentives
    - Use market discount rate
    - Consider full lease term
    - Factor in all costs
    - Run sensitivity analysis
    - Compare to market comps
    """)

    st.markdown("---")

    st.markdown("### 🔗 Related Tools")
    st.markdown("""
    - **Renewal Economics** - Renewal vs relocation
    - **Tenant Credit** - Assess tenant quality
    - **Relative Valuation** - Competitive positioning
    - **Market Comparison** - Benchmark against market
    """)
