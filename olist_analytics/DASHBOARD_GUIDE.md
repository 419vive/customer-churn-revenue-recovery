# 📊 Olist Analytics Dashboard Guide

## 🚀 Quick Start

### 1. Launch Dashboard
```bash
# From project root directory
python launch_dashboard.py

# Or directly from src folder
cd src && python dashboard/app.py
```

### 2. Access Dashboard
Open your browser and go to: **http://localhost:8050**

## 📱 Dashboard Features

### 🏠 **Overview Tab**
- **KPI Cards**: Total customers, average LTV, orders per customer, total revenue
- **Customer Segment Distribution**: Interactive donut chart
- **Revenue by Segment**: Horizontal bar chart
- **Monthly Trends**: Dual-axis line chart showing customers and revenue

### 🎯 **RFM Analysis Tab**
- **Interactive Scatter Plot**: RFM segmentation with size=monetary, color=segment
- **Segment Performance Table**: Detailed metrics by customer segment
- **Action Recommendations**: Specific strategies for each segment

### 📅 **Cohort Analysis Tab**
- **Retention Heatmap**: Color-coded cohort retention matrix
- **Retention Trend**: Average retention rates by period
- **Key Metrics**: Month 1, 2, and 3 retention benchmarks

### 💰 **LTV Analysis Tab**
- **LTV Distribution**: Histogram showing customer value spread
- **LTV by Segment**: Box plots comparing segments
- **Percentile Breakdown**: LTV at different percentiles
- **Key Metrics**: Average, median, top 10%, LTV/CAC ratio

### 📈 **Insights Tab**
- **Strategic Findings**: Revenue concentration and retention opportunities
- **Action Plan**: Immediate, medium-term, and long-term recommendations
- **ROI Projections**: Quantified impact of proposed initiatives

## 🎨 Dashboard Features

### **Interactive Elements**
- ✅ Responsive design for all screen sizes
- ✅ Interactive charts with hover details
- ✅ Color-coded segments and performance indicators
- ✅ Sortable and filterable data tables

### **Visual Design**
- ✅ Professional color scheme
- ✅ Bootstrap-styled components
- ✅ Clear typography and spacing
- ✅ Consistent branding throughout

## 🛠️ Troubleshooting

### **Dashboard Won't Start**
1. Check if analysis results exist: `ls outputs/`
2. Run analysis first: `python src/main_advanced.py`
3. Install dependencies: `pip install dash plotly pandas`

### **No Data Showing**
1. Verify CSV files in outputs/ folder
2. Check timestamps match in filenames
3. Regenerate data with main_advanced.py

### **Port Already in Use**
```bash
# Use different port
python launch_dashboard.py --port 8051
```

## 📊 Data Requirements

The dashboard expects these files in `outputs/` folder:
- `rfm_segments_detailed_[timestamp].csv`
- `customer_ltv_detailed_[timestamp].csv`
- `retention_matrix_[timestamp].csv`
- `customer_journey_[timestamp].csv`

## 🎯 Demo Features

### **Sample Data Mode**
If analysis results are missing, dashboard automatically creates sample data for demonstration purposes.

### **Performance Optimized**
- Fast loading with cached data
- Responsive charts for smooth interaction
- Minimal memory footprint

## 📱 Mobile Friendly

Dashboard works on:
- ✅ Desktop (1920x1080+)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667+)

## 🎨 Customization

To customize colors, edit `colors` dictionary in `src/dashboard/app.py`:
```python
colors = {
    'primary': '#1f77b4',    # Blue
    'secondary': '#ff7f0e',  # Orange
    'success': '#2ca02c',    # Green
    'danger': '#d62728',     # Red
    'warning': '#ff7f0e',    # Orange
    'background': '#f8f9fa', # Light gray
    'text': '#212529'        # Dark gray
}
```

---

**🎉 Your interactive dashboard is ready to showcase your analytics skills!**

Perfect for:
- 📈 Portfolio presentations
- 🤝 Stakeholder meetings  
- 💼 Job interviews
- 📊 Executive reporting