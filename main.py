#!/usr/bin/env python3
"""Main entry point for JoyBoy Music Bot System

This script starts the unified bot that loads both:
- Maker (صانع) - Factory for creating music bots
- KERO (المصنوع) - Music bot handlers
"""

import asyncio
import start_all


if __name__ == "__main__":
    try:
        asyncio.run(start_all.main())
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped by user")
    except Exception as e:
        print(f"[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()