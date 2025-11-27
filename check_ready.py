#!/usr/bin/env python3
"""
Final verification - Check that everything is ready to go
التحقق النهائي - تأكد من أن كل شيء جاهز
"""

import sys
import os

def print_status(status, message):
    """Print formatted status message"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")
    return status

def main():
    print("=" * 70)
    print("JoyBoy Bot - Final Pre-Launch Verification")
    print("=" * 70)
    
    all_ok = True
    
    # Check files exist
    print("\n📁 Checking critical files...")
    files_to_check = [
        ('main.py', 'Main entry point'),
        ('start_all.py', 'Bot startup'),
        ('config.py', 'Configuration'),
        ('OWNER.py', 'Credentials'),
        ('requirements.txt', 'Dependencies'),
        ('KERO/Data.py', 'Database layer'),
        ('KERO/info.py', 'Utility functions'),
        ('Maker/KERO.py', 'Factory bot'),
        ('plugins/load_both.py', 'Plugin loader'),
    ]
    
    for filename, description in files_to_check:
        exists = os.path.isfile(filename)
        all_ok &= print_status(exists, f"{description:25} ({filename})")
    
    # Check directories exist
    print("\n📂 Checking directories...")
    dirs_to_check = [
        ('KERO', 'Music handlers'),
        ('Maker', 'Factory bot'),
        ('plugins', 'Plugin system'),
        ('scripts', 'Utility scripts'),
    ]
    
    for dirname, description in dirs_to_check:
        exists = os.path.isdir(dirname)
        all_ok &= print_status(exists, f"{description:25} ({dirname}/)")
    
    # Check Python version
    print("\n🐍 Checking Python environment...")
    py_version = sys.version_info
    version_ok = py_version.major >= 3 and py_version.minor >= 8
    all_ok &= print_status(version_ok, f"Python {py_version.major}.{py_version.minor}.{py_version.micro} (3.8+ required)")
    
    # Check syntax of key files
    print("\n✔️ Checking file syntax...")
    syntax_ok = True
    for filename in ['main.py', 'start_all.py', 'config.py']:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                compile(f.read(), filename, 'exec')
            print_status(True, f"Syntax OK: {filename}")
        except SyntaxError as e:
            print_status(False, f"Syntax ERROR in {filename}: {e}")
            syntax_ok = False
    all_ok &= syntax_ok
    
    # Final result
    print("\n" + "=" * 70)
    if all_ok:
        print("✅ ALL CHECKS PASSED - Ready to launch!")
        print("\nTo start the bot, run:")
        print("  python3 main.py")
        print("\nOr use quick start:")
        print("  python3 quick_run.py")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Fix errors above before launching")
        return 1

if __name__ == "__main__":
    sys.exit(main())
