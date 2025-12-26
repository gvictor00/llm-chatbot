#!/usr/bin/env python3
"""
Entry point for the LLM Chatbot with RAG application.

This script serves as the main entry point to start both the FastAPI backend server
and the React frontend application simultaneously.
"""

import sys
import os
import subprocess
import threading
import time
import signal
from pathlib import Path

# Add the project root to Python path to enable proper imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ApplicationRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True

    def start_backend(self):
        """Start the FastAPI backend server"""
        print("🚀 Starting Python backend server...")
        try:
            # Start uvicorn server
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "src.main:app",  # Changed from backend.main:app
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ], cwd=project_root)
            print("✅ Backend server started on http://localhost:8000")
        except Exception as e:
            print(f"❌ Failed to start backend server: {e}")
            return False
        return True

    def start_frontend(self):
        """Start the React frontend application"""
        frontend_path = project_root / "frontend"

        # Check if frontend directory exists
        if not frontend_path.exists():
            print("⚠️  Frontend directory not found. Creating frontend setup...")
            self.setup_frontend()
            return False

        # Check if node_modules exists
        if not (frontend_path / "node_modules").exists():
            print("📦 Installing frontend dependencies...")
            try:
                subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install frontend dependencies: {e}")
                return False

        print("🌐 Starting React frontend server...")
        try:
            # Start React development server
            self.frontend_process = subprocess.Popen([
                "npm", "start"
            ], cwd=frontend_path)
            print("✅ Frontend server starting on http://localhost:3000")
        except Exception as e:
            print(f"❌ Failed to start frontend server: {e}")
            return False
        return True

    def setup_frontend(self):
        """Setup frontend if it doesn't exist"""
        print("🔧 Setting up frontend application...")
        frontend_path = project_root / "frontend"

        try:
            # Create frontend directory
            frontend_path.mkdir(exist_ok=True)

            # Create React app
            subprocess.run([
                "npx", "create-react-app", ".", "--template", "javascript"
            ], cwd=frontend_path, check=True)

            # Install additional dependencies
            subprocess.run([
                "npm", "install", "axios", "tailwindcss", "postcss", "autoprefixer"
            ], cwd=frontend_path, check=True)

            # Initialize Tailwind CSS
            subprocess.run([
                "npx", "tailwindcss", "init", "-p"
            ], cwd=frontend_path, check=True)

            print("✅ Frontend setup completed!")
            print("📝 Please add the frontend components and restart the application.")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to setup frontend: {e}")
        except Exception as e:
            print(f"❌ Unexpected error during frontend setup: {e}")

    def check_dependencies(self):
        """Check if required dependencies are available"""
        print("🔍 Checking dependencies...")

        # Check Python dependencies
        try:
            import uvicorn
            import fastapi
            print("✅ Python dependencies found")
        except ImportError as e:
            print(f"❌ Missing Python dependencies: {e}")
            print("💡 Run: pip install -r requirements.txt")
            return False

        # Check Node.js
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js found: {result.stdout.strip()}")
            else:
                print("❌ Node.js not found")
                return False
        except FileNotFoundError:
            print("❌ Node.js not found. Please install Node.js from https://nodejs.org/")
            return False

        # Check npm
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm found: {result.stdout.strip()}")
            else:
                print("❌ npm not found")
                return False
        except FileNotFoundError:
            print("❌ npm not found. Please install npm")
            return False

        return True

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down applications...")
        self.running = False
        self.stop_applications()
        sys.exit(0)

    def stop_applications(self):
        """Stop both backend and frontend processes"""
        if self.backend_process:
            print("🔄 Stopping backend server...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()

        if self.frontend_process:
            print("🔄 Stopping frontend server...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()

    def wait_for_backend(self, max_attempts=30):
        """Wait for backend to be ready"""
        import requests

        _timeout_in_sec = 5
        for attempt in range(max_attempts):
            try:
                response = requests.get("http://localhost:8000/health", timeout=_timeout_in_sec)
                print(f"Backend health check response code: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass

            print(f"⏳ Waiting for backend... ({attempt + 1}/{max_attempts})")
            time.sleep(_timeout_in_sec)

        print("❌ Backend failed to start within expected time")
        return False

    def run(self):
        """Main run method"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("🤖 LLM Chatbot with RAG - Starting Application")
        print("=" * 50)

        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed. Please install missing dependencies.")
            return 1

        try:
            # Start backend
            if not self.start_backend():
                return 1

            # Wait for backend to be ready
            if not self.wait_for_backend():
                self.stop_applications()
                return 1

            # Start frontend
            if not self.start_frontend():
                print("⚠️  Frontend failed to start, but backend is running.")
                print("🌐 You can access the API at http://localhost:8000")
                print("📚 API documentation at http://localhost:8000/docs")
            else:
                print("\n🎉 Application started successfully!")
                print("=" * 50)
                print("🌐 Frontend: http://localhost:3000")
                print("🚀 Backend:  http://localhost:8000")
                print("📚 API Docs: http://localhost:8000/docs")
                print("=" * 50)
                print("Press Ctrl+C to stop both servers")

            # Keep the main thread alive
            while self.running:
                time.sleep(1)

                # Check if processes are still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process stopped unexpectedly")
                    break

                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("⚠️  Frontend process stopped")
                    # Frontend stopping is not critical, continue with backend only

        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        finally:
            self.stop_applications()

        return 0

def main():
    """Main entry point"""
    runner = ApplicationRunner()
    return runner.run()
if __name__ == "__main__":
    sys.exit(main())
