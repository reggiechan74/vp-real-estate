"""
Plotly chart templates for VP Real Estate Platform
Interactive visualizations for financial analysis
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def create_cash_flow_chart(monthly_data):
    """
    Create monthly cash flow bar chart

    Args:
        monthly_data: DataFrame with 'month', 'cash_flow', 'cumulative' columns

    Returns:
        plotly Figure
    """
    fig = go.Figure()

    # Monthly cash flow bars
    fig.add_trace(go.Bar(
        x=monthly_data['month'],
        y=monthly_data['cash_flow'],
        name='Monthly Cash Flow',
        marker_color='#3b82f6',
        hovertemplate='<b>Month %{x}</b><br>Cash Flow: $%{y:,.0f}<extra></extra>'
    ))

    # Cumulative line
    fig.add_trace(go.Scatter(
        x=monthly_data['month'],
        y=monthly_data['cumulative'],
        name='Cumulative Cash Flow',
        mode='lines+markers',
        line=dict(color='#d97706', width=3),
        marker=dict(size=6),
        yaxis='y2',
        hovertemplate='<b>Month %{x}</b><br>Cumulative: $%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='Monthly Cash Flow Analysis',
        xaxis=dict(
            title='Month',
            showgrid=True,
            gridcolor='#e2e8f0'
        ),
        yaxis=dict(
            title='Monthly Cash Flow ($)',
            showgrid=True,
            gridcolor='#e2e8f0',
            tickformat='$,.0f'
        ),
        yaxis2=dict(
            title='Cumulative Cash Flow ($)',
            overlaying='y',
            side='right',
            showgrid=False,
            tickformat='$,.0f'
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=500
    )

    return fig


def create_sensitivity_heatmap(rent_range=None, ti_range=None):
    """
    Create NER sensitivity heatmap (Base Rent vs TI Allowance)

    Args:
        rent_range: tuple (min, max) for rent, defaults to (20, 35)
        ti_range: tuple (min, max) for TI, defaults to (15, 35)

    Returns:
        plotly Figure
    """
    if rent_range is None:
        rent_range = (20, 35)
    if ti_range is None:
        ti_range = (15, 35)

    # Generate sensitivity data
    rent_values = np.linspace(rent_range[0], rent_range[1], 15)
    ti_values = np.linspace(ti_range[0], ti_range[1], 15)

    # Calculate NER matrix (simplified calculation)
    ner_matrix = np.zeros((len(rent_values), len(ti_values)))

    for i, rent in enumerate(rent_values):
        for j, ti in enumerate(ti_values):
            # Simplified NER calculation
            ner_matrix[i, j] = rent - (ti / 5)  # Very simplified

    fig = go.Figure(data=go.Heatmap(
        z=ner_matrix,
        x=ti_values,
        y=rent_values,
        colorscale='RdYlGn',
        hovertemplate='Base Rent: $%{y:.2f}/SF<br>TI Allowance: $%{x:.2f}/SF<br>NER: $%{z:.2f}/SF<extra></extra>',
        colorbar=dict(title='NER ($/SF)')
    ))

    fig.update_layout(
        title='Net Effective Rent Sensitivity Analysis',
        xaxis=dict(
            title='TI Allowance ($/SF)',
            showgrid=True,
            gridcolor='#cbd5e1'
        ),
        yaxis=dict(
            title='Base Rent ($/SF)',
            showgrid=True,
            gridcolor='#cbd5e1'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        height=500
    )

    return fig


def create_radar_chart(variables, scores, title="Property Analysis"):
    """
    Create radar chart for multi-variable analysis (MCDA)

    Args:
        variables: list of variable names
        scores: list of scores (0-10) corresponding to variables
        title: Chart title

    Returns:
        plotly Figure
    """
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=variables,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#3b82f6', width=2),
        marker=dict(size=8, color='#3b82f6'),
        name='Subject Property',
        hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}/10<extra></extra>'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                showgrid=True,
                gridcolor='#e2e8f0',
                tickfont=dict(size=10)
            ),
            angularaxis=dict(
                showgrid=True,
                gridcolor='#e2e8f0',
                tickfont=dict(size=11, family='Inter, sans-serif')
            ),
            bgcolor='white'
        ),
        showlegend=False,
        title=dict(
            text=title,
            font=dict(size=18, family='Inter, sans-serif', color='#0f172a')
        ),
        paper_bgcolor='white',
        height=600
    )

    return fig


def create_scatter_plot(df, x_col, y_col, color_col=None, title="Comparison"):
    """
    Create scatter plot for competitive positioning

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        color_col: Optional column for color coding
        title: Chart title

    Returns:
        plotly Figure
    """
    if color_col:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            hover_data=df.columns,
            title=title,
            labels={x_col: x_col.replace('_', ' ').title(),
                   y_col: y_col.replace('_', ' ').title()}
        )
    else:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            hover_data=df.columns,
            title=title,
            labels={x_col: x_col.replace('_', ' ').title(),
                   y_col: y_col.replace('_', ' ').title()}
        )

    fig.update_traces(
        marker=dict(size=12, line=dict(width=2, color='white'))
    )

    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        xaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
        yaxis=dict(showgrid=True, gridcolor='#e2e8f0'),
        height=500
    )

    return fig


def create_waterfall_chart(categories, values, title="Deal Economics"):
    """
    Create waterfall chart for deal analysis

    Args:
        categories: list of category names
        values: list of values (positive or negative)
        title: Chart title

    Returns:
        plotly Figure
    """
    fig = go.Figure(go.Waterfall(
        name="Deal",
        orientation="v",
        measure=["relative"] * (len(categories) - 1) + ["total"],
        x=categories,
        y=values,
        text=[f"${v:,.0f}" for v in values],
        textposition="outside",
        connector=dict(line=dict(color="#cbd5e1")),
        increasing=dict(marker=dict(color="#10b981")),
        decreasing=dict(marker=dict(color="#dc2626")),
        totals=dict(marker=dict(color="#3b82f6"))
    ))

    fig.update_layout(
        title=title,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        xaxis=dict(showgrid=False),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0',
            tickformat='$,.0f'
        ),
        height=500
    )

    return fig


def create_amortization_chart(schedule_df):
    """
    Create IFRS 16 amortization chart (Liability vs ROU Asset)

    Args:
        schedule_df: DataFrame with 'Month', 'Interest', 'Principal', 'Balance' columns

    Returns:
        plotly Figure
    """
    fig = go.Figure()

    # Liability balance line
    fig.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=schedule_df['Balance'],
        mode='lines+markers',
        name='Lease Liability',
        line=dict(color='#dc2626', width=3),
        marker=dict(size=6),
        hovertemplate='<b>Month %{x}</b><br>Liability: $%{y:,.0f}<extra></extra>'
    ))

    # ROU Asset (simplified - same as initial liability, straight-line depreciation)
    initial_balance = schedule_df['Balance'].iloc[0] + schedule_df['Principal'].iloc[0]
    monthly_depreciation = initial_balance / len(schedule_df)
    rou_values = [initial_balance - (i * monthly_depreciation) for i in range(len(schedule_df))]

    fig.add_trace(go.Scatter(
        x=schedule_df['Month'],
        y=rou_values,
        mode='lines+markers',
        name='ROU Asset',
        line=dict(color='#3b82f6', width=3, dash='dash'),
        marker=dict(size=6),
        hovertemplate='<b>Month %{x}</b><br>ROU Asset: $%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(
        title='IFRS 16 Lease Liability vs ROU Asset',
        xaxis=dict(
            title='Month',
            showgrid=True,
            gridcolor='#e2e8f0'
        ),
        yaxis=dict(
            title='Balance ($)',
            showgrid=True,
            gridcolor='#e2e8f0',
            tickformat='$,.0f'
        ),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=500
    )

    return fig


def create_credit_gauge(score, rating):
    """
    Create gauge chart for credit score

    Args:
        score: Credit score (0-100)
        rating: Letter rating (A, B, C, D)

    Returns:
        plotly Figure
    """
    # Color based on rating
    if rating == "A":
        color = "#10b981"  # Green
    elif rating == "B":
        color = "#3b82f6"  # Blue
    elif rating == "C":
        color = "#f59e0b"  # Orange
    else:
        color = "#dc2626"  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Credit Score<br><span style='font-size:0.8em;color:#64748b'>Rating: {rating}</span>"},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, 40], 'color': '#fee2e2'},
                {'range': [40, 60], 'color': '#fef3c7'},
                {'range': [60, 80], 'color': '#dbeafe'},
                {'range': [80, 100], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "#0f172a", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif', color='#0f172a'),
        height=400
    )

    return fig


def create_comparison_bars(comparison_data):
    """
    Create grouped bar chart for document comparison

    Args:
        comparison_data: list of dicts with 'section', 'document_a', 'document_b' (numeric values)

    Returns:
        plotly Figure
    """
    sections = [item['section'] for item in comparison_data]
    doc_a = [float(item.get('document_a', 0)) for item in comparison_data]
    doc_b = [float(item.get('document_b', 0)) for item in comparison_data]

    fig = go.Figure(data=[
        go.Bar(name='Original', x=sections, y=doc_a, marker_color='#94a3b8'),
        go.Bar(name='Amended', x=sections, y=doc_b, marker_color='#3b82f6')
    ])

    fig.update_layout(
        barmode='group',
        title='Document Comparison',
        xaxis=dict(title='Section', showgrid=False),
        yaxis=dict(title='Value', showgrid=True, gridcolor='#e2e8f0'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        height=500
    )

    return fig


def create_portfolio_donut(data_dict, title="Portfolio Composition"):
    """
    Create donut chart for portfolio breakdown

    Args:
        data_dict: dict with labels as keys and values
        title: Chart title

    Returns:
        plotly Figure
    """
    labels = list(data_dict.keys())
    values = list(data_dict.values())

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(
            colors=['#3b82f6', '#d97706', '#059669', '#64748b', '#dc2626'],
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{label}</b><br>%{value:,.0f}<br>%{percent}<extra></extra>',
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, family='Inter, sans-serif', color='#0f172a')
        ),
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.05
        ),
        height=500
    )

    return fig
