
#!/usr/bin/env python
"""
Quick Dashboard Test
Test the dashboard in non-blocking mode
"""

import sys
import os
import subprocess
import webbrowser
import time

def test_dashboard():
    """Test dashboard with automatic browser opening"""
    
    print("🚀 Testing Olist Analytics Dashboard...")
    print("=" * 50)
    
    # Check if dashboard files exist
    dashboard_file = "src/dashboard/app.py"
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return False
    
    print("✅ Dashboard files found")
    
    # Try to start dashboard in background
    try:
        print("🔧 Starting dashboard server...")
        
        # Start dashboard process
        process = subprocess.Popen([
            sys.executable, "launch_dashboard.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is running
        if process.poll() is None:
            print("✅ Dashboard server started successfully!")
            print("🌐 Opening browser to http://localhost:8050")
            
            # Open browser
            webbrowser.open("http://localhost:8050")
            
            print("\n📊 Dashboard Features to Test:")
            print("- Overview tab with KPI cards and charts")
            print("- RFM Analysis with interactive scatter plot")
            print("- Cohort Analysis with retention heatmap")
            print("- LTV Analysis with distribution charts")
            print("- Insights tab with strategic recommendations")
            
            print("\n⌨️  Press Ctrl+C to stop the dashboard")
            
            # Wait for user to stop
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping dashboard...")
                process.terminate()
                process.wait()
                print("✅ Dashboard stopped successfully!")
                
            return True
        else:
            print("❌ Dashboard failed to start")
            stdout, stderr = process.communicate()
            print(f"Error: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

if __name__ == "__main__":
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    success = test_dashboard()
    
    if success:
        print("\n🎉 Dashboard test completed successfully!")
        print("💡 Your dashboard is ready for portfolio presentation!")
    else:
        print("\n⚠️  Dashboard test failed. Check the error messages above.")
        print("💡 Try running 'python src/main_advanced.py' first to generate data.")