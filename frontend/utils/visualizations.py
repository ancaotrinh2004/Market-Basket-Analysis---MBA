"""
Visualization utilities
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict, Any

def plot_top_items(items: List[Dict[str, Any]], title: str = "Top Items"):
    """Bar chart for top items"""
    df = pd.DataFrame(items)
    
    if df.empty:
        return None
    
    fig = px.bar(
        df,
        x='frequency',
        y='item_name',
        orientation='h',
        title=title,
        labels={'frequency': 'Frequency', 'item_name': 'Item'},
        color='frequency',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def plot_distribution(data: List[float], column: str, title: str):
    """Histogram for distribution"""
    df = pd.DataFrame({column: data})
    
    fig = px.histogram(
        df,
        x=column,
        nbins=30,
        title=title,
        labels={column: column.capitalize()},
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_layout(
        showlegend=False,
        bargap=0.1
    )
    
    return fig

def plot_scatter(rules: List[Dict[str, Any]]):
    """Scatter plot: Confidence vs Lift"""
    df = pd.DataFrame(rules)
    
    if df.empty:
        return None
    
    fig = px.scatter(
        df,
        x='confidence',
        y='lift',
        size='support',
        hover_data=['antecedent', 'consequent'],
        title='Association Rules: Confidence vs Lift',
        labels={'confidence': 'Confidence', 'lift': 'Lift', 'support': 'Support'},
        color='lift',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(height=600)
    
    return fig

def plot_recommendation_scores(recommendations: List[Dict[str, Any]]):
    """Bar chart for recommendation scores"""
    df = pd.DataFrame(recommendations)
    
    if df.empty:
        return None
    
    fig = go.Figure()
    
    # Lift bars
    fig.add_trace(go.Bar(
        name='Lift Score',
        x=df['item_name'],
        y=df['lift'],
        marker_color='lightblue'
    ))
    
    # Confidence bars
    fig.add_trace(go.Bar(
        name='Confidence',
        x=df['item_name'],
        y=df['confidence'],
        marker_color='lightcoral'
    ))
    
    fig.update_layout(
        title='Recommendation Scores',
        xaxis_title='Recommended Items',
        yaxis_title='Score',
        barmode='group',
        height=400
    )
    
    return fig

def create_metrics_cards(stats: Dict[str, Any]):
    """Create metric cards HTML"""
    return f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0;">
        <div class="metric-card">
            <h3>📊 Total Rules</h3>
            <h2>{stats.get('total_rules', 0):,}</h2>
        </div>
        <div class="metric-card">
            <h3>🎯 Avg Confidence</h3>
            <h2>{stats.get('avg_confidence', 0):.2%}</h2>
        </div>
        <div class="metric-card">
            <h3>📈 Avg Lift</h3>
            <h2>{stats.get('avg_lift', 0):.2f}</h2>
        </div>
    </div>
    """