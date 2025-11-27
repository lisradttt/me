"""Wrapper plugin: import modules from Maker and KERO packages.

This plugin runs when Pyrogram loads and:
1. Gets the actual bot instance from Pyrogram's plugin system
2. Injects it into Maker and KERO packages
3. Imports all modules so handlers register on the bot
"""
import pkgutil
import importlib
import sys
import traceback
import inspect
from pyrogram import Client


def get_client_from_stack():
    """Get the Client instance that called this plugin (Pyrogram's plugin loader)"""
    for frame_info in inspect.stack():
        frame = frame_info.frame
        # Look for 'self' which should be the Client instance
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            # Check if it's a Pyrogram Client
            if isinstance(obj, Client):
                print(f"[PLUGIN] Found Client instance in frame: {frame_info.function}")
                return obj
        # Also check locals for 'client' parameter
        if 'client' in frame.f_locals:
            obj = frame.f_locals['client']
            if isinstance(obj, Client):
                print(f"[PLUGIN] Found 'client' in frame: {frame_info.function}")
                return obj
    return None


def inject_bot_into_package(package_name: str, bot_instance):
    """Inject bot instance into a package before importing its modules"""
    if not bot_instance:
        return False
        
    try:
        pkg = importlib.import_module(package_name)
        
        # Call set_app_instance if it exists
        if hasattr(pkg, 'set_app_instance'):
            pkg.set_app_instance(bot_instance)
            print(f"[PLUGIN] Injected bot into {package_name}")
            return True
        else:
            print(f"[PLUGIN WARNING] {package_name} doesn't have set_app_instance")
            return False
    except Exception as e:
        print(f"[PLUGIN ERROR] Could not inject bot into {package_name}: {e}")
        return False


def import_package_modules(package_name: str) -> None:
    """Import all modules from a package to register handlers"""
    try:
        pkg = importlib.import_module(package_name)
        if not hasattr(pkg, '__path__'):
            print(f"[PLUGIN ERROR] {package_name} is not a package")
            return
    except Exception as e:
        print(f"[PLUGIN ERROR] Could not import package {package_name}: {e}")
        return

    try:
        modules = list(pkgutil.iter_modules(pkg.__path__))
        
        for finder, name, ispkg in modules:
            if name.startswith('_'):
                continue
                
            fullname = f"{package_name}.{name}"
            try:
                # Import the module - this will register handlers
                importlib.import_module(fullname)
                print(f"[PLUGIN] ✓ {fullname}")
                
            except Exception as ex:
                print(f"[PLUGIN ERROR] Failed {fullname}: {ex}")
                
    except Exception as e:
        print(f"[PLUGIN ERROR] Error in {package_name}: {e}")


# Main execution
print("[PLUGIN] === JoyBoy Bot Plugin Loader ===")

# Get the actual bot instance
bot = get_client_from_stack()

if not bot:
    print("[PLUGIN ERROR] Could not find bot instance!")
    print("[PLUGIN ERROR] Handlers will NOT register!")
else:
    print(f"[PLUGIN] Bot found: {bot}")
    
    # Inject bot into packages
    print("[PLUGIN] Injecting bot into packages...")
    inject_bot_into_package("Maker", bot)
    inject_bot_into_package("KERO", bot)
    
    # Now import modules so handlers register
    print("[PLUGIN] Loading Maker modules...")
    import_package_modules("Maker")
    
    print("[PLUGIN] Loading KERO modules...")
    import_package_modules("KERO")

print("[PLUGIN] === Plugin Loading Complete ===")

