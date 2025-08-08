#!/usr/bin/env python
"""
Simple Dashboard Test - Standalone Version
"""
import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
segments = ['Champions', 'Loyal', 'At Risk', 'Lost', 'New']
sample_data = pd.DataFrame({
    'segment': np.random.choice(segments, 100),
    'recency': np.random.randint(1, 365, 100),
    'frequency': np.random.randint(1, 10, 100),
    'monetary': np.random.uniform(100, 2000, 100)
})

# Create Dash app
app = dash.Dash(__name__)

# Sample chart
fig = px.scatter(
    sample_data, 
    x='recency', 
    y='frequency',
    color='segment',
    size='monetary',
    title="Customer Segmentation with Plain English Explanations"
)

app.layout = html.Div([
    html.H1("🎉 Enhanced Analytics Dashboard", 
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Plain English Explanation Section
    html.Div([
        html.H3("💡 What This Means for Your Business", 
                style={'color': '#27ae60', 'marginBottom': 15}),
        html.P([
            "This scatter plot shows your customers in different groups. ",
            html.Strong("LEFT side = recent customers"), ", ",
            html.Strong("RIGHT side = old customers"), ". ",
            html.Strong("TOP = frequent buyers"), ", ",
            html.Strong("BOTTOM = rare buyers"), "."
        ], style={'fontSize': 16, 'lineHeight': 1.6, 'marginBottom': 15}),
        
        html.Div([
            html.H4("🎯 Your Action Plan:", style={'color': '#e74c3c'}),
            html.Ul([
                html.Li("Champions (blue dots): Your best customers - give them VIP treatment!"),
                html.Li("At Risk (red dots): Send them special offers before they leave"),
                html.Li("Lost customers: Try win-back campaigns with discounts"),
            ])
        ], className="alert alert-info")
    ], style={'backgroundColor': '#f8f9fa', 'padding': 20, 'borderRadius': 10, 'margin': 20}),
    
    # Chart
    dcc.Graph(figure=fig),
    
    # More explanations
    html.Div([
        html.H4("📊 How to Read This Chart:", style={'color': '#8e44ad'}),
        html.P("Each dot is a customer. Bigger dots = higher spending. Colors show different customer types."),
        html.Hr(),
        html.P("✅ This enhanced dashboard includes plain English explanations for all charts!", 
               style={'fontWeight': 'bold', 'color': '#27ae60', 'textAlign': 'center'})
    ], style={'backgroundColor': '#fff3cd', 'padding': 15, 'borderRadius': 8, 'margin': 20})
])

if __name__ == '__main__':
    print("🚀 Starting Simple Dashboard Demo...")
    print("📊 Available at: http://127.0.0.1:8051")
    print("💡 This version shows the enhanced explanations!")
    app.run(debug=True, port=8051, host='127.0.0.1')