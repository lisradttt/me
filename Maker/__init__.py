"""
Maker Package - Factory Bot

This package is imported as a Pyrogram plugin and creates music bots.
"""

# This will be patched by the plugin loader
app = None

def set_app_instance(bot_instance):
    """Set the bot instance for all Maker handlers"""
    global app
    app = bot_instance
    print(f"[Maker] Bot instance set to: {app}")

__all__ = ['app', 'set_app_instance']
