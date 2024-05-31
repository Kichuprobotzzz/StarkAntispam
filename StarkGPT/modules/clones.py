from pyrogram.errors import *
from pyrogram import *
from pyrogram.handlers import *
from pyrogram.types import *
from StarkGPT.main import *

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
mongo_dbb = MongoClient(MONGO_URL)
db = mongo_dbb["STARKANTISPAMROBOT"]
tokensdb = db['TOKENS']

import re
pattern = r'\d+:[\w-]+'

async def get_all_session():
    lol = [n async for n in tokensdb.find({})]
    return lol

async def add_session(client,is_start):
    await tokensdb.insert_one({"token": client, 'is_start': is_start})

async def del_session_id(user_id):
    await tokensdb.delete_many({"_id": user_id})

async def add_username(name):
    await alivedb.insert_one({"uname": name})


@Client.on_message(filters.command("clone"))
async def clone(_, msg: Message):
  try:
      chat = msg.chat
      text = await msg.reply("Usage:\n\n /clone [BOT TOKEN]")
      try:
        phone = msg.command[1]
        await text.edit("Please Wait...")
      except:
         text.edit("Usage:\n\n /clone [BOT TOKEN]")
      try:
          client = Client(phone, API_ID, API_HASH, bot_token=phone, plugins={"root": "StarkGPT.modules"})
          await client.start()
          idle()
          user = await client.get_me()
          await add_session(phone,"yes")
          return await text.edit(f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning.\nTry /start in Your Clone!")
      except Exception as e:
          return await text.edit(f"**ERROR:** `{str(e)}`\nTry /clone [BOT TOKEN] to Clone again.")
  except Exception as e:
    pass
  
@Client.on_message(filters.command("sclone"))
async def sclone(_, msg: Message):
  try:
      chat = msg.chat
      text = await msg.reply("Usage:\n\n /clone [BOT TOKEN]")
      try:
        phone = msg.command[1]
        await text.edit("Please Wait...")
      except:
         text.edit("Usage:\n\n /clone [BOT TOKEN]")
      try:
          client = Client(phone, API_ID, API_HASH, bot_token=phone, plugins={"root": "StarkGPT.plugins"})
          await client.start()
          idle()
          user = await client.get_me()
          await add_session(phone,"no")
          return await text.edit(f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning.\nTry /start in Your Clone!")
      except Exception as e:
          return await text.edit(f"**ERROR:** `{str(e)}`\nTry /clone [BOT TOKEN] to Clone again.")
  except Exception as e:
    pass
  
@Client.on_message(filters.forwarded & filters.private)
async def for_clone(client, message):
    if message.forward_from.id==93372553:
        pass
    else:
        return
    try:
        msg = message.text
        match = re.search(pattern, msg)
        if match:
            phone = match.group(0)
            try:
                text = await message.reply("Booting Your Client")
                client = Client(phone, API_ID, API_HASH, bot_token=phone, plugins={"root": "StarkGPT.modules"})
                await client.start()
                idle()
                user = await client.get_me()
                await add_session(phone,"yes")
                return await text.edit(f"Your Client Has Been Successfully Started As @{user.username}! ✅\n\nThanks for Cloning.\nTry /start in Your Clone!")
            except Exception as e:
                return await text.edit(f"**ERROR:** `{str(e)}`\nTry /clone [BOT TOKEN] to Clone again.")
        else:
            return await message.reply("Forward Message which Consists Bot Token!")
    except Exception as e:
        pass

@Client.on_message(filters.command("rmclone"))
async def rmclone(_, msg: Message):
  try:
      text = await msg.reply("Try /rmclone [BOT ID]")
      cmd = msg.command
      phone = msg.command[1]
      try:
          await del_session_id(phone)
          await text.edit(f"`{phone}` token Has been Removed Successfully!\nYour session will be stop after my Restart!")
      except Exception as e:
          await text.edit(f"**Error:** \n`{e}`")
  except Exception as e:
    pass
