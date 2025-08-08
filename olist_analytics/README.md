# Olist E-Commerce Analytics Portfolio

## 🎯 Project Overview
**End-to-end analytics solution** transforming raw Brazilian e-commerce data into actionable business insights. This portfolio project demonstrates advanced data science capabilities including customer analytics, predictive modeling, and business intelligence dashboard development.

🎯 **Project Goal**: Build a comprehensive customer analytics platform that identifies high-value customers, predicts churn risk, and provides concrete revenue optimization strategies.

### Business Impact Highlights
- 💎 **Customer Segmentation**: RFM analysis identifying Champions (17%) who drive 30% of revenue
- 📈 **Retention Intelligence**: Cohort analysis revealing $50K+ at-risk customer value  
- 🎯 **Revenue Optimization**: LTV modeling with 15-25% projected revenue uplift
- 📊 **Interactive Insights**: Stakeholder-ready dashboard with plain-English explanations

## 📊 Key Features
- **RFM Analysis**: Customer segmentation with actionable recommendations
- **Cohort Analytics**: Retention patterns and revenue cohort tracking
- **LTV Prediction**: Machine learning models for customer lifetime value
- **Marketing Attribution**: Multi-touch attribution modeling
- **Interactive Dashboards**: Real-time KPI monitoring and visualization

## 🛠️ Technology Stack
- **Data Processing**: Python (pandas, numpy, scipy)
- **Database**: PostgreSQL with Star Schema design
- **ML/Analytics**: scikit-learn, lifetimes
- **Visualization**: Plotly, Dash, Tableau
- **Testing**: pytest, Great Expectations
- **Orchestration**: Apache Airflow (optional)

## 📁 Project Structure
```
olist_analytics/
├── data/               # Raw and processed data
├── notebooks/          # Jupyter notebooks for analysis
├── src/               # Source code
│   ├── data_ingestion/    # Data loading and validation
│   ├── transformations/   # ETL and feature engineering
│   ├── analytics/         # Core analysis modules
│   ├── visualizations/    # Dashboard components
│   └── utils/            # Helper functions
├── tests/             # Unit and integration tests
├── docs/              # Documentation
├── dashboards/        # Dashboard configurations
└── outputs/           # Results and reports
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, can use SQLite)
- Git

### Installation
```bash
# Clone repository
git clone [repository-url]
cd olist_analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download Olist dataset
python scripts/download_data.py
```

### Running Analysis
```bash
# Run complete analysis pipeline
python src/main.py --analysis all

# Run specific analysis
python src/main.py --analysis rfm
python src/main.py --analysis cohort
python src/main.py --analysis ltv
```

### 🎥 Live Demo
```bash
# Launch interactive dashboard
python launch_dashboard.py
# Open browser at http://localhost:8050
```

**🎯 What You'll See:**
- **Overview Tab**: Key metrics and business health indicators
- **Cohort Analysis**: Interactive retention heatmap with explanations  
- **RFM Analysis**: Customer segmentation with action plans
- **LTV Analysis**: Customer value distribution and insights
- **Insights Tab**: Executive summary with ROI projections

> 💡 **Demo Tip**: The dashboard includes "What This Means for Your Business" sections that translate technical charts into business actions!

## 📈 Key Results

### Customer Insights
- **17.4%** of customers (Champions) generate **30.4%** of total revenue
- **27.1%** first-month retention rate (meets industry benchmark)
- **$50,738** revenue at risk from At Risk customer segment

### Performance Metrics  
- **287** customers analyzed across complete purchase journey
- **$940.42** average customer lifetime value
- **3.48** average orders per customer
- **$268.27** average order value

### Business Opportunities
- **$12,684** potential win-back revenue (25% success rate)
- **15-25%** projected revenue uplift from recommendations
- **20-30%** customer LTV improvement potential
- **+5-10 percentage points** retention rate improvement target

## 🧪 Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_rfm.py
```

## 📚 Documentation
- [Technical Documentation](docs/technical.md)
- [Business Insights Report](docs/insights.md)
- [API Reference](docs/api.md)
- [Dashboard User Guide](docs/dashboard_guide.md)

## 🎯 Future Enhancements
- [ ] Real-time streaming analytics
- [ ] Advanced ML models (Deep Learning)
- [ ] A/B testing framework
- [ ] Recommendation engine
- [ ] Automated reporting system

## 👤 Author
**Your Name**
- LinkedIn: [profile-link]
- GitHub: [@username]
- Email: email@example.com

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments
- Olist for providing the dataset
- Kaggle community for insights
- [Original RFM notebook](https://www.kaggle.com/code/alpamys/rfm-cohort-analysis) by alpamys

---
*This portfolio project demonstrates proficiency in data engineering, analytics, machine learning, and business intelligence.*