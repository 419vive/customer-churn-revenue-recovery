#!/usr/bin/env python
"""
Dashboard Preview Generator
Create static preview images of the dashboard charts
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import os

def create_dashboard_previews():
    """Generate sample charts as preview images"""
    
    print("📊 Generating Dashboard Preview Charts...")
    
    # Create sample data
    np.random.seed(42)
    
    # Sample RFM data
    segments = ['Champions', 'Loyal Customers', 'Big Spenders', 'At Risk', 'Lost', 'Regular']
    segment_counts = [50, 36, 25, 47, 67, 62]
    segment_colors = ['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6', '#34495e']
    
    rfm_data = pd.DataFrame({
        'customer_id': [f'customer_{i:04d}' for i in range(287)],
        'recency': np.random.randint(1, 365, 287),
        'frequency': np.random.randint(1, 10, 287),
        'monetary': np.random.uniform(100, 2000, 287),
        'segment': np.random.choice(segments, 287, p=[0.17, 0.12, 0.09, 0.16, 0.23, 0.23])
    })
    
    # 1. Customer Segment Donut Chart
    donut_fig = go.Figure(data=[go.Pie(
        labels=segments,
        values=segment_counts,
        hole=.5,
        textinfo="label+percent",
        textposition="outside",
        marker=dict(colors=segment_colors)
    )])
    
    donut_fig.update_layout(
        title={
            'text': "Customer Segment Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Segoe UI'}
        },
        showlegend=True,
        height=500,
        width=700,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50', 'size': 12, 'family': 'Segoe UI'},
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    donut_fig.update_traces(textfont={'size': 14})
    
    # Save chart
    os.makedirs('dashboard_previews', exist_ok=True)
    donut_fig.write_html("dashboard_previews/segment_distribution.html")
    print("✅ Segment distribution chart saved")
    
    # 2. RFM Scatter Plot
    rfm_scatter = px.scatter(
        rfm_data, 
        x='recency', 
        y='frequency',
        size='monetary',
        color='segment',
        title="RFM Customer Segmentation Analysis",
        labels={
            'recency': 'Recency (days since last order)',
            'frequency': 'Frequency (total orders)',
            'monetary': 'Monetary (total spent $)'
        },
        color_discrete_sequence=segment_colors,
        hover_data=['customer_id']
    )
    
    rfm_scatter.update_layout(
        title={
            'text': "RFM Customer Segmentation Analysis",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Segoe UI'}
        },
        height=600,
        width=900,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50', 'family': 'Segoe UI'},
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True)
    )
    
    rfm_scatter.write_html("dashboard_previews/rfm_scatter.html")
    print("✅ RFM scatter plot saved")
    
    # 3. Cohort Retention Heatmap
    months = ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06']
    retention_data = np.array([
        [100.0, 32.9, 15.7, 28.6, 25.7, 20.1],
        [100.0, 16.4, 29.1, 30.9, 25.5, 22.3],
        [100.0, 29.4, 23.5, 35.3, 29.4, 25.8],
        [100.0, 14.3, 17.1, 11.4, 25.7, 18.9],
        [100.0, 23.5, 23.5, 26.5, 26.5, 24.1],
        [100.0, 38.5, 30.8, 30.8, 23.1, 21.7]
    ])
    
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=retention_data,
        x=[f"Month {i}" for i in range(6)],
        y=months,
        colorscale='RdYlBu_r',
        text=retention_data,
        texttemplate="%{text:.1f}%",
        textfont={"size": 12, "color": "white"},
        colorbar=dict(title="Retention Rate (%)")
    ))
    
    heatmap_fig.update_layout(
        title={
            'text': "Customer Retention Cohort Analysis",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Segoe UI'}
        },
        xaxis_title="Periods Since First Purchase",
        yaxis_title="Cohort (First Purchase Month)",
        height=500,
        width=800,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50', 'family': 'Segoe UI'}
    )
    
    heatmap_fig.write_html("dashboard_previews/cohort_heatmap.html")
    print("✅ Cohort heatmap saved")
    
    # 4. LTV Distribution
    ltv_values = np.random.lognormal(mean=6, sigma=0.8, size=287)
    ltv_hist = px.histogram(
        x=ltv_values,
        nbins=30,
        title="Customer Lifetime Value Distribution",
        labels={'x': 'Customer LTV ($)', 'count': 'Number of Customers'},
        color_discrete_sequence=['#3498db']
    )
    
    ltv_hist.update_layout(
        title={
            'text': "Customer Lifetime Value Distribution",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Segoe UI'}
        },
        height=500,
        width=800,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#2c3e50', 'family': 'Segoe UI'},
        xaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        yaxis=dict(gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        bargap=0.1
    )
    
    ltv_hist.write_html("dashboard_previews/ltv_distribution.html")
    print("✅ LTV distribution chart saved")
    
    # Create index file for easy viewing
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Olist Dashboard Preview</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 40px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { 
                text-align: center; 
                margin-bottom: 40px; 
                padding: 40px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            .chart { 
                margin: 30px 0; 
                padding: 20px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            iframe { 
                width: 100%; 
                height: 600px; 
                border: none;
                border-radius: 10px;
            }
            h1 { font-size: 2.5rem; margin: 0; font-weight: 300; }
            h2 { color: #2c3e50; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Olist Analytics Dashboard Preview</h1>
                <p>Interactive data visualization showcase</p>
            </div>
            
            <div class="chart">
                <h2>Customer Segment Distribution</h2>
                <iframe src="segment_distribution.html"></iframe>
            </div>
            
            <div class="chart">
                <h2>RFM Customer Segmentation</h2>
                <iframe src="rfm_scatter.html"></iframe>
            </div>
            
            <div class="chart">
                <h2>Cohort Retention Analysis</h2>
                <iframe src="cohort_heatmap.html"></iframe>
            </div>
            
            <div class="chart">
                <h2>Customer Lifetime Value Distribution</h2>
                <iframe src="ltv_distribution.html"></iframe>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open("dashboard_previews/index.html", "w") as f:
        f.write(index_html)
    
    print("\n🎉 Dashboard preview generated successfully!")
    print(f"📂 Open: {os.path.abspath('dashboard_previews/index.html')}")
    print("\n📊 Preview includes:")
    print("  - Customer Segment Distribution (Donut Chart)")
    print("  - RFM Segmentation Scatter Plot")
    print("  - Cohort Retention Heatmap")
    print("  - LTV Distribution Histogram")
    
    return os.path.abspath('dashboard_previews/index.html')

if __name__ == "__main__":
    create_dashboard_previews()