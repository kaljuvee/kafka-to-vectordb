#!/usr/bin/env python3
"""
Run the Kafka to VectorDB Streamlit Demo Application
"""

import os
import sys
import subprocess

def main():
    """Run the Streamlit application"""
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, 'Home.py')
    
    # Check if the app file exists
    if not os.path.exists(app_path):
        print(f"❌ Streamlit app not found at: {app_path}")
        return 1
    
    print("🚀 Starting Kafka to VectorDB Streamlit Demo...")
    print(f"📁 App location: {app_path}")
    print("🌐 The app will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application")
    print()
    
    try:
        # Run streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd, cwd=script_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error running Streamlit app: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

