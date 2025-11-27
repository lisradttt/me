#!/usr/bin/env python3
"""
Comprehensive import test script to verify all modules load correctly.
(Archived copy)
"""

import sys
import traceback

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

tests_passed = 0
tests_failed = 0
errors = []

def test_import(module_name, description=""):
    """Test importing a module and print results"""
    global tests_passed, tests_failed, errors
    
    try:
        __import__(module_name)
        print(f"{GREEN}✓{RESET} {module_name:<40} {description}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"{RED}✗{RESET} {module_name:<40} {description}")
        print(f"  {RED}Error: {str(e)}{RESET}")
        tests_failed += 1
        errors.append((module_name, str(e), traceback.format_exc()))
        return False


print("\n" + "="*80)
print("IMPORT VALIDATION TEST SUITE (ARCHIVED COPY)")
print("="*80 + "\n")

# Test core config first
print(f"{YELLOW}[1] Testing core configuration...{RESET}")
test_import("config", "- Global configuration")
test_import("OWNER", "- Owner/settings module")

# Test KERO.Data
print(f"\n{YELLOW}[2] Testing KERO.Data...{RESET}")
test_import("KERO.Data", "- Data management and MongoDB")

# Test KERO.info
print(f"\n{YELLOW}[3] Testing KERO.info...{RESET}")
test_import("KERO.info", "- Info utilities and handlers")

# Test KERO modules
print(f"\n{YELLOW}[4] Testing KERO command modules...{RESET}")
test_import("KERO.start", "- Start/initialization commands")
test_import("KERO.admin", "- Admin commands")
test_import("KERO.callback", "- Callback handlers")
test_import("KERO.play", "- Music/video playback")
test_import("KERO.tools", "- Tool functions")
test_import("KERO.youtube", "- YouTube integration")

# Test Maker modules
print(f"\n{YELLOW}[5] Testing Maker (Factory) modules...{RESET}")
test_import("Maker.generate", "- Session generation")
test_import("Maker.callbacks", "- Callback handlers for Maker")
test_import("Maker.KERO", "- Main Maker logic")

# Test plugin system
print(f"\n{YELLOW}[6] Testing plugin system...{RESET}")
test_import("plugins", "- Plugin package")
test_import("plugins.load_both", "- Plugin loader")

# Test startup modules
print(f"\n{YELLOW}[7] Testing startup modules...{RESET}")
test_import("start_all", "- Unified startup module")
test_import("bot", "- Main bot instance")
test_import("main", "- Main entrypoint")

# Print summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"{GREEN}Passed: {tests_passed}{RESET}")
print(f"{RED}Failed: {tests_failed}{RESET}")

if errors:
    print(f"\n{RED}ERRORS FOUND:{RESET}\n")
    for module, error, trace in errors:
        print(f"{RED}[{module}]{RESET}")
        print(f"  Error: {error}")
        print()

print("="*80 + "\n")

if tests_failed == 0:
    print(f"{GREEN}✓ All imports successful! Bot should start correctly.{RESET}\n")
    sys.exit(0)
else:
    print(f"{RED}✗ {tests_failed} import(s) failed. Fix errors above before starting bot.{RESET}\n")
    sys.exit(1)
