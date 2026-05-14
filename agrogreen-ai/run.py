#!/usr/bin/env python3
# run.py — AgroGreen AI Launcher
"""
Start the AgroGreen AI platform.
Run: python run.py
Or:  python run.py --mode backend    (FastAPI only)
     python run.py --mode frontend   (Gradio only)
     python run.py --mode both       (default)
"""

import sys
import os
import argparse
import threading
import subprocess
import time
import socket

def find_available_port(start_port=7860, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                s.close()
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

def start_backend():
    """Start FastAPI backend server."""
    print("\n🚀 Starting AgroGreen AI Backend (FastAPI)...")
    try:
        os.system("uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

def start_frontend():
    """Start Gradio frontend."""
    print("\n🌿 Starting AgroGreen AI Frontend (Gradio)...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and launch the Gradio app
    from frontend.app import app as gradio_app
    from config.settings import GRADIO_PORT
    
    # Find an available port
    try:
        available_port = find_available_port(GRADIO_PORT)
        if available_port != GRADIO_PORT:
            print(f"⚠️  Port {GRADIO_PORT} is in use, using port {available_port} instead")
        
        print(f"📡 Gradio will be accessible at: http://localhost:{available_port}")
        gradio_app.launch(
            server_name="0.0.0.0",
            server_port=available_port,
            share=False,
            show_error=True
        )
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="AgroGreen AI Platform")
    parser.add_argument("--mode", choices=["backend", "frontend", "both"], 
                        default="frontend", help="What to start")
    args = parser.parse_args()
    
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║           🌱 AgroGreen AI Platform v1.0              ║
    ║    AI-Powered Smart Farming & Urban Green Planning   ║
    ╚══════════════════════════════════════════════════════╝
    """)
    
    if args.mode == "backend":
        start_backend()
    elif args.mode == "frontend":
        start_frontend()
    else:
        # Start backend in thread, frontend in main thread
        backend_thread = threading.Thread(target=start_backend, daemon=True)
        backend_thread.start()
        time.sleep(2)
        start_frontend()

if __name__ == "__main__":
    main()
