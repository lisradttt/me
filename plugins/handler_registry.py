"""Handler registration system for JoyBoy Bot

This module provides a way to register handlers on the actual bot instance
instead of using @Client.on_message which doesn't work with Pyrogram's plugin system.
"""

# Global reference to the actual bot instance
_bot_instance = None


def set_bot_instance(bot):
    """Set the actual bot instance that was created in start_all.py"""
    global _bot_instance
    _bot_instance = bot
    print(f"[HANDLER REGISTRY] Bot instance set: {bot}")


def get_bot_instance():
    """Get the actual bot instance"""
    global _bot_instance
    if _bot_instance is None:
        raise RuntimeError(
            "Bot instance not set! Call set_bot_instance() first. "
            "This should be called from start_all.py after bot.start()"
        )
    return _bot_instance


def register_handler(filter_obj, group=0):
    """Decorator to register a handler on the actual bot instance
    
    Usage:
        @register_handler(filters.command("start"))
        async def start_handler(client, message):
            ...
    """
    def decorator(func):
        bot = get_bot_instance()
        bot.add_handler(
            (lambda client, message: func(client, message), filter_obj),
            group=group
        )
        return func
    return decorator
