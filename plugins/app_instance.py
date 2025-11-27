"""
Global app instance for handlers
This is the actual bot that handlers will register to
"""

from pyrogram import Client

# This will be set to the actual bot instance from start_all.py
app = None


def set_app(client):
    """Set the global app instance"""
    global app
    app = client
    print(f"[APP REGISTRY] Global app set to: {app}")


def get_app():
    """Get the global app instance"""
    global app
    if app is None:
        raise RuntimeError("App not initialized. Call set_app() first.")
    return app
