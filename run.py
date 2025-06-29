#!/usr/bin/env python3
"""
Startup script for Calendar Booking Agent
"""
import subprocess
import sys
import time
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return None
    
    try:
        # Change to backend directory and start the server
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(3)
        
        if process.poll() is None:  # Process is still running
            print("✅ Backend started successfully on http://localhost:8000")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎨 Starting Streamlit frontend...")
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    try:
        # Start Streamlit
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"],
            cwd=frontend_dir
        )
        
        print("✅ Frontend started successfully")
        print("🌐 Open your browser to: http://localhost:8501")
        return process
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None

def main():
    """Main startup function"""
    print("🤖 Calendar Booking Agent Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the calendar_agent directory")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Cannot start frontend without backend")
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Frontend failed to start")
        if backend_process:
            backend_process.terminate()
        return
    
    print("\n🎉 Calendar Booking Agent is running!")
    print("📅 Backend API: http://localhost:8000")
    print("🎨 Frontend UI: http://localhost:8501")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop both services")
    
    try:
        # Wait for user to stop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Services stopped")

if __name__ == "__main__":
    main()
