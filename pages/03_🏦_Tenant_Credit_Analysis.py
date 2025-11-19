"""
Tenant Credit Analysis
Creditworthiness assessment, DSCR analysis, and security structuring
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.styling import inject_custom_css
from utils.dummy_functions import calculate_credit_score as calculate_credit_score_dummy
from utils.charts import create_credit_gauge
from utils.calculator_integrations import calculate_credit_score_real, get_calculator_status
import pandas as pd

# Page config
st.set_page_config(
    page_title="Tenant Credit Analysis",
    page_icon="🏦",
    layout="wide"
)

# Inject custom CSS
inject_custom_css()

# Header
st.title("🏦 Tenant Credit Analysis")
st.markdown("**Creditworthiness Assessment & Risk Scoring** - Institutional-grade tenant evaluation")
st.markdown("---")

# Form for credit analysis
with st.form("credit_analysis_form"):
    # Company Information
    st.markdown("### 🏢 Company Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        company_name = st.text_input("Company Name", value="Sample Corp Inc.")

    with col2:
        industry = st.selectbox(
            "Industry",
            ["Technology", "Manufacturing", "Retail", "Logistics", "Healthcare", "Professional Services", "Other"]
        )

    with col3:
        years_operating = st.number_input("Years Operating", value=5, min_value=0, max_value=100, step=1)

    st.markdown("---")

    # Financial Ratios
    st.markdown("### 📊 Financial Ratios")

    ratio_col1, ratio_col2 = st.columns(2)

    with ratio_col1:
        dscr = st.number_input(
            "DSCR (Debt Service Coverage Ratio)",
            value=1.5,
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            help="Net Operating Income / Total Debt Service (>1.25 is healthy)"
        )

        current_ratio = st.number_input(
            "Current Ratio",
            value=2.0,
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            help="Current Assets / Current Liabilities (>1.5 is healthy)"
        )

    with ratio_col2:
        debt_ebitda = st.number_input(
            "Debt-to-EBITDA Ratio",
            value=2.5,
            min_value=0.0,
            max_value=20.0,
            step=0.1,
            help="Total Debt / EBITDA (<3.0 is healthy)"
        )

        icr = st.number_input(
            "Interest Coverage Ratio",
            value=4.0,
            min_value=0.0,
            max_value=50.0,
            step=0.5,
            help="EBIT / Interest Expense (>3.0 is healthy)"
        )

    st.markdown("---")

    # Revenue Metrics
    st.markdown("### 💰 Revenue Metrics")

    rev_col1, rev_col2, rev_col3 = st.columns(3)

    with rev_col1:
        revenue = st.number_input(
            "Annual Revenue ($)",
            value=5000000,
            min_value=0,
            step=100000,
            help="Total annual revenue"
        )

    with rev_col2:
        revenue_growth = st.slider(
            "Revenue Growth Rate (%)",
            min_value=-50.0,
            max_value=100.0,
            value=15.0,
            step=1.0,
            help="Year-over-year revenue growth"
        )

    with rev_col3:
        gross_margin = st.slider(
            "Gross Margin (%)",
            min_value=0.0,
            max_value=100.0,
            value=45.0,
            step=1.0,
            help="Gross profit as % of revenue"
        )

    st.markdown("---")

    submitted = st.form_submit_button("📊 Analyze Credit", use_container_width=True)

# Results section
if submitted:
    with st.spinner("Analyzing tenant credit..."):
        # Check if real calculator is available
        calc_status = get_calculator_status()
        using_real_calc = calc_status.get('credit_analysis', False)

        # Calculate credit score - try real calculator first
        if using_real_calc:
            try:
                results = calculate_credit_score_real(
                    company_name, industry, years_operating,
                    dscr, current_ratio, debt_ebitda, icr,
                    revenue, revenue_growth, gross_margin
                )
                if not results.get('success', False):
                    st.warning(f"Real calculator error: {results.get('error', 'Unknown')}. Using fallback.")
                    results = calculate_credit_score_dummy(
                        dscr, current_ratio, debt_ebitda, revenue_growth,
                        gross_margin, years_operating, industry
                    )
                    using_real_calc = False
            except Exception as e:
                st.warning(f"Error with real calculator: {e}. Using fallback.")
                results = calculate_credit_score_dummy(
                    dscr, current_ratio, debt_ebitda, revenue_growth,
                    gross_margin, years_operating, industry
                )
                using_real_calc = False
        else:
            results = calculate_credit_score_dummy(
                dscr, current_ratio, debt_ebitda, revenue_growth,
                gross_margin, years_operating, industry
            )
            using_real_calc = False

        st.markdown("---")
        st.markdown("## 📈 Credit Analysis Results")

        # Top-level metrics
        result_col1, result_col2, result_col3 = st.columns([1, 1, 1])

        with result_col1:
            # Color-code score
            if results['rating'] == 'A':
                score_color = "normal"
            elif results['rating'] == 'B':
                score_color = "normal"
            else:
                score_color = "inverse"

            st.metric(
                "Credit Score",
                f"{results['score']}/100",
                delta=f"{results['rating']} Rating",
                delta_color=score_color
            )

        with result_col2:
            st.metric(
                "Risk Assessment",
                results['risk_level'],
                delta=None
            )

        with result_col3:
            st.metric(
                "Industry",
                industry,
                delta=f"{years_operating} years"
            )

        # Credit gauge visualization
        st.markdown("---")
        gauge_col1, gauge_col2 = st.columns([1, 1])

        with gauge_col1:
            fig_gauge = create_credit_gauge(results['score'], results['rating'])
            st.plotly_chart(fig_gauge, use_container_width=True)

        with gauge_col2:
            st.markdown("#### 📊 Sub-Score Breakdown")

            # Financial Health
            st.markdown("**Financial Health**")
            st.progress(results['financial_health'] / 100)
            st.caption(f"{results['financial_health']}/100")

            # Cash Flow Coverage
            st.markdown("**Cash Flow Coverage**")
            st.progress(results['cash_flow'] / 100)
            st.caption(f"{results['cash_flow']}/100")

            # Revenue Stability
            st.markdown("**Revenue Stability**")
            st.progress(results['revenue_stability'] / 100)
            st.caption(f"{results['revenue_stability']}/100")

            # Management Quality
            st.markdown("**Management Quality**")
            st.progress(results['management_quality'] / 100)
            st.caption(f"{results['management_quality']}/100")

        st.markdown("---")

        # Recommendations
        st.markdown("### ✅ Security Recommendations")

        rec_col1, rec_col2 = st.columns([1, 1])

        with rec_col1:
            st.markdown("#### Required Security Measures")
            for rec in results['recommendations']:
                st.markdown(f"- ✓ {rec}")

        with rec_col2:
            st.markdown("#### Risk Mitigation")

            if results['score'] >= 70:
                st.success("""
                **Low to Moderate Risk**
                - Standard lease terms acceptable
                - Monitor financial performance annually
                - Request updated financials yearly
                """)
            elif results['score'] >= 50:
                st.warning("""
                **Moderate to Elevated Risk**
                - Enhanced security required
                - Quarterly financial monitoring
                - Consider shorter lease term
                - Evaluate personal guarantee value
                """)
            else:
                st.error("""
                **High Risk**
                - Maximum security required
                - Monthly financial reporting
                - Consider declining tenant
                - If proceeding: Full personal guarantee + 6mo deposit
                - Shorter term with frequent renewals
                """)

        st.markdown("---")

        # Detailed Financial Analysis
        st.markdown("### 📋 Detailed Financial Analysis")

        analysis_data = {
            "Metric": [
                "DSCR (Debt Service Coverage)",
                "Current Ratio (Liquidity)",
                "Debt-to-EBITDA (Leverage)",
                "Interest Coverage Ratio",
                "Revenue Growth Rate",
                "Gross Margin",
                "Years in Business"
            ],
            "Value": [
                f"{dscr:.2f}x",
                f"{current_ratio:.2f}x",
                f"{debt_ebitda:.2f}x",
                f"{icr:.2f}x",
                f"{revenue_growth:.1f}%",
                f"{gross_margin:.1f}%",
                f"{years_operating} years"
            ],
            "Benchmark": [
                ">1.25x (Healthy)",
                ">1.5x (Healthy)",
                "<3.0x (Healthy)",
                ">3.0x (Healthy)",
                ">5% (Good)",
                ">40% (Good)",
                ">3 years (Stable)"
            ],
            "Status": [
                "✅ Strong" if dscr >= 1.25 else "⚠️ Weak",
                "✅ Strong" if current_ratio >= 1.5 else "⚠️ Weak",
                "✅ Strong" if debt_ebitda <= 3.0 else "⚠️ Weak",
                "✅ Strong" if icr >= 3.0 else "⚠️ Weak",
                "✅ Strong" if revenue_growth >= 5 else "⚠️ Weak",
                "✅ Strong" if gross_margin >= 40 else "⚠️ Weak",
                "✅ Established" if years_operating >= 3 else "⚠️ Early Stage"
            ]
        }

        st.dataframe(
            pd.DataFrame(analysis_data),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Export Options
        st.markdown("### 📥 Export Credit Report")

        export_col1, export_col2, export_col3 = st.columns(3)

        with export_col1:
            if st.button("📊 Export to Excel", use_container_width=True):
                st.info("Excel export coming soon")

        with export_col2:
            if st.button("📄 Generate PDF Report", use_container_width=True):
                st.info("PDF report coming soon")

        with export_col3:
            if st.button("💾 Save to Reports Vault", use_container_width=True):
                st.info("Vault integration coming soon")

        # Show which calculator was used
        calc_badge = "🔬 Real Calculator" if using_real_calc else "🧪 Demo Mode"
        st.info(f"ℹ️ Analysis performed using: {calc_badge}")

else:
    st.info("👆 Fill in the tenant information above and click 'Analyze Credit' to generate the credit assessment")

    # Show methodology
    st.markdown("---")
    st.markdown("### 📖 Credit Scoring Methodology")

    method_col1, method_col2 = st.columns(2)

    with method_col1:
        st.markdown("""
        **Scoring Components:**
        - **Financial Health (30%)** - DSCR and Current Ratio
        - **Cash Flow Coverage (25%)** - Ability to service debt
        - **Revenue Stability (25%)** - Growth and margins
        - **Management Quality (20%)** - Years in business and track record

        **Rating Scale:**
        - **A (80-100)**: Low risk - minimal security
        - **B (60-79)**: Acceptable risk - standard security
        - **C (40-59)**: Elevated risk - enhanced security
        - **D (<40)**: High risk - maximum security or decline
        """)

    with method_col2:
        st.markdown("""
        **Key Benchmarks:**
        - **DSCR**: >1.25x indicates healthy cash flow
        - **Current Ratio**: >1.5x indicates good liquidity
        - **Debt/EBITDA**: <3.0x indicates manageable leverage
        - **ICR**: >3.0x indicates strong interest coverage
        - **Revenue Growth**: >5% year-over-year
        - **Gross Margin**: >40% indicates profitability

        **Security Options:**
        - Personal guarantee
        - Corporate guarantee
        - Security deposit (1-6 months)
        - Letter of credit
        - Financial covenants
        """)

# Sidebar
with st.sidebar:
    st.markdown("### 📖 About This Tool")

    st.info("""
    **Tenant Credit Analysis**

    Institutional-grade credit scoring for commercial real estate tenants.

    **Uses:**
    - Pre-lease credit assessment
    - Ongoing tenant monitoring
    - Security requirement determination
    - Risk management
    """)

    st.markdown("---")

    st.markdown("### 💡 Tips")
    st.markdown("""
    **Best Practices:**
    - Request 3 years of financials
    - Verify revenue with tax returns
    - Check industry benchmarks
    - Consider lease as % of revenue
    - Assess management experience
    - Review payment history
    """)

    st.markdown("---")

    st.markdown("### 🔗 Related Tools")
    st.markdown("""
    - **Effective Rent** - Deal economics
    - **Default Analysis** - Default scenarios
    - **Assignment Consent** - Evaluate assignees
    """)
