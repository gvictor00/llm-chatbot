#!/usr/bin/env python3
"""
Setup script for the LLM Chatbot with RAG application.
This script helps set up both backend and frontend dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, cwd=cwd, check=True, shell=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed: {e}")
        return False

def setup_backend():
    """Setup Python backend dependencies"""
    print("🐍 Setting up Python backend...")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", description="Installing Python dependencies"):
        return False
    
    return True

def setup_frontend():
    """Setup React frontend"""
    print("⚛️  Setting up React frontend...")
    
    project_root = Path(__file__).parent
    frontend_path = project_root / "frontend"
    
    # Create frontend directory if it doesn't exist
    frontend_path.mkdir(exist_ok=True)
    
    # Check if it's already a React app
    if not (frontend_path / "package.json").exists():
        # Create React app
        if not run_command("npx create-react-app . --template javascript", 
                          cwd=frontend_path, 
                          description="Creating React application"):
            return False
    
    # Install additional dependencies
    dependencies = [
        "axios",
        "tailwindcss",
        "postcss", 
        "autoprefixer"
    ]
    
    for dep in dependencies:
        if not run_command(f"npm install {dep}", 
                          cwd=frontend_path, 
                          description=f"Installing {dep}"):
            return False
    
    # Initialize Tailwind CSS
    if not run_command("npx tailwindcss init -p", 
                      cwd=frontend_path, 
                      description="Initializing Tailwind CSS"):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 LLM Chatbot with RAG - Setup")
    print("=" * 40)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        return 1
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return 1
    
    print("\n🎉 Setup completed successfully!")
    print("=" * 40)
    print("📝 Next steps:")
    print("1. Add your frontend components to the 'frontend' directory")
    print("2. Configure your backend settings in backend/config/config.yaml")
    print("3. Run 'python run.py' to start both servers")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
