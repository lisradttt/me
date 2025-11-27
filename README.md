# JoyBoy Music Bot - Deployment Guide

## Project Overview

This is a **Pyrogram-based Telegram Music Bot System** with two main components:

### 🏭 **The Maker (صانع)** - Factory Bot
- Allows creating and managing multiple music bots dynamically
- Session generator for Pyrogram/Telethon accounts
- Bot management commands (start/stop/delete)
- Broadcasting and admin controls

### 🤖 **The Manufactured Bots (المصنوع)** - Music Players
- Each created bot is a music/video player
- Supports YouTube playback
- Voice chat integration with PyTgCalls
- User statistics tracking

---

## Prerequisites

- **Python**: 3.10+
- **MongoDB**: Cloud or local instance (MongoDB Atlas recommended)
- **FFmpeg**: System package (`ffmpeg` command available)
- **Telegram Bot Token**: From BotFather
- **Telegram API Credentials**: From my.telegram.org

---

## Installation

### 1. Clone Repository
```bash
cd /root/mes  # or your target directory
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If pip fails on `tgcrypto` or `py-tgcalls`, those are expected fallbacks for compatibility. The bot will still work with available alternatives.

### 3. Configure Settings

Edit `OWNER.py`:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
OWNER = ["your_telegram_username"]
OWNER_NAME = "Your Display Name"
DATABASE = "mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster0"
CHANNEL = "https://t.me/your_channel"
GROUP = "https://t.me/your_group"
```

### 4. Verify Installation
```bash
python test_imports.py
```

Expected output:
```
✓ config                                - Global configuration
✓ KERO.Data                             - Data management and MongoDB
✓ KERO.info                             - Info utilities and handlers
✓ Maker.KERO                            - Main Maker logic
✓ plugins.load_both                     - Plugin loader
✓ start_all                             - Unified startup module
✓ bot                                   - Main bot instance
✓ main                                  - Main entrypoint

Passed: N
Failed: 0

✓ All imports successful! Bot should start correctly.
```

---

## Running the Bot

### Development Mode
```bash
python main.py
```

### Production Mode (with systemd)

Create `/etc/systemd/system/joyboy-music.service`:
```ini
[Unit]
Description=JoyBoy Music Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mes
ExecStart=/usr/bin/python3 /root/mes/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
systemctl start joyboy-music
systemctl enable joyboy-music
journalctl -u joyboy-music -f  # View logs
```

---

## Project Architecture

```
mes/
├── main.py                 # Primary entrypoint
├── start_all.py           # Unified startup (loads both Maker + KERO)
├── config.py              # Global configuration
├── OWNER.py               # Credentials and constants
├── bot.py                 # Main bot client instance
├── requirements.txt       # Python dependencies
│
├── Maker/                 # Factory bot (creates music bots)
│   ├── KERO.py           # Main Maker logic (bot creation/management)
│   ├── callbacks.py       # Callback handlers
│   └── generate.py        # Session generator
│
├── KERO/                  # Music bot modules (runs in all created bots)
│   ├── Data.py           # MongoDB data access layer
│   ├── info.py           # Utility functions and event handlers
│   ├── start.py          # /start command and handlers
│   ├── admin.py          # Admin/callback commands
│   ├── play.py           # Music playback and voice chat
│   ├── tools.py          # Statistics and tools
│   ├── youtube.py        # YouTube integration
│   ├── callback.py       # Inline button callbacks
│   └── __init__.py        # Package initializer
│
├── plugins/              # Plugin wrapper for Pyrogram
│   ├── __init__.py
│   └── load_both.py      # Imports both Maker and KERO modules
│
└── scripts/
    └── import_audit.py    # Import validation script
```

### How It Works

1. **Startup Phase:**
   - `main.py` calls `start_all.main()` 
   - Pyrogram client starts with `plugins=dict(root="plugins")`
   - `plugins/load_both.py` is automatically loaded
   - It dynamically imports all modules from `Maker` and `KERO`
   - All handlers are registered on the bot client

2. **User Interaction:**
   - User sends `/start` to the Maker bot
   - If they're owner, they see bot creation options
   - They can create new music bots by providing:
     - Bot token (from BotFather)
     - Session string (from session generator)
   - New bots are stored in MongoDB and auto-started

3. **Music Bot Operation:**
   - Each created bot loads the `KERO` handlers
   - Users can add it to groups
   - Bot plays music via PyTgCalls
   - Statistics tracked in MongoDB

---

## Key Modules Explained

### `KERO/Data.py`
- MongoDB connection and collections
- Bot metadata caching
- Developer ID/name tracking
- Video source management
- All database operations

**Exports:** `get_dev()`, `get_bot_name()`, `set_bot_name()`, `get_group()`, `get_channel()`, `get_userbot()`, `get_call()`, etc.

### `KERO/info.py`
- Utility functions for chat/user management
- Playlist management (`db`)
- Voice call helper functions (`Call()`, `helper()`)
- Media download and thumbnail generation
- Active voice chat tracking

**Exports:** `Call()`, `helper()`, `active`, `activecall`, `db`, `add()`, `download()`, `gen_thumb()`, etc.

### `KERO/play.py`
- Music/video playback logic
- PyTgCalls integration
- Stream handling and quality selection
- Playlist queue management
- Voice chat event handlers

### `Maker/KERO.py`
- Bot factory logic
- Creates new bots from tokens and sessions
- Auto-starts created bots
- Broadcasting to all bots
- Blocking/unblocking users

---

## Troubleshooting

### Import Errors

**Error:** `ImportError: cannot import name 'X' from 'KERO.Data'`

**Solution:** Run `python test_imports.py` to identify missing exports. Check `__all__` list in Data.py and info.py.

### MongoDB Connection Failed

**Error:** `pymongo.errors.ServerSelectionTimeoutError`

**Solution:**
1. Verify `MONGO_DB_URL` in `OWNER.py`
2. Check MongoDB cluster network access (IP whitelist)
3. Ensure credentials are correct

### Bot Not Responding

**Error:** Bot receives messages but doesn't respond

**Solution:**
1. Verify `BOT_TOKEN` is correct in `OWNER.py`
2. Check bot has admin rights (if needed for group)
3. Look at logs: `journalctl -u joyboy-music -f`

### PyTgCalls Errors

**Error:** `NotInCallError`, `AlreadyJoinedError`, etc.

**Solution:** These are handled with fallback imports in `play.py`. Ensure:
1. Bot is admin in the group
2. Group has voice chat enabled
3. Session account (userbot) is admin too

---

## Deployment Checklist

- [ ] Python 3.10+ installed
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] `OWNER.py` configured with real credentials
- [ ] `test_imports.py` runs successfully
- [ ] MongoDB connection verified
- [ ] FFmpeg available on system
- [ ] Bot token created and valid
- [ ] Telegram API credentials obtained
- [ ] Bot added to required groups/channels
- [ ] Permissions set correctly (admin where needed)
- [ ] First test: `python main.py` runs without errors
- [ ] Production: systemd service configured and running

---

## Commands

### Maker Bot Commands (Owner Only)

| Command | Description |
|---------|-------------|
| `/start` | Show main menu |
| `صنع بوت` | Create a new music bot |
| `حذف بوت` | Delete a music bot |
| `تفعيل الصانع` | Enable free mode |
| `تعطيل الصانع` | Disable free mode |
| `تفعيل البوتات` | Start all bots |
| `البوتات المصنوعه` | List all created bots |

### Music Bot Commands (User)

| Command | Description |
|---------|-------------|
| `/start` | Show help menu |
| `/play [song]` | Play music from YouTube |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/stop` | Stop and leave voice chat |

---

## Environment Variables (Optional)

Create `.env` file:
```bash
API_ID=12345678
API_HASH=your_api_hash_here
```

If not set, defaults from `config.py` will be used.

---

## Support & Maintenance

### Log Rotation
```bash
# View logs
journalctl -u joyboy-music -n 100  # Last 100 lines
journalctl -u joyboy-music -f       # Follow logs
journalctl -u joyboy-music --since "2 hours ago"
```

### Updating Dependencies
```bash
pip install --upgrade -r requirements.txt
systemctl restart joyboy-music
```

### Backup MongoDB
```bash
mongodump --uri "mongodb+srv://user:pass@cluster.mongodb.net" --out ./backup
```

---

## Performance Tuning

1. **Connection Pooling**: MongoDB motor client uses connection pooling
2. **Caching**: Developer names, group links cached in memory
3. **Async I/O**: All database and network operations are async
4. **Handler Registration**: Handlers registered once on startup, not per-request

---

## License

Proprietary - JoyBoy Project

---

## Contributors

- Developer: @ISIIQ (Mimo)
- Developer: @e2zzz (Kero)  
- Programmer: @AT_W2

---

**Last Updated:** November 27, 2025
