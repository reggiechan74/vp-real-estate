# VP Real Estate Platform - Streamlit UI

**Institutional Real Estate Command Center** - Professional web interface for comprehensive lease analysis and portfolio management.

## Overview

This Streamlit application provides a production-ready UI for the VP Real Estate Platform, featuring:

- **Dashboard** - Portfolio metrics, quick actions, and alerts
- **Team Room** - Chat with 3 AI personas (Adam, Reggie, Dennis)
- **Financial Analysis** - 6 calculators with interactive visualizations
- **Lease Processing** - Document abstraction and analysis
- **Reports Vault** - Browse, search, and export generated reports

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### 3. Navigate the Platform

Use the sidebar to navigate between:
- 🏠 Dashboard (Home)
- 👥 Team Room (Chat)
- 💰 Effective Rent Calculator
- 🏦 Tenant Credit Analysis
- 📋 Lease Abstraction
- 🎯 Relative Valuation (MCDA)
- 🗄️ Reports Vault

## Features

### Dashboard
- Portfolio overview metrics (GLA, ARR, Occupancy, WALT)
- Quick action buttons
- Recent activity feed
- Critical alerts and deadlines
- System status

### Team Room
Chat with three specialized AI personas:

1. **Adam (Analyst)** - Fast, diplomatic, 80/20 analysis
   - Use for: Standard lease reviews, routine credit checks
   - Model: Haiku (fast execution)

2. **Reggie (VP)** - Deep expertise, forensic analysis
   - Use for: Complex situations, crisis turnarounds, fraud detection
   - Model: Sonnet (comprehensive analysis)
   - Credentials: CFA, FRICS, 20+ years experience

3. **Dennis (Advisor)** - Strategic wisdom, reality checks
   - Use for: Career decisions, negotiation psychology, tough love
   - Model: Opus (strategic depth)
   - Experience: 36+ years, former president

### Financial Calculators

#### 1. Effective Rent Calculator
- Net Effective Rent (NER) & Gross Effective Rent (GER)
- NPV and IRR analysis
- Breakeven calculation
- Interactive cash flow charts
- Sensitivity heatmaps
- Waterfall charts

#### 2. Tenant Credit Analysis
- Credit scoring (0-100 scale with A-D ratings)
- DSCR, Current Ratio, Debt/EBITDA analysis
- Risk assessment and security recommendations
- Visual credit gauge
- Sub-score breakdown
- Detailed financial analysis table

#### 3. Lease Abstraction
- 24-section comprehensive lease analysis
- Industrial & Office property types
- BOMA measurement standards
- Critical dates extraction
- Special provisions (Schedule G) highlighting
- JSON export functionality

#### 4. Relative Valuation (MCDA)
- 25-variable competitive analysis
- 5 category scoring (Location, Building, Financial, Operational, Market)
- Weighted scoring methodology
- Radar chart visualization
- Competitive landscape positioning
- Strategic pricing recommendations

### Reports Vault
- Browse all generated reports
- Full-text search
- Date range filtering
- Tag-based organization
- List, Card, and Timeline views
- Bulk export functionality

## Design Philosophy

**Vibe:** Institutional Real Estate Excellence
- Clean, high-contrast, data-dense but scannable
- Professional Bloomberg Terminal meets modern SaaS
- "Serious money, serious tools" aesthetic
- Zero fluff, maximum information density
- Keyboard-first power user workflows

**Color Palette: Navy & Slate Pro**
- Primary Navy: `#0f172a` (Trust, Finance, Authority)
- Gold Accent: `#d97706` (Reggie's Insights, Warnings)
- Steel Blue: `#3b82f6` (Adam's Analysis, Information)
- Sage Green: `#059669` (Dennis's Wisdom, Success)

**Typography:**
- Headings: Inter Bold (Modern, Professional)
- Body: Inter Regular (Highly readable)
- Data/Numbers: JetBrains Mono (Monospaced for financial data)

## Project Structure

```
lease-abstract/
├── app.py                          # Main entry point (Dashboard)
├── pages/                          # Streamlit pages (auto-navigation)
│   ├── 01_👥_Team_Room.py         # AI Chat interface
│   ├── 02_💰_Effective_Rent_Calculator.py
│   ├── 03_🏦_Tenant_Credit_Analysis.py
│   ├── 04_📋_Lease_Abstraction.py
│   ├── 05_🎯_Relative_Valuation.py
│   └── 06_🗄️_Reports_Vault.py
├── utils/                          # Utility modules
│   ├── styling.py                  # Custom CSS & theme
│   ├── personas.py                 # AI persona definitions
│   ├── dummy_functions.py          # Placeholder calculations
│   └── charts.py                   # Plotly chart templates
├── requirements.txt                # Python dependencies
└── README_STREAMLIT_UI.md         # This file
```

## Current Status

**Phase 1: UI Foundation** ✅ COMPLETE

This is a fully functional UI with dummy backend calculations. All forms, visualizations, and navigation work perfectly.

**Next Steps:**
- Phase 2: Connect to actual Python calculators in the repository
- Phase 3: Integrate AI personas with LLM backend
- Phase 4: Add file processing pipelines
- Phase 5: Deploy to cloud (Streamlit Cloud, AWS, or Azure)

## Usage Tips

### Portfolio Metrics (Dashboard)
- Metrics are currently using sample data
- In production, these will connect to your portfolio database

### Calculators
- All input forms are fully functional
- Calculations use simplified placeholder logic
- Charts and visualizations display properly
- Export functionality is stubbed (shows "coming soon")

### File Uploads
- Lease Abstraction accepts PDF/DOCX uploads
- File processing is simulated (returns mock 24-section abstract)
- JSON export works (downloads mock data)

### Chat (Team Room)
- Chat interface works with message history
- Responses are placeholder text
- In production, will connect to OpenAI/Anthropic API
- Each persona maintains separate conversation history

## Customization

### Modify Colors
Edit `utils/styling.py` to change the color palette:

```python
:root {
    --primary-navy: #0f172a;
    --gold-accent: #d97706;
    --steel-blue: #3b82f6;
    --sage-green: #059669;
}
```

### Add New Pages
1. Create a new file in `pages/` directory
2. Use naming convention: `##_Emoji_Page_Name.py`
3. Streamlit will automatically add it to navigation

Example:
```python
# pages/07_📊_New_Calculator.py
import streamlit as st

st.set_page_config(page_title="New Calculator", page_icon="📊")
st.title("📊 New Calculator")
# Your content here
```

### Modify Dashboard Metrics
Edit `app.py` session state initialization:

```python
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = {
        'total_gla': 2_400_000,  # Change these values
        'arr': 48_200_000,
        'occupancy': 94.2,
        # ...
    }
```

## Deployment Options

### Streamlit Cloud (Fastest)
```bash
# 1. Push to GitHub
# 2. Go to share.streamlit.io
# 3. Connect repository
# 4. Deploy!
```

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### AWS / Azure
See deployment guides in main documentation.

## Troubleshooting

### Issue: Pages not showing in sidebar
**Solution:** Ensure files in `pages/` directory follow naming convention `##_Name.py`

### Issue: Charts not displaying
**Solution:** Check that plotly is installed: `pip install plotly>=5.17.0`

### Issue: Styling not applied
**Solution:** Clear browser cache and refresh. Streamlit caches CSS.

### Issue: File upload not working
**Solution:** Check file size limits in Streamlit config (default 200MB)

## Support

- **Documentation:** See main `CLAUDE.md` in repository root
- **Issues:** Report at GitHub repository
- **Questions:** Use Team Room chat (in production) or contact maintainers

## License

Part of the VP Real Estate Platform - Institutional lease analysis toolkit.

---

**Built with Claude Code** | Streamlit UI Framework | Institutional-Grade Design

For complete platform documentation, see `/workspaces/lease-abstract/CLAUDE.md`
