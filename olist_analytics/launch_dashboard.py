#!/usr/bin/env python
"""
Simple Dashboard Launcher
Launch the Olist Analytics Dashboard with one command
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.dashboard.app import OlistDashboard
    
    print("🚀 Launching Olist Analytics Dashboard...")
    print("=" * 60)
    
    # Create and run dashboard
    dashboard = OlistDashboard()
    dashboard.run_server(debug=True, port=8050)
    
except ImportError as e:
    print("❌ Missing dependencies. Please install:")
    print("pip install dash plotly pandas numpy")
    print(f"\nError: {e}")
    
except Exception as e:
    print(f"❌ Error launching dashboard: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure all analysis results exist in outputs/ folder")
    print("2. Run 'python src/main_advanced.py' first to generate data")
    print("3. Check that all dependencies are installed")