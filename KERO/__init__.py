"""
KERO Package - Music Bot Handlers

This package is imported as a Pyrogram plugin and needs to register
handlers on the actual bot instance.
"""

# This will be patched by the plugin loader
app = None

def set_app_instance(bot_instance):
    """Set the bot instance for all KERO handlers"""
    global app
    app = bot_instance
    print(f"[KERO] Bot instance set to: {app}")

__all__ = ['app', 'set_app_instance']
