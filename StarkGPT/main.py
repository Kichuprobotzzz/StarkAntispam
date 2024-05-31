from pyrogram.errors import *
from pyrogram import *
from pyrogram.handlers import *
from pyrogram.types import *
import pymongo

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

BOT_NAME = "Stark AntiSpam"

LOG_CHANNEL = "StarkAntiSpamErrors"
MONGO_URL = "mongodb+srv://starkai:starkai@cluster0.yxr0olj.mongodb.net/?retryWrites=true&w=majority"
mongo = pymongo.MongoClient(MONGO_URL)

#------------- AntiSpam ---------------#
asdb = mongo["STARKAPIBOT"]
astokensdb = asdb["TOKENS"]
asalertdb = asdb["ALERTSENT"]
asusersdb = asdb["USERS"]
aschatsdb = asdb["CHATS"]
guardb = asdb["GUARD-DB"]
safedb = asdb["SAFEDB"]

#------------ Nudity DB ----------------#
nudityhub = mongo["NudityGen"]
nuditydb = nudityhub["TOKENS"]

API_URL = "https://antispam.marvelcloudsolutions.tech/"

API_KEY = "sathishzus"
ADMIN_API_KEY = "bb6d95bb-dd1b-4bca-9494-ff47b10c6149"

API_ID = "15037283"
API_HASH = "7af9d761267bf6b81ed07f942d87127f"
BOT_TOKEN = "6176049894:AAEe9QO_sJtOp5wjYLYPZKEYx4hglifZjjo"

UPLOAD_TOKEN = "5602157150:AAHmvH-PQWUedKZVpXLlW0m3ClPzgABWtjw"

upapp = Client("UPLOADBOT",api_id=API_ID,api_hash=API_HASH,bot_token=UPLOAD_TOKEN)

app = Client("Stark",api_id=API_ID,api_hash=API_HASH,bot_token=BOT_TOKEN, plugins={"root": "StarkGPT.modules"})
