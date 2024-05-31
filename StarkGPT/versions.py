from pyrogram import __version__
import platform
from pymongo._version import version as mongov

StarkGPT_V = "v0.0.1"
PYROGRAM_V = f"v{__version__}"
DEVICE_MODEL = f"{platform.python_implementation()} {platform.python_version()}"
SYSTEM_V = f"{platform.system()} {platform.release()}"
MONGO_V = f"v{mongov}"

V_TEXT = f"""
**StarkGPT:** `{StarkGPT_V}`
**Bot Version:** `v5.2.3`
**Pyrogram:** `{PYROGRAM_V}`
**MongoDB:** `{MONGO_V}`
**Device Model:** `{DEVICE_MODEL}`
**System Version:** `{SYSTEM_V}`
"""