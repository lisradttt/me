"""Run this script on the server to audit imports for `Maker` and `KERO`.

Usage (from repository root):
    python scripts/import_audit.py

It prints each import attempt and writes a summary to
`scripts/import_audit_report.txt` for easier sharing here.
"""
import pkgutil
import importlib
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "import_audit_report.txt"

packages = ["Maker", "KERO"]
errors = []

def log(msg):
    print(msg)
    with open(REPORT, "a", encoding="utf8") as f:
        f.write(msg + "\n")

if REPORT.exists():
    REPORT.unlink()

log("IMPORT AUDIT START\n")

for pkg_name in packages:
    log(f"--- Package: {pkg_name} ---")
    try:
        pkg = importlib.import_module(pkg_name)
        log(f"Package imported: {pkg_name} -> {pkg}")
    except Exception as e:
        log(f"Failed to import package {pkg_name}: {e}")
        log(traceback.format_exc())
        errors.append((pkg_name, None, str(e)))
        continue

    if hasattr(pkg, "__path__"):
        for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
            fullname = f"{pkg_name}.{name}"
            try:
                importlib.import_module(fullname)
                log(f"Imported: {fullname}")
            except Exception as ex:
                log(f"ERROR importing {fullname}: {ex}")
                log(traceback.format_exc())
                errors.append((pkg_name, fullname, str(ex)))
    else:
        log(f"No __path__ for {pkg_name}; skipping submodule scan")

log("\nTop-level entrypoints check:")
for top in ["bot", "main", "start_all"]:
    try:
        importlib.import_module(top)
        log(f"Imported top-level: {top}")
    except Exception as e:
        log(f"ERROR importing top-level {top}: {e}")
        log(traceback.format_exc())
        errors.append(("top", top, str(e)))

log("\nIMPORT AUDIT COMPLETE\n")
log("Summary of errors:")
if not errors:
    log("No import errors detected.")
else:
    for pkg, mod, err in errors:
        log(f"- Package: {pkg}, Module: {mod}, Error: {err}")

log(f"Report saved to: {REPORT}\n")

print("Done. Paste the contents of scripts/import_audit_report.txt here and I'll fix the issues.")
