#!/usr/bin/env python3
"""
Quick Setup & Test Script for IV Tracker
Run this to verify everything is working
"""

import sys
import subprocess
import os


def check_dependencies():
    """Check if required packages are installed"""
    required = ['yfinance', 'pandas', 'openpyxl', 'openai']
    missing = []

    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)

    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False

    return True


def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')

    if api_key:
        print(f"✅ OpenAI API Key found (starts with: {api_key[:7]}...)")
        return True
    else:
        print("⚠️  OpenAI API Key NOT SET")
        print("\nSet it with:")
        print("  Mac/Linux: export OPENAI_API_KEY='sk-...'")
        print("  Windows:   $env:OPENAI_API_KEY='sk-...'")
        print("\n⚡ You can still run without it (GPT analysis will be disabled)")
        return False


def check_watchlist():
    """Check if watchlist file exists"""
    if os.path.exists('watchlist.txt'):
        with open('watchlist.txt', 'r') as f:
            tickers = [line.strip() for line in f if line.strip()]
        print(f"✅ Watchlist found: {len(tickers)} tickers")
        print(f"   Tickers: {', '.join(tickers[:5])}{'...' if len(tickers) > 5 else ''}")
        return True
    else:
        print("❌ watchlist.txt NOT FOUND")
        print("\nCreate watchlist.txt with your tickers (one per line)")
        return False


def main():
    print("=" * 60)
    print("IV TRACKER - SETUP & VERIFICATION")
    print("=" * 60 + "\n")

    print("1. Checking Python Dependencies...")
    print("-" * 40)
    deps_ok = check_dependencies()

    print("\n2. Checking OpenAI API Key...")
    print("-" * 40)
    api_key_ok = check_api_key()

    print("\n3. Checking Watchlist...")
    print("-" * 40)
    watchlist_ok = check_watchlist()

    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)

    if deps_ok and watchlist_ok:
        print("✅ Ready to run!")
        print("\nNext steps:")
        print("  1. python iv_tracker.py         # Run daily scan")
        print("  2. python generate_dashboard.py # Create Excel report")

        if not api_key_ok:
            print("\n⚠️  GPT analysis disabled (no API key)")
            print("   Scanner will still work, just without AI commentary")
    else:
        print("❌ Setup incomplete")
        if not deps_ok:
            print("   → Install missing packages: pip install -r requirements.txt")
        if not watchlist_ok:
            print("   → Create watchlist.txt with your tickers")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()