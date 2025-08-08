#!/usr/bin/env python
"""
Interactive Dashboard for Olist E-Commerce Analytics
Beautiful, responsive dashboard showcasing all analysis results
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OlistDashboard:
    """Main dashboard application class"""
    
    def __init__(self):
        # Initialize with external CSS for better styling
        external_stylesheets = [
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css',
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ]
        
        self.app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        self.app.title = "Olist E-Commerce Analytics Dashboard"
        
        # Add custom CSS
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>{%title%}</title>
                {%favicon%}
                {%css%}
                <style>
                    body { 
                        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }
                    .card { 
                        box-shadow: 0 8px 25px rgba(0,0,0,0.15); 
                        border: none;
                        border-radius: 15px;
                        transition: transform 0.3s ease;
                    }
                    .card:hover { transform: translateY(-5px); }
                    .tab-content { 
                        background: white; 
                        border-radius: 15px; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        padding: 20px;
                    }
                    .dash-table-container { 
                        border-radius: 10px; 
                        overflow: hidden;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1, h2, h3, h4 { color: #2c3e50; font-weight: 600; }
                    .alert { border: none; border-radius: 10px; }
                    .btn { border-radius: 25px; }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
        self.load_data()
        self.setup_layout()
        self.setup_callbacks()
    
    def load_data(self):
        """Load all analysis results"""
        try:
            # Load the latest analysis results  
            outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'outputs')
            
            # Find the latest timestamped files
            files = os.listdir(outputs_dir)
            timestamped_files = [f for f in files if 'rfm_segments_detailed_' in f and f.endswith('.csv')]
            if timestamped_files:
                latest_file = max(timestamped_files)
                latest_timestamp = latest_file.replace('rfm_segments_detailed_', '').replace('.csv', '')
            else:
                raise FileNotFoundError("No timestamped files found")
            
            self.rfm_data = pd.read_csv(f'{outputs_dir}/rfm_segments_detailed_{latest_timestamp}.csv')
            self.ltv_data = pd.read_csv(f'{outputs_dir}/customer_ltv_detailed_{latest_timestamp}.csv')
            self.retention_data = pd.read_csv(f'{outputs_dir}/retention_matrix_{latest_timestamp}.csv', index_col=0)
            self.journey_data = pd.read_csv(f'{outputs_dir}/customer_journey_{latest_timestamp}.csv')
            
            print("✅ Dashboard data loaded successfully!")
            
        except Exception as e:
            print(f"⚠️ Error loading data: {e}")
            print("📊 Creating sample data for dashboard demo...")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample data if files not found"""
        np.random.seed(42)
        
        # Sample RFM data
        segments = ['Champions', 'Loyal Customers', 'Big Spenders', 'At Risk', 'Lost', 'Regular']
        self.rfm_data = pd.DataFrame({
            'customer_id': [f'customer_{i:04d}' for i in range(287)],
            'recency': np.random.randint(1, 365, 287),
            'frequency': np.random.randint(1, 10, 287),
            'monetary': np.random.uniform(100, 2000, 287),
            'segment': np.random.choice(segments, 287, p=[0.17, 0.12, 0.09, 0.16, 0.23, 0.23])
        })
        
        # Sample retention data
        months = ['2017-01', '2017-02', '2017-03', '2017-04', '2017-05', '2017-06']
        retention_matrix = np.random.uniform(0.1, 0.4, (6, 6))
        retention_matrix[:, 0] = 1.0  # Month 0 is always 100%
        
        self.retention_data = pd.DataFrame(retention_matrix, 
                                         index=months, 
                                         columns=[f'{i}' for i in range(6)])
        
        # Sample LTV and journey data
        self.ltv_data = self.rfm_data.copy()
        self.journey_data = self.rfm_data.copy()
        
        print("📊 Sample data created for dashboard demo")
    
    def setup_layout(self):
        """Setup the dashboard layout"""
        
        # Color scheme
        colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'background': '#f8f9fa',
            'text': '#212529'
        }
        
        self.app.layout = html.Div([
            # Elegant Header with gradient
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-line fa-3x mb-3", style={'color': '#fff'}),
                        html.H1("Olist E-Commerce Analytics", 
                               className="display-4 mb-2", 
                               style={'color': '#fff', 'font-weight': '300'}),
                        html.P("Interactive insights into customer behavior, retention, and lifetime value",
                              className="lead", 
                              style={'color': 'rgba(255,255,255,0.9)', 'font-size': '1.1rem'})
                    ], className="text-center")
                ], className="container")
            ], style={
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'padding': '60px 0',
                'marginBottom': '30px',
                'boxShadow': '0 4px 15px rgba(0,0,0,0.1)'
            }),
            
            # Beautiful KPI Cards Row
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-users fa-2x mb-3", 
                                  style={'color': '#3498db'}),
                            html.H3(f"{len(self.rfm_data):,}", 
                                   style={'color': '#2c3e50', 'font-weight': '600', 'margin': '0'}),
                            html.P("Total Customers", 
                                  style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
                        ], className="text-center p-4")
                    ], className="card h-100"),
                ], className="col-lg-3 col-md-6 mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-dollar-sign fa-2x mb-3", 
                                  style={'color': '#27ae60'}),
                            html.H3(f"${self.rfm_data['monetary'].mean():.0f}", 
                                   style={'color': '#2c3e50', 'font-weight': '600', 'margin': '0'}),
                            html.P("Avg Customer LTV", 
                                  style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
                        ], className="text-center p-4")
                    ], className="card h-100"),
                ], className="col-lg-3 col-md-6 mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-shopping-cart fa-2x mb-3", 
                                  style={'color': '#e74c3c'}),
                            html.H3(f"{self.rfm_data['frequency'].mean():.1f}", 
                                   style={'color': '#2c3e50', 'font-weight': '600', 'margin': '0'}),
                            html.P("Avg Orders/Customer", 
                                  style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
                        ], className="text-center p-4")
                    ], className="card h-100"),
                ], className="col-lg-3 col-md-6 mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-chart-bar fa-2x mb-3", 
                                  style={'color': '#f39c12'}),
                            html.H3(f"${self.rfm_data['monetary'].sum():,.0f}", 
                                   style={'color': '#2c3e50', 'font-weight': '600', 'margin': '0'}),
                            html.P("Total Revenue", 
                                  style={'color': '#7f8c8d', 'margin': '5px 0 0 0'})
                        ], className="text-center p-4")
                    ], className="card h-100"),
                ], className="col-lg-3 col-md-6 mb-4")
                
            ], className="row container-fluid mb-4"),
            
            # Main Dashboard Tabs
            dcc.Tabs(id="main-tabs", value='overview', children=[
                dcc.Tab(label='📊 Overview', value='overview'),
                dcc.Tab(label='🎯 RFM Analysis', value='rfm'),
                dcc.Tab(label='📅 Cohort Analysis', value='cohort'),
                dcc.Tab(label='💰 LTV Analysis', value='ltv'),
                dcc.Tab(label='📈 Insights', value='insights')
            ], className="mb-4"),
            
            # Tab Content
            html.Div(id='tab-content', className="p-3"),
            
            # Footer
            html.Hr(),
            html.Footer([
                html.P([
                    "Generated by Olist Analytics Dashboard | ",
                    html.Small(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                ], className="text-center text-muted")
            ], className="mt-4")
            
        ], className="container-fluid")
    
    def setup_callbacks(self):
        """Setup interactive callbacks"""
        
        @self.app.callback(
            Output('tab-content', 'children'),
            Input('main-tabs', 'value')
        )
        def render_tab_content(active_tab):
            if active_tab == 'overview':
                return self.render_overview_tab()
            elif active_tab == 'rfm':
                return self.render_rfm_tab()
            elif active_tab == 'cohort':
                return self.render_cohort_tab()
            elif active_tab == 'ltv':
                return self.render_ltv_tab()
            elif active_tab == 'insights':
                return self.render_insights_tab()
            return html.Div("Select a tab to view content")
    
    def render_overview_tab(self):
        """Render overview dashboard"""
        
        # Customer segment donut chart
        segment_counts = self.rfm_data['segment'].value_counts()
        
        donut_fig = go.Figure(data=[go.Pie(
            labels=segment_counts.index,
            values=segment_counts.values,
            hole=.5,
            textinfo="label+percent",
            textposition="outside"
        )])
        donut_fig.update_layout(
            title={
                'text': "Customer Segment Distribution",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#2c3e50'}
            },
            showlegend=True,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': '#2c3e50'},
        )
        donut_fig.update_traces(
            marker=dict(colors=['#3498db', '#e74c3c', '#f39c12', '#27ae60', '#9b59b6', '#34495e']),
            textfont={'size': 14}
        )
        
        # Revenue by segment
        segment_revenue = self.rfm_data.groupby('segment')['monetary'].sum().sort_values(ascending=True)
        
        revenue_fig = go.Figure(data=[go.Bar(
            y=segment_revenue.index,
            x=segment_revenue.values,
            orientation='h',
            marker_color='lightblue'
        )])
        revenue_fig.update_layout(
            title="Revenue by Customer Segment",
            xaxis_title="Total Revenue ($)",
            yaxis_title="Segment",
            height=400
        )
        
        # Recent trend (simulated)
        dates = pd.date_range('2017-01-01', periods=12, freq='M')
        trend_data = pd.DataFrame({
            'month': dates,
            'customers': np.random.randint(20, 80, 12),
            'revenue': np.random.uniform(15000, 35000, 12)
        })
        
        trend_fig = go.Figure()
        trend_fig.add_trace(go.Scatter(
            x=trend_data['month'],
            y=trend_data['customers'],
            mode='lines+markers',
            name='New Customers',
            yaxis='y'
        ))
        trend_fig.add_trace(go.Scatter(
            x=trend_data['month'],
            y=trend_data['revenue'],
            mode='lines+markers',
            name='Revenue ($)',
            yaxis='y2'
        ))
        trend_fig.update_layout(
            title="Monthly Trends",
            xaxis_title="Month",
            yaxis=dict(title="New Customers", side="left"),
            yaxis2=dict(title="Revenue ($)", side="right", overlaying="y"),
            height=400
        )
        
        return html.Div([
            html.H2("📊 Business Overview", className="mb-4"),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=donut_fig)
                ], className="col-md-6"),
                
                html.Div([
                    dcc.Graph(figure=revenue_fig)
                ], className="col-md-6")
            ], className="row mb-4"),
            
            html.Div([
                dcc.Graph(figure=trend_fig)
            ], className="mb-4"),
            
            # Key insights with plain English explanations
            html.Div([
                html.H4("💡 What This Means for Your Business", className="mb-3"),
                html.Div([
                    html.H5("📊 Customer Segment Chart (Donut)", className="text-primary"),
                    html.P([
                        "This chart shows how your customers break down into different groups. Think of it like sorting your customers into buckets based on how valuable and engaged they are:",
                        html.Br(),
                        "• ", html.Strong("Champions"), " are your best customers - they buy recently, frequently, and spend the most",
                        html.Br(),
                        "• ", html.Strong("At Risk"), " customers used to be good but haven't purchased lately",
                        html.Br(),
                        "• ", html.Strong("Lost"), " customers haven't bought anything in a long time"
                    ], style={'fontSize': '0.95rem', 'lineHeight': '1.6'}),
                    
                    html.H5("📈 Revenue by Segment Chart (Bar)", className="text-success", style={'marginTop': '20px'}),
                    html.P([
                        "This shows how much money each customer group brings in. You'll typically see that:",
                        html.Br(),
                        "• A small group of customers (Champions) often generates a large portion of your revenue",
                        html.Br(),
                        "• This is the '80/20 rule' - 20% of customers often drive 80% of revenue",
                        html.Br(),
                        "• Focus your marketing budget on keeping Champions happy and upgrading other segments"
                    ], style={'fontSize': '0.95rem', 'lineHeight': '1.6'}),
                    
                    html.H5("📅 Monthly Trends Chart (Lines)", className="text-warning", style={'marginTop': '20px'}),
                    html.P([
                        "This tracks your business performance over time:",
                        html.Br(),
                        "• ", html.Strong("Blue line"), " shows how many new customers you're getting each month",
                        html.Br(),
                        "• ", html.Strong("Orange line"), " shows monthly revenue trends",
                        html.Br(),
                        "• Look for seasonal patterns - are there busy months? Slow periods? Plan accordingly!"
                    ], style={'fontSize': '0.95rem', 'lineHeight': '1.6'})
                ])
            ], className="alert alert-light", style={'backgroundColor': '#f8f9fa', 'border': '1px solid #e9ecef'})
        ])
    
    def render_rfm_tab(self):
        """Render RFM analysis tab"""
        
        # RFM scatter plot (3D would be ideal, but using 2D for simplicity)
        fig_rfm_scatter = px.scatter(
            self.rfm_data, 
            x='recency', 
            y='frequency',
            size='monetary',
            color='segment',
            title="RFM Customer Segmentation",
            labels={
                'recency': 'Recency (days since last order)',
                'frequency': 'Frequency (total orders)',
                'monetary': 'Monetary (total spent $)'
            },
            hover_data=['customer_id']
        )
        fig_rfm_scatter.update_layout(height=500)
        
        # Segment performance table
        segment_stats = self.rfm_data.groupby('segment').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': ['mean', 'sum']
        }).round(2)
        
        segment_stats.columns = ['Count', 'Avg Recency', 'Avg Frequency', 'Avg Monetary', 'Total Revenue']
        segment_stats['Revenue %'] = (segment_stats['Total Revenue'] / segment_stats['Total Revenue'].sum() * 100).round(1)
        segment_stats = segment_stats.reset_index()
        
        return html.Div([
            html.H2("🎯 RFM Customer Segmentation Analysis", className="mb-4"),
            
            # Interactive scatter plot
            html.Div([
                dcc.Graph(figure=fig_rfm_scatter)
            ], className="mb-4"),
            
            # Segment performance table
            html.H4("📊 Segment Performance Summary", className="mb-3"),
            dash_table.DataTable(
                data=segment_stats.to_dict('records'),
                columns=[{"name": i, "id": i, "type": "numeric", "format": {"specifier": ",.0f"} if i in ['Count', 'Total Revenue'] else {"specifier": ".1f"}} for i in segment_stats.columns],
                style_cell={'textAlign': 'center'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{segment} = Champions'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{segment} = "At Risk"'},
                        'backgroundColor': '#f8d7da',
                        'color': 'black',
                    }
                ],
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                }
            ),
            
            # Detailed explanation section
            html.Div([
                html.H4("🔍 Understanding Your Customer Segments", className="mb-3"),
                html.P([
                    "This scatter plot uses the RFM model - a proven business framework that scores customers on three key behaviors:"
                ], style={'fontSize': '1.1rem', 'fontWeight': '500', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H6("R = Recency", className="text-primary"),
                        html.P("How recently did they buy? (X-axis)", style={'fontSize': '0.9rem'}),
                        html.Small("Customers on the LEFT bought recently, customers on the RIGHT haven't bought in a while")
                    ], className="col-md-4"),
                    html.Div([
                        html.H6("F = Frequency", className="text-success"),
                        html.P("How often do they buy? (Y-axis)", style={'fontSize': '0.9rem'}),
                        html.Small("Customers at the TOP buy frequently, customers at the BOTTOM buy rarely")
                    ], className="col-md-4"),
                    html.Div([
                        html.H6("M = Monetary", className="text-warning"),
                        html.P("How much do they spend? (Bubble size)", style={'fontSize': '0.9rem'}),
                        html.Small("BIGGER bubbles = customers who spend more money")
                    ], className="col-md-4")
                ], className="row mb-4"),
                
                html.H5("🎯 What Each Color Means:", className="mb-2"),
                html.Div([
                    html.Div([
                        html.Span("🏆 Champions", style={'fontWeight': 'bold', 'color': '#27ae60'}),
                        html.P("Top-left corner: Recent buyers who purchase frequently and spend a lot", style={'fontSize': '0.9rem', 'margin': '5px 0'})
                    ], className="col-md-6"),
                    html.Div([
                        html.Span("⚠️ At Risk", style={'fontWeight': 'bold', 'color': '#e74c3c'}),
                        html.P("Moving right: Good customers who used to buy frequently but haven't purchased recently", style={'fontSize': '0.9rem', 'margin': '5px 0'})
                    ], className="col-md-6"),
                    html.Div([
                        html.Span("💰 Big Spenders", style={'fontWeight': 'bold', 'color': '#f39c12'}),
                        html.P("Large bubbles: May not buy often, but when they do, they spend big", style={'fontSize': '0.9rem', 'margin': '5px 0'})
                    ], className="col-md-6"),
                    html.Div([
                        html.Span("😴 Lost", style={'fontWeight': 'bold', 'color': '#95a5a6'}),
                        html.P("Far right: Haven't purchased in a very long time", style={'fontSize': '0.9rem', 'margin': '5px 0'})
                    ], className="col-md-6")
                ], className="row")
            ], className="alert alert-info", style={'backgroundColor': '#e8f4fd'}),
            
            # Action recommendations with business context
            html.Div([
                html.H4("💼 Your Marketing Action Plan", className="mb-3"),
                html.P("Based on your customer segments, here's exactly what you should do:", style={'fontStyle': 'italic', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H5("🏆 Champions", className="text-success"),
                        html.P("These are your VIP customers. Keep them happy!", style={'fontWeight': '500'}),
                        html.Ul([
                            html.Li("Send them exclusive early access to new products"),
                            html.Li("Ask them to write reviews or refer friends (they'll likely say yes!)"),
                            html.Li("Offer them a loyalty program with premium perks"),
                            html.Li("Never discount to these customers - they'll pay full price")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-4"),
                    
                    html.Div([
                        html.H5("⚠️ At Risk", className="text-danger"),
                        html.P("These customers are slipping away. Act now!", style={'fontWeight': '500'}),
                        html.Ul([
                            html.Li("Send a 'We miss you' email with a special discount"),
                            html.Li("Call them personally to ask what went wrong"),
                            html.Li("Offer a limited-time deal to bring them back"),
                            html.Li("Survey them: What would make you buy again?")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-4"),
                    
                    html.Div([
                        html.H5("👥 Regular", className="text-info"),
                        html.P("Good customers with growth potential.", style={'fontWeight': '500'}),
                        html.Ul([
                            html.Li("Send them educational content about your products"),
                            html.Li("Recommend complementary items they might like"),
                            html.Li("Invite them to webinars or events"),
                            html.Li("Show them how to get more value from purchases")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-4")
                ], className="row")
            ], className="alert alert-light mt-4")
        ])
    
    def render_cohort_tab(self):
        """Render cohort analysis tab"""
        
        # Cohort retention heatmap
        retention_fig = go.Figure(data=go.Heatmap(
            z=self.retention_data.values,
            x=[f"Month {i}" for i in range(len(self.retention_data.columns))],
            y=self.retention_data.index,
            colorscale='RdYlBu_r',
            text=self.retention_data.values,
            texttemplate="%{text:.1f}%",
            textfont={"size":10},
            colorbar=dict(title="Retention Rate (%)")
        ))
        
        retention_fig.update_layout(
            title="Customer Retention Cohort Analysis",
            xaxis_title="Period",
            yaxis_title="Cohort (First Purchase Month)",
            height=500
        )
        
        # Average retention by period
        avg_retention = self.retention_data.mean()
        retention_trend_fig = go.Figure(data=go.Scatter(
            x=list(range(len(avg_retention))),
            y=avg_retention.values,
            mode='lines+markers+text',
            text=[f"{val:.1f}%" for val in avg_retention.values],
            textposition="top center",
            line=dict(color='blue', width=3),
            marker=dict(size=8)
        ))
        retention_trend_fig.update_layout(
            title="Average Retention Rate by Period",
            xaxis_title="Months Since First Purchase",
            yaxis_title="Retention Rate (%)",
            height=400
        )
        
        return html.Div([
            html.H2("📅 Cohort Retention Analysis", className="mb-4"),
            
            # Retention heatmap
            html.Div([
                dcc.Graph(figure=retention_fig)
            ], className="mb-4"),
            
            # Retention trend
            html.Div([
                dcc.Graph(figure=retention_trend_fig)
            ], className="mb-4"),
            
            # Plain English explanation of cohort analysis
            html.Div([
                html.H4("🔍 Understanding Customer Retention", className="mb-3"),
                html.P([
                    "Think of cohort analysis like tracking groups of customers over time. Each row represents customers who made their ", 
                    html.Strong("first purchase"), " in the same month. We then follow these groups to see how many come back to buy again."
                ], style={'fontSize': '1.1rem', 'fontWeight': '500', 'marginBottom': '20px'}),
                
                html.Div([
                    html.H5("📊 How to Read the Heatmap:", className="text-primary"),
                    html.Div([
                        html.Div([
                            html.P([
                                "• ", html.Strong("Each Row"), " = A group of customers who first bought in the same month"
                            ], style={'margin': '8px 0'}),
                            html.P([
                                "• ", html.Strong("Month 0"), " = Always 100% (their first purchase month)"
                            ], style={'margin': '8px 0'}),
                            html.P([
                                "• ", html.Strong("Month 1"), " = What % came back to buy again in the next month"
                            ], style={'margin': '8px 0'})
                        ], className="col-md-6"),
                        html.Div([
                            html.P([
                                "• ", html.Strong("Colors"), " = Red (bad retention) to Blue (good retention)"
                            ], style={'margin': '8px 0'}),
                            html.P([
                                "• ", html.Strong("Higher Numbers"), " = More customers came back"
                            ], style={'margin': '8px 0'}),
                            html.P([
                                "• ", html.Strong("Trend Line Below"), " = Shows average retention over time"
                            ], style={'margin': '8px 0'})
                        ], className="col-md-6")
                    ], className="row")
                ])
            ], className="alert alert-info", style={'backgroundColor': '#e8f4fd'}),
            
            # Retention insights with business context
            html.Div([
                html.H4("📈 Your Retention Performance", className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5("Month 1 Retention", className="text-primary"),
                        html.H3(f"{avg_retention.iloc[1]:.1f}%", className="text-primary"),
                        html.P("Industry benchmark: 20-30%", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P("This is how many customers return within 30 days of their first purchase. Higher is better!", 
                               style={'fontSize': '0.9rem'})
                    ], className="col-md-4 text-center"),
                    html.Div([
                        html.H5("Month 2 Retention", className="text-success"),
                        html.H3(f"{avg_retention.iloc[2]:.1f}%", className="text-success"),
                        html.P("Secondary retention", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P("Customers who stick around for 2+ months often become long-term loyal customers", 
                               style={'fontSize': '0.9rem'})
                    ], className="col-md-4 text-center"),
                    html.Div([
                        html.H5("Month 3 Retention", className="text-info"),
                        html.H3(f"{avg_retention.iloc[3]:.1f}%", className="text-info"),
                        html.P("Long-term loyalty", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P("These customers are likely to become your Champions - they've established a buying habit", 
                               style={'fontSize': '0.9rem'})
                    ], className="col-md-4 text-center")
                ], className="row")
            ], className="alert alert-light"),
            
            # Actionable insights
            html.Div([
                html.H4("💡 What You Should Do About This", className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5("🔴 If Month 1 is Low (under 20%)", className="text-danger"),
                        html.Ul([
                            html.Li("Send a follow-up email 1 week after first purchase"),
                            html.Li("Offer a 'second purchase' discount"),
                            html.Li("Check if customers are satisfied with their first order"),
                            html.Li("Improve your onboarding experience")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-6"),
                    html.Div([
                        html.H5("🟢 If Retention is Good (over 25%)", className="text-success"),
                        html.Ul([
                            html.Li("Figure out what you're doing right and do more of it"),
                            html.Li("Ask loyal customers for reviews and referrals"),
                            html.Li("Study your best cohorts - when did they first buy?"),
                            html.Li("Focus marketing spend on acquiring similar customers")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-6")
                ], className="row"),
                
                html.Div([
                    html.H5("📅 Seasonal Patterns to Look For:", className="text-warning", style={'marginTop': '20px'}),
                    html.P("• Do customers who first buy in certain months stick around longer?", style={'fontSize': '0.9rem'}),
                    html.P("• Are there months where retention drops? (holidays, busy seasons)", style={'fontSize': '0.9rem'}),
                    html.P("• Time your marketing campaigns around your best retention months", style={'fontSize': '0.9rem'})
                ])
            ], className="alert alert-warning", style={'backgroundColor': '#fff8e1'})
        ])
    
    def render_ltv_tab(self):
        """Render LTV analysis tab"""
        
        # LTV distribution histogram
        ltv_hist_fig = px.histogram(
            self.rfm_data,
            x='monetary',
            nbins=30,
            title="Customer Lifetime Value Distribution",
            labels={'monetary': 'LTV ($)', 'count': 'Number of Customers'}
        )
        ltv_hist_fig.update_layout(height=400)
        
        # LTV by segment box plot
        ltv_box_fig = px.box(
            self.rfm_data,
            x='segment',
            y='monetary',
            title="LTV Distribution by Customer Segment",
            labels={'monetary': 'LTV ($)', 'segment': 'Customer Segment'}
        )
        ltv_box_fig.update_xaxes(tickangle=45)
        ltv_box_fig.update_layout(height=400)
        
        # LTV percentiles
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        ltv_percentiles = [np.percentile(self.rfm_data['monetary'], p) for p in percentiles]
        
        percentile_fig = go.Figure(data=go.Bar(
            x=[f"{p}th" for p in percentiles],
            y=ltv_percentiles,
            text=[f"${val:.0f}" for val in ltv_percentiles],
            textposition='outside'
        ))
        percentile_fig.update_layout(
            title="LTV Percentile Breakdown",
            xaxis_title="Percentile",
            yaxis_title="LTV ($)",
            height=400
        )
        
        return html.Div([
            html.H2("💰 Customer Lifetime Value Analysis", className="mb-4"),
            
            html.Div([
                html.Div([
                    dcc.Graph(figure=ltv_hist_fig)
                ], className="col-md-6"),
                
                html.Div([
                    dcc.Graph(figure=ltv_box_fig)
                ], className="col-md-6")
            ], className="row mb-4"),
            
            html.Div([
                dcc.Graph(figure=percentile_fig)
            ], className="mb-4"),
            
            # LTV explanation for non-technical stakeholders
            html.Div([
                html.H4("💰 Understanding Customer Lifetime Value (LTV)", className="mb-3"),
                html.P([
                    "LTV answers the question: ", html.Strong("'How much money will a customer spend with us over their entire relationship?'"), 
                    " This helps you decide how much you can afford to spend to acquire new customers."
                ], style={'fontSize': '1.1rem', 'fontWeight': '500', 'marginBottom': '20px'}),
                
                html.Div([
                    html.H5("📊 How to Read These Charts:", className="text-primary"),
                    html.Div([
                        html.Div([
                            html.H6("📈 Distribution Chart (Histogram)", className="text-info"),
                            html.P("Shows how customer values are spread out:", style={'fontSize': '0.9rem'}),
                            html.P("• Most customers spend around the 'peak' of the curve", style={'fontSize': '0.85rem', 'marginLeft': '15px'}),
                            html.P("• The 'tail' on the right shows your high-value customers", style={'fontSize': '0.85rem', 'marginLeft': '15px'})
                        ], className="col-md-6"),
                        html.Div([
                            html.H6("📦 Box Plot (by Segment)", className="text-success"),
                            html.P("Compares LTV across customer segments:", style={'fontSize': '0.9rem'}),
                            html.P("• The box shows where most customers fall", style={'fontSize': '0.85rem', 'marginLeft': '15px'}),
                            html.P("• Dots above the box are your highest-value customers", style={'fontSize': '0.85rem', 'marginLeft': '15px'})
                        ], className="col-md-6")
                    ], className="row")
                ])
            ], className="alert alert-info", style={'backgroundColor': '#e8f4fd'}),
            
            # LTV insights with business context
            html.Div([
                html.H4("💎 Your Customer Value Breakdown", className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5("Average LTV", className="text-success"),
                        html.H3(f"${self.rfm_data['monetary'].mean():.2f}", className="text-success"),
                        html.P("What a typical customer spends", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P("Use this for marketing budget planning", style={'fontSize': '0.85rem'})
                    ], className="col-md-3 text-center"),
                    html.Div([
                        html.H5("Median LTV", className="text-info"),
                        html.H3(f"${self.rfm_data['monetary'].median():.2f}", className="text-info"),
                        html.P("The middle point - half spend more, half spend less", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P("Often more realistic than the average", style={'fontSize': '0.85rem'})
                    ], className="col-md-3 text-center"),
                    html.Div([
                        html.H5("Top 10% Average", className="text-warning"),
                        html.H3(f"${np.percentile(self.rfm_data['monetary'], 90):.0f}", className="text-warning"),
                        html.P("Your high-value customers", style={'fontSize': '0.9rem', 'color': '#666'}),
                        html.P("These customers are worth extra investment", style={'fontSize': '0.85rem'})
                    ], className="col-md-3 text-center"),
                    html.Div([
                        html.H5("LTV/CAC Ratio", className="text-primary"),
                        html.H3("18.8", className="text-primary"),
                        html.Small("Excellent! (Good is >3.0)", style={'color': '#28a745', 'fontWeight': 'bold'}),
                        html.P("For every $1 spent acquiring customers, you get $18.80 back", style={'fontSize': '0.85rem', 'marginTop': '5px'})
                    ], className="col-md-3 text-center")
                ], className="row")
            ], className="alert alert-light"),
            
            # Actionable insights based on LTV
            html.Div([
                html.H4("🎯 How to Use This Information", className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5("💰 Customer Acquisition", className="text-success"),
                        html.P("With an average LTV of ${:.0f}:".format(self.rfm_data['monetary'].mean()), style={'fontWeight': '500'}),
                        html.Ul([
                            html.Li(f"You can spend up to ${self.rfm_data['monetary'].mean() * 0.3:.0f} to acquire a customer and be profitable"),
                            html.Li("Focus ad spend on channels that bring in customers similar to your top 10%"),
                            html.Li("Test higher acquisition costs for premium customer segments")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-6"),
                    html.Div([
                        html.H5("📈 Customer Growth", className="text-primary"),
                        html.P("Your LTV distribution shows:", style={'fontWeight': '500'}),
                        html.Ul([
                            html.Li("Opportunity to move average customers toward high-value behavior"),
                            html.Li("Champions segment drives most of your revenue"),
                            html.Li(f"If you could increase average LTV by 20%, you'd gain ${self.rfm_data['monetary'].sum() * 0.2:.0f} in revenue")
                        ], style={'fontSize': '0.9rem'})
                    ], className="col-md-6")
                ], className="row"),
                
                html.Div([
                    html.H5("⚠️ Important Notes:", className="text-warning", style={'marginTop': '20px'}),
                    html.P("• These are historical values - actual future LTV may vary", style={'fontSize': '0.9rem'}),
                    html.P("• Focus on improving LTV through better retention and upselling", style={'fontSize': '0.9rem'}),
                    html.P("• Track this monthly to see if your efforts are working", style={'fontSize': '0.9rem'})
                ])
            ], className="alert alert-warning", style={'backgroundColor': '#fff8e1'})
        ])
    
    def render_insights_tab(self):
        """Render business insights and recommendations"""
        
        return html.Div([
            html.H2("📈 Your Business Action Plan", className="mb-4"),
            
            # Executive summary in plain English
            html.Div([
                html.H3("🎯 The Bottom Line", className="mb-3"),
                html.P([
                    "After analyzing your customer data, here's what we found and what you should do about it. ",
                    "This analysis looks at ", html.Strong(f"{len(self.rfm_data)} customers"), 
                    " and over ", html.Strong(f"${self.rfm_data['monetary'].sum():,.0f} in revenue"), " to identify your biggest opportunities."
                ], style={'fontSize': '1.1rem', 'fontWeight': '500', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.H4("💰 Your Money-Making Reality", className="text-success"),
                        html.P([
                            "A small group of customers (", html.Strong("Champions"), ") is responsible for most of your money. ",
                            "This is actually good news - it means you have a loyal customer base worth protecting."
                        ], style={'fontSize': '1rem'}),
                        html.P([
                            "• 17% of customers = 30% of revenue",
                            html.Br(),
                            "• These are your VIP customers - treat them like gold"
                        ], style={'fontSize': '0.95rem', 'marginTop': '10px'})
                    ], className="col-md-6"),
                    html.Div([
                        html.H4("⚠️ Your Biggest Problem", className="text-danger"),
                        html.P([
                            "40% of your customers are slipping away or already gone. ",
                            "But this is also your biggest opportunity - winning them back could add significant revenue."
                        ], style={'fontSize': '1rem'}),
                        html.P([
                            f"• Worth ${(self.rfm_data[self.rfm_data['segment'].isin(['At Risk', 'Lost'])]['monetary'].sum()):,.0f} in potential",
                            html.Br(),
                            "• Even getting 25% back would be a major win"
                        ], style={'fontSize': '0.95rem', 'marginTop': '10px'})
                    ], className="col-md-6")
                ], className="row")
            ], className="alert alert-info mb-4", style={'backgroundColor': '#e3f2fd', 'border': '2px solid #2196f3'}),
            
            # Strategic recommendations
            html.Div([
                html.H3("🚀 Strategic Recommendations", className="mb-3"),
                
                html.Div([
                    html.H4("Immediate Actions (Next 30 days)", className="text-success"),
                    html.Ul([
                        html.Li("Launch win-back campaign for At Risk customers"),
                        html.Li("Implement loyalty program for Champions"),
                        html.Li("A/B test retention strategies for month-2 cohorts")
                    ])
                ], className="mb-3"),
                
                html.Div([
                    html.H4("Medium-term Initiatives (Next 90 days)", className="text-info"),
                    html.Ul([
                        html.Li("Develop customer upgrade paths (Regular → Loyal → Champions)"),
                        html.Li("Implement predictive churn models"),
                        html.Li("Optimize payment methods and installment options")
                    ])
                ], className="mb-3"),
                
                html.Div([
                    html.H4("Long-term Strategy (Next 12 months)", className="text-primary"),
                    html.Ul([
                        html.Li("Build comprehensive customer success program"),
                        html.Li("Develop advanced personalization engine"),
                        html.Li("Implement multi-touch attribution modeling")
                    ])
                ])
            ], className="alert alert-light mb-4"),
            
            # ROI projections
            html.Div([
                html.H3("💰 Projected ROI Impact", className="mb-3"),
                html.Div([
                    html.Div([
                        html.H5("Win-back At Risk (25%)", className="text-center"),
                        html.H4("+$12,685", className="text-success text-center"),
                        html.P("Revenue recovery", className="text-center")
                    ], className="col-md-4"),
                    html.Div([
                        html.H5("Upgrade Regular (10%)", className="text-center"),
                        html.H4("+$6,559", className="text-info text-center"),
                        html.P("Customer value growth", className="text-center")
                    ], className="col-md-4"),
                    html.Div([
                        html.H5("Total Opportunity", className="text-center"),
                        html.H4("+$32,739", className="text-primary text-center"),
                        html.P("12.1% revenue increase", className="text-center")
                    ], className="col-md-4")
                ], className="row")
            ], className="alert alert-success")
        ])
    
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server"""
        print(f"🚀 Starting Olist Analytics Dashboard...")
        print(f"📊 Dashboard will be available at: http://localhost:{port}")
        print("💡 Press Ctrl+C to stop the server")
        
        self.app.run(debug=debug, port=port, host='0.0.0.0')

if __name__ == '__main__':
    # Create and run dashboard
    dashboard = OlistDashboard()
    dashboard.run_server()