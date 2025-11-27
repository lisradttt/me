#!/usr/bin/env python3
"""
Quick start script - Run this to start the bot immediately
تشغيل سريع - قم بتشغيل هذا لبدء البوت مباشرة
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("JoyBoy Bot - Quick Start")
    print("=" * 60)
    
    # Step 1: Install requirements
    print("\n[1/3] Installing dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=False
    )
    if result.returncode != 0:
        print("❌ Failed to install dependencies")
        return 1
    print("✅ Dependencies installed")
    
    # Step 2: Verify setup
    print("\n[2/3] Verifying setup...")
    result = subprocess.run(
        [sys.executable, "verify_setup.py"],
        capture_output=False
    )
    if result.returncode != 0:
        print("❌ Setup verification failed")
        return 1
    print("✅ Setup verified")
    
    # Step 3: Run bot
    print("\n[3/3] Starting bot...")
    print("-" * 60)
    result = subprocess.run(
        [sys.executable, "main.py"],
        capture_output=False
    )
    
    return result.returncode

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Bot stopped")
        sys.exit(0)
