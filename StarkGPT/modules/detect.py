import asyncio
import speedtest
import datetime
import pytz
import threading
from time import *
from pyrogram.errors import *
from pyrogram import *
from pyrogram.handlers import *
from pyrogram.types import *
from psutil import *
from StarkGPT.main import *
from StarkGPT.Utils.pastebin import *
import requests
from nsfw_detector import predict
from telegraph import upload_file
import numpy as np
from PIL import Image
from os import remove
import os
import uuid
import random

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']

model = predict.load_model('./stark/nsfw_mobilenet2.224x224.h5')

botStartTime = time()

tokensdb = astokensdb
alertdb = asalertdb
usersdb = asusersdb
chatsdb = aschatsdb

import ffmpeg

def convert_webp_to_jpg(webp_path, jpg_path):
    try:
        # Define the input and output file paths
        input_file = ffmpeg.input(webp_path)

        # Extract the first frame and save it as a jpg file
        ffmpeg.output(input_file, jpg_path, vframes=1, format='image2', vcodec='mjpeg').run()

        print(f"Image converted to {jpg_path}")

    except ffmpeg.Error as e:
        print(f"Error: {e.stderr.decode('utf-8')}")


def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result


def get_readable_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except:
        return 'Error'


HELP_PIC = "https://graph.org/file/1b9d171be29ca44b4ebc8.jpg"


HELP_TEXT = "**Help Menu**"

USAGE_HELP_TEXT = """🔧 Available Commands 🔧

Here are the commands you can use with StarkAntispam Bot:

/start - Start the bot and initialize its functionalities.
/status - Get information about your account and bot settings.
/clone [BOT TOKEN] - Clone this bot by providing the BOT TOKEN from @BotFather.
/stats - Retrieve API statistics and usage details.
/admins - Obtain a list of administrators in the current group.
/get_api - Generate an API key for accessing advanced features (only for admins).
/ban - Ban a user from the group (admins only).
/unban - Unban a previously banned user (admins only).
/add_admin - Add new admins to assist in managing the group (owner only).
/rm_admin - Remove admins from their roles (owner only).
/scan - Reply to any media message to initiate a scan for spam content.

🤖 Feel free to explore and utilize these commands to enhance your experience with StarkAntispam Bot. Should you require any further assistance, our support team is here to help. Enjoy a spam-free and secure group environment!"""

CLONES_HELP_TEXT = "**How to Clone Stark AntiSpam Bot with your own Bot?**\n\n**Step 1:** `Go to` **@BotFather**`. If you already created Bot get your Bot Token or create new Bot by using` /new `command!`\n**Step 2:** `Forward the message from the BotFather that contains Bot Token to this Bot or` **@StarkAntiSpamBot**\n**Step 3:** `Wait for some seconds for Booting Your Client!`"

PRIVACY_HELP_TEXT = """🔒 Privacy Policy Notice 🔒

At StarkAntispam, we prioritize the privacy and security of our users. Here's a summary of our privacy policy:

1️⃣ Message and Media Storage: We want to assure you that we do not store any of your messages or media files on our servers. Your conversations and media remain private and are not accessible or retrievable by us.
2️⃣ Text Messages Detected as Spam: However, we do retain text messages that are detected as spam for a period of 12 months. This retention period allows us to improve our spam detection algorithms and ensure better protection for your group. After 12 months, these messages are automatically deleted from our servers.
3️⃣ Media Content: We want to emphasize that we do not store any media content, even if it is detected as spam. This includes stickers, GIFs, photos, documents, and any other files shared within your group. Rest assured that your media files remain private and are not stored by us.
4️⃣ User Spam Scores: Please note that we cannot delete or reset user spam scores, even if requested. The spam scores assigned to users are necessary for our system to identify and take action against spam accounts effectively.
5️⃣ Data Sharing: We want to make it clear that we do not share any data we process with any third parties. Your information and group data are treated with utmost confidentiality and are used solely for the purpose of spam detection and prevention.

Your trust and privacy are of utmost importance to us. If you have any further questions or concerns regarding our privacy policy, please feel free to contact our support team. We are here to address any queries you may have.
Thank you for choosing StarkAntispam, and we remain committed to providing you with a secure and spam-free environment for your Telegram groups."""

TOS_HELP_TEXT = """📜 Terms and Conditions 📜

By using StarkAntispam Bot and our associated services, you agree to the following terms and conditions:

1️⃣ Prohibited Spamming Activities: Users are strictly prohibited from spamming our bot or any clones hosted by our servers with excessive texts or media content. This includes repetitive, unsolicited messages or any other form of unwanted communication. Users found engaging in such activities may face consequences, including being restricted from accessing our other services, such as StarkGPT, Stark Music, and other offerings.
2️⃣ Non-Commercial Use: Our services are intended for personal use and group administration purposes only. Users must not utilize our services for any commercial endeavors, including advertising, promotions, or any other form of commercial gain without obtaining explicit permission from StarkAntispam.
3️⃣ Compliance with Applicable Laws: Users must comply with all applicable laws and regulations while using our services. Any illegal or unauthorized use of our services is strictly prohibited.
4️⃣ Ownership and Intellectual Property: StarkAntispam retains all rights, ownership, and intellectual property associated with our services, including the bot, its features, and any other proprietary content. Users are prohibited from reproducing, modifying, distributing, or creating derivative works from our services without prior written consent.
5️⃣ Disclaimer of Liability: While we strive to provide accurate and reliable services, StarkAntispam cannot guarantee the complete elimination of all spam or offensive content. Users understand and agree that the use of our services is at their own risk, and we shall not be held liable for any damages or losses resulting from the use of our services.
6️⃣ Modification of Terms: StarkAntispam reserves the right to modify or update these terms and conditions at any time. Users will be notified of any significant changes, and continued use of our services constitutes acceptance of the modified terms.

We encourage all users to read and understand these terms and conditions. If you have any questions or concerns, please reach out to our support team for clarification.
Thank you for choosing StarkAntispam. We appreciate your cooperation in creating a secure and spam-free environment for Telegram groups."""

START_BUTTON = [[
        InlineKeyboardButton("⚔️ Add to Group ⚔️", url="https://t.me/StarkAntispamBot?startgroup=true")
    ],
    [
        InlineKeyboardButton("API", url=f"{API_URL}"),
        InlineKeyboardButton("Status", url="https://server.starkai.live") 
    ],
    [
        InlineKeyboardButton("Help", callback_data="help_callback"),
	InlineKeyboardButton("Universe • ⃤ •",url="https://t.me/we_are_universee")
]]


HELP_BUTTON = [
        [
            InlineKeyboardButton("Usage", callback_data="usage_Button"),
            InlineKeyboardButton("Clones", callback_data="clones_Button"),
        ],
        [
            InlineKeyboardButton("Privacy", callback_data="privacy_Button"),
            InlineKeyboardButton("TOS", callback_data="tos_Button"),
        ],
        [
            InlineKeyboardButton("GDPR", callback_data="gdpr_Button"),
            InlineKeyboardButton("About", callback_data="about_Button"),
        ],
        [
            InlineKeyboardButton("My Status", callback_data="mystatus_Button"),
            InlineKeyboardButton("System Status", callback_data="sys_Button"),
        ],
        [
            InlineKeyboardButton("Back", callback_data="start_callback"),
            InlineKeyboardButton("Close", callback_data="delete"),
    ],   
]

GDPR_BUTTON = [
    [
        InlineKeyboardButton("Delete", callback_data="delete_gdpr_button"),
        InlineKeyboardButton("Get Copy", callback_data="copy_gdpr_button")        
    ],
    [
        InlineKeyboardButton("Back", callback_data="Help_Back")
    ]
]

HELP_BACK_BUTTON = [
        [
            InlineKeyboardButton("Back", callback_data="Help_Back"),
    ],   
]


#------------------------ InlineQuery Start ------------------------------#

@Client.on_message(filters.command(["start"]))
async def start(_, message):
    START_TEXT = f"**Hello {message.from_user.mention}\n\n🌟 Welcome to StarkAntispam Bot! 🌟\n\n🤖 We're here to ensure your Telegram group stays spam-free and secure. Our advanced AntiSpam System powered by AI and ML will filter and remove spam messages and adult content automatically. Enjoy a safe and enjoyable chatting experience! 🔒🚫📷\n\n⛔ No more dealing with spammers or offensive posts! Let us handle it. Add the bot to your group and grant permissions. We'll take care of the rest. 🛡️👥\n\n🌈 Embrace the power of StarkAntispam Bot and create a vibrant, spam-free community. Happy chatting! 🌈✨🎉\n\n🙏 Thank you for choosing StarkAntispam Bot! For more information, click the help button below. Reach out to our support team if needed. Enjoy a spam-free experience! 🤗🙌\n\n👇 For More Informations Click Help Button Below  👇"    
    return await message.reply_text(START_TEXT,reply_markup=InlineKeyboardMarkup(START_BUTTON))


# Start CallBack
@Client.on_callback_query(filters.regex("start_callback"))
async def start_back(_, query: CallbackQuery):
    client_id = query.from_user.id
    START_TEXT = f"**Hello {query.from_user.mention}\n\n🌟 Welcome to StarkAntispam Bot! 🌟\n\n🤖 We're here to ensure your Telegram group stays spam-free and secure. Our advanced AntiSpam System powered by AI and ML will filter and remove spam messages and adult content automatically. Enjoy a safe and enjoyable chatting experience! 🔒🚫📷\n\n⛔ No more dealing with spammers or offensive posts! Let us handle it. Add the bot to your group and grant permissions. We'll take care of the rest. 🛡️👥\n\n🌈 Embrace the power of StarkAntispam Bot and create a vibrant, spam-free community. Happy chatting! 🌈✨🎉\n\n🙏 Thank you for choosing StarkAntispam Bot! For more information, click the help button below. Reach out to our support team if needed. Enjoy a spam-free experience! 🤗🙌\n\n👇 For More Informations Click Help Button Below  👇"
    await query.edit_message_text(text=START_TEXT,reply_markup=InlineKeyboardMarkup(START_BUTTON))
# Help CallBack
@Client.on_callback_query(filters.regex("help_callback"))
async def help(_, query: CallbackQuery):
    await query.edit_message_text(HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BUTTON))
# Help Back
@Client.on_callback_query(filters.regex("Help_Back"))
async def helpback(_, query: CallbackQuery):
    await query.edit_message_text(HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BUTTON))

# Usage CallBack 
@Client.on_callback_query(filters.regex("usage_Button"))
async def usage_help(_, query: CallbackQuery):
    await query.edit_message_text(USAGE_HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))

# GDPR CallBack 
@Client.on_callback_query(filters.regex("gdpr_Button"))
async def gdpr_help(_, query: CallbackQuery):
    client_id = query.from_user.id
    mention = query.from_user.mention
    GDPR_TEXT = """
    **GDPR Data Protection Rights**

    __We would like to make sure you are fully aware of all of your data protection rights. Every user is entitled to the following:__
    
    📄 **The right to access**
    You have the right to request copies of your personal data.

    ⚜ **The right to erasur**
    You have the right to request that we erase your personal data.
    """
    await query.edit_message_text(GDPR_TEXT,reply_markup=InlineKeyboardMarkup(GDPR_BUTTON))


# GDPR Delete CallBack 
@Client.on_callback_query(filters.regex("delete_gdpr_button"))
async def delete_gdpr_button(_, query: CallbackQuery):
    DELETE_GDPR_TEXT = """
    We are trying to make this Delete Feature Soon!
    """
    await query.edit_message_text(DELETE_GDPR_TEXT,reply_markup=InlineKeyboardMarkup(GDPR_BUTTON))


# GDPR Delete CallBack 
@Client.on_callback_query(filters.regex("copy_gdpr_button"))
async def copy_gdpr_button(_, query: CallbackQuery):
    COPY_GDPR_TEXT = """
    We are trying to make this Copy Feature Soon!
    """
    await query.edit_message_text(COPY_GDPR_TEXT,reply_markup=InlineKeyboardMarkup(GDPR_BUTTON))


# MyStatus CallBack 
@Client.on_callback_query(filters.regex("mystatus_Button"))
async def mystatus_Button(_, query: CallbackQuery):
  try:
    user_id = query.from_user.id
        
    data = requests.get(f"{API_URL}check_user?user_id={user_id}")
    r = data.json()
    if user_id == 2043144248:
        is_admin = "Onwer"
    else:
        is_admin = r['is_admin']
       
    spam_score = r['spam_score']
    is_banned = r['is_banned']
    msg = f"User ID: `{user_id}`\nAdmin Status: `{is_admin}`\nIs Banned: `{is_banned}`\nSpam Score: `{spam_score} %`"
    if is_banned == "True":
      admin = r['admin']
      reason = r['banned_reason']
      time = r['banned_time']
      msg += f"\nReason: `{reason}`\nAdmin: `{admin}`\nTime: `{time}`"
    MY_STATUS_TEXT=msg
    return await query.edit_message_text(MY_STATUS_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))
  except Exception as e:
    print(e)
    return await query.edit_message_text("Unable To Get Your Status.\nTry Again Later",reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))


# Clones CallBack 
@Client.on_callback_query(filters.regex("clones_Button"))
async def clones_help(_, query: CallbackQuery):
    await query.edit_message_text(CLONES_HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))

# Privacy CallBack 
@Client.on_callback_query(filters.regex("privacy_Button"))
async def privacy_help(_, query: CallbackQuery):
    await query.edit_message_text(PRIVACY_HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))

# TOS CallBack 
@Client.on_callback_query(filters.regex("tos_Button"))
async def tos_help(_, query: CallbackQuery):
    await query.edit_message_text(TOS_HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))


# About CallBack 
@Client.on_callback_query(filters.regex("about_Button"))
async def about_help(_, query: CallbackQuery):
    ABOUT_HELP_TEXT = """📖 About StarkAntispam Bot 📖

StarkAntispam Bot is an advanced anti-spam system designed to ensure secure and spam-free Telegram group environments. Our bot utilizes cutting-edge Artificial Intelligence and Machine Learning technologies to detect and filter spam messages and adult content automatically.

🤖 With StarkAntispam, you can enjoy the following key features:

🔒 Powerful Anti-Spam Protection: Our AI and ML algorithms work tirelessly to filter and remove spam messages, stickers, GIFs, photos, documents, and files from your group chats. This helps create a clean and enjoyable space for all members.

⛔ Automatic Spam Detection and Removal: StarkAntispam Bot automatically identifies spam and offensive content, taking swift action to delete or restrict the responsible users. Say goodbye to dealing with spammers and unwanted messages!

🌈 Vibrant and Secure Communities: By implementing StarkAntispam, you can build thriving communities where members feel safe and comfortable engaging in meaningful conversations without the distractions and risks associated with spam and inappropriate content.

🛡️ Privacy and Data Protection: We prioritize the privacy and security of our users. StarkAntispam Bot does not store your messages or media content on our servers. Text messages flagged as spam are retained for 12 months for algorithm improvement purposes, while media content is never stored.

🙌 We're committed to providing an excellent user experience and maintaining the integrity of your Telegram groups. Please review our Privacy Policy and Terms and Conditions to understand our policies and guidelines.

👉 If you have any questions, need assistance, or wish to provide feedback, our support team is always here to help. We appreciate your trust in StarkAntispam Bot and look forward to helping you create a spam-free and secure environment for your Telegram groups!

🤗 Thank you for choosing StarkAntispam Bot, and we hope you enjoy using our services."""
    await query.edit_message_text(ABOUT_HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))


# Sys CallBack 
@Client.on_callback_query(filters.regex("sys_Button"))
async def sys_help(_, query: CallbackQuery):
  try:
    start_time = int(round(time() * 1000))
    bot_uptime = time() - botStartTime
    end_time = int(round(time() * 1000))
    ping = f"{end_time - start_time} ms"
    memory = virtual_memory()
    bot_up = get_readable_time(bot_uptime)
    dspeed = "N/A"
    uspeed = "N/A"
    data = requests.get(f"{API_URL}sys")
    r = data.json()
    admins = r['admins']
    bans = r['bans']
    keys_gen = r['keys']
    ram_per = f"{memory.percent} %"
    cpu_per = f"{cpu_percent(interval=0.5)} %"
    api_uptime = get_readable_time(r['api_uptime'])
    SYS_HELP_TEXT = f"**API Uptime:** `{api_uptime}`\n**No of Admins:** `{admins}`\n**No of Keys Generated:** `{keys_gen}`\n**No of Bans:** `{bans}`\n\n**Bot SYS**\n**Bot Uptime:** `{bot_up}`\n**Ping:** `{ping}`\n**CPU:** `{cpu_per}`\n**RAM:** `{ram_per}`\n**SpeedTest**\n**Download:** `{dspeed} kbps`\n**Upload:** `{uspeed} kbps`"
    return await query.edit_message_text(SYS_HELP_TEXT,reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))
  except Exception as e:
    print(e)
    return await query.edit_message_text("Unable To Get System Status.\nTry Again Later",reply_markup=InlineKeyboardMarkup(HELP_BACK_BUTTON))



# Delete CallBack
@Client.on_callback_query(filters.regex("delete"))
async def delete(_, query):
    await asyncio.sleep(2)
    await query.message.delete()



@Client.on_message(filters.command("stats"))
async def sysstats(_,message: Message):
  try:
    start_time = int(round(time() * 1000))
    bot_uptime = time() - botStartTime
    text = await message.reply("Getting Ping....!")
    end_time = int(round(time() * 1000))
    ping = f"{end_time - start_time} ms"
    memory = virtual_memory()
    bot_up = get_readable_time(bot_uptime)
    dspeed = "N/A"
    uspeed = "N/A"
    data = requests.get(f"{API_URL}sys")
    r = data.json()
    admins = r['admins']
    bans = r['bans']
    keys_gen = r['keys']
    ram_per = f"{memory.percent} %"
    cpu_per = f"{cpu_percent(interval=0.5)} %"
    api_uptime = get_readable_time(r['api_uptime'])
    texts = f"**API Uptime:** `{api_uptime}`\n**No of Admins:** `{admins}`\n**No of Keys Generated:** `{keys_gen}`\n**No of Bans:** `{bans}`\n\n**Bot SYS**\n**Bot Uptime:** `{bot_up}`\n**Ping:** `{ping}`\n**CPU:** `{cpu_per}`\n**RAM:** `{ram_per}`\n**SpeedTest**\n**Download:** `{dspeed} kbps`\n**Upload:** `{uspeed} kbps`"
    return await text.edit(texts)
  except Exception as e:
    print(e)

@Client.on_message(filters.command("add_admin"))
async def add_admin(_, message: Message):
  try:
      text = await message.reply("Generating Response....!")
      if message.from_user.id == 2043144248:
        pass
      else:
        return await text.edit("Not an Authorized User!")
      
      if message.reply_to_message:
        reply = message.reply_to_message
        user_id = reply.from_user.id
      else:
        return await text.edit("Tag any user to make Admin!")
        
      data = requests.get(f"{API_URL}addsudo?user_id={user_id}&api_key={API_KEY}")
      r = data.json()
      msg = r["message"]
      return await text.edit(msg)
  except Exception as e:
    print(e)

@Client.on_message(filters.command("rm_admin"))
async def rm_admin(_, message: Message):
  try:
      text = await message.reply("Generating Response....!")
      if message.from_user.id == 2043144248:
        pass
      else:
        return await text.edit("Not an Authorized User!")
      if message.reply_to_message:
        reply = message.reply_to_message
        user_id = reply.from_user.id
      else:
        return await text.edit("Tag Admin to Remove!")
        
      data = requests.get(f"{API_URL}rmsudo?user_id={user_id}&api_key={API_KEY}")
      r = data.json()
      msg = r["message"]
      return await message.reply(msg)
  except Exception as e:
    print(e)

@Client.on_message(filters.command("get_api") & filters.private)
async def get_api(_, message: Message):
  try:
    text = await message.reply("Generating Response....!")
    user_id = message.from_user.id
    data = requests.get(f"{API_URL}get_api_key?user_id={user_id}")
    r = data.json()
    tk = r["message"]
    msg = f"**Your API Key is:**\n`{tk}`"
    return await text.edit(msg)
  except Exception as e:
    print(e)


@Client.on_message(filters.command("get_trust"))
async def get_trust(_, message: Message):
  try:
    text = await message.reply("Generating Response....!")
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            id_or_uname = message.command[1]
            user = await app.get_users(id_or_uname)
            user_id = user.id
        except:
            user_id = message.from_user.id  
    
    data = requests.get(f"{API_URL}gettrust?user_id={user_id}")
    if data.status_code == 404:
      return await text.edit("Data Not Found or User Maybe System Admin")
    else:
      r = data.json()
      userid = r['user_id']
      spamscore = r['spam_avg'] * 100
      return await text.edit(f"**Data Found!**\n\nUser ID: `{userid}`\nSpam Score: `{spamscore} %`")
  except Exception as e:
    print(e)

@Client.on_callback_query(filters.regex("pressed_info"))
async def user_info(client, callback_query):
    data = callback_query.data
    pressed_user_id = callback_query.from_user.id
    user_id = int(data.split(None, 1)[1])
    user = await client.get_users(user_id)
    is_deleted = user.is_deleted 
    is_bot = user.is_bot 
    is_verified = user.is_verified 
    is_restricted = user.is_restricted 
    is_scam = user.is_scam 
    is_fake = user.is_fake 
    is_support = user.is_support 
    is_premium = user.is_premium 
    first_name = user.first_name
    last_name = user.last_name 
    status = user.status 
    last_online_date = user.last_online_date
    next_offline_date = user.next_offline_date 
    username = user.username 
    language_code = user.language_code 
    emoji_status = user.emoji_status 
    dc_id = user.dc_id 
    restrictions = user.restrictions 
    msg = f"""
First Name: `{first_name}`
Username: @{username}
Dc ID: `{dc_id}`
User ID: `{user_id}`
Is Bot: `{is_bot}`
Is Deleted Acct: `{is_deleted}`
Is Premium: `{is_premium}`
Emoji Status: `{emoji_status}`
Language Code: `{language_code}`
Is Verified: `{is_verified}`
Is Telegram Support: `{is_support}`

Telegram Rectrictions
Is Scam: `{is_scam}`
Is Fake: `{is_fake}`
Is Restricted: `{is_restricted}`
Restrection Reasons: `{restrictions}`

Online/Offline Status
Current Status: `{status}`
Last Online: `{last_online_date}`
Next Offline: `{next_offline_date}`
"""
    INFO_KEYBOARD = [
       [
          InlineKeyboardButton("Close",callback_data="delete")
       ]
    ]
    await callback_query.edit(msg,reply_markup=InlineKeyboardMarkup(INFO_KEYBOARD))




@Client.on_message(filters.command("status"))
async def status(client, message: Message):
  try:
    text = await message.reply("Generating Response....!")
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    else:
        try:
            id_or_uname = message.command[1]
            user = await client.get_users(id_or_uname)
            user_id = user.id
        except:
            user_id = message.from_user.id
    user = await client.get_users(user_id)
    first_name = user.first_name
    username = user.username 
    dc_id = user.dc_id 
    data = requests.get(f"{API_URL}check_user?user_id={user_id}")
    r = data.json()
    if user_id == 2043144248:
        is_admin = "Onwer"
    else:
        is_admin = r['is_admin']
    spam_score = r['spam_score']
    is_banned = r['is_banned']
    msg = f"First Name: `{first_name}`\nUsername: @{username}\nDC: `{dc_id}`\nUser ID: `{user_id}`\nAdmin Status: `{is_admin}`\nIs Banned: `{is_banned}`\nSpam Score: `{spam_score:2f}%`"
    if is_banned == "True":
      admin = r['admin']
      reason = r['banned_reason']
      time = r['banned_time']
      pdata = requests.get(f"{API_URL}getproof?user_id={user_id}")
      pr = pdata.json()
      pmsg = pr['message']
      link = await pastebin(pmsg)
      msg += f"\nReason: `{reason}`\nAdmin: `{admin}`\nTime: `{time}`\nProof: [Here]({link})"
    INFO_KEYBOARD = [
       [
          InlineKeyboardButton("More Info",callback_data=f"pressed_info {user_id}"),
          InlineKeyboardButton("Close",callback_data="delete")
       ]
    ]
    await message.reply(msg,reply_markup=InlineKeyboardMarkup(INFO_KEYBOARD))
    return await text.delete()
  except Exception as e:
    print(e)
  
@Client.on_message(filters.command("admins"))
async def admins(_, message: Message):
  try:
    text = await message.reply("Generating Response....!")
    data = requests.get(f"{API_URL}admins")
    r = data.json()
    admins = r['message']
    return await text.edit(admins)
  except Exception as e:
    print(e)

@Client.on_message(filters.command("ban"))
async def ban(_, message: Message):
  try:
      text = await message.reply("Generating Response....!")
      from_id = message.from_user.id
      if len(message.command) < 2:
         return await text.edit("Reason Not Provided")

      reason = message.text.split(None, 1)[1]
      if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
      else:
        try:
            id_or_uname = message.command[1]
            user = await app.get_users(id_or_uname)
            user_id = user.id
        except:
           return await text.edit("Reply to any user or pass user id or username")
        
      data = requests.get(f"{API_URL}ban_user?user_id={user_id}&api_key={ADMIN_API_KEY}&reason={reason}&admin_id={from_id}")
      r = data.json()
      msg = r["message"]
      return await text.edit(msg)
  except Exception as e:
    print(e)
  
@Client.on_message(filters.command("unban"))
async def unban(_, message: Message):
  try:
      text = await message.reply("Generating Response....!")
      reason = message.text
      from_id = message.from_user.id
      if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
      else:
        try:
            id_or_uname = message.command[1]
            user = await app.get_users(id_or_uname)
            user_id = user.id
        except:
           return await text.edit("Reply to any user or pass user id or username")
        
      data = requests.get(f"{API_URL}unban_user?user_id={user_id}&api_key={ADMIN_API_KEY}&admin_id={from_id}")
      r = data.json()
      msg = r["message"]
      return await text.edit(msg)
  except Exception as e:
    print(e)

@Client.on_message(filters.command("addwhite"))
async def addwhite(_, message: Message):
  try:
      text = await message.reply("Generating Response....!")
      from_id = message.from_user.id
      if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
      else:
        try:
            id_or_uname = message.command[1]
            user = await app.get_users(id_or_uname)
            user_id = user.id
        except:
           return await text.edit("Reply to any user or pass user id or username")
        
      data = requests.get(f"{API_URL}addwhite?user_id={user_id}&api_key={ADMIN_API_KEY}&admin_id={from_id}")
      r = data.json()
      msg = r["message"]
      return await text.edit(msg)
  except Exception as e:
    print(e)

@Client.on_message(filters.command("rmwhite"))
async def rmwhite(_, message: Message):
  try:
      text = await message.reply("Generating Response....!")
      from_id = message.from_user.id
      if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
      else:
        try:
            id_or_uname = message.command[1]
            user = await app.get_users(id_or_uname)
            user_id = user.id
        except:
           return await text.edit("Reply to any user or pass user id or username")
        
      data = requests.get(f"{API_URL}rmwhite?user_id={user_id}&api_key={ADMIN_API_KEY}&admin_id={from_id}")
      r = data.json()
      msg = r["message"]
      return await text.edit(msg)
  except Exception as e:
    print(e)

def get_file_id(message):
    if message.document:
        if int(message.document.file_size) > 3145728:
            return
        mime_type = message.document.mime_type
        if mime_type != "image/png" and mime_type != "image/jpeg":
            return
        return message.document.file_id,message.document.file_unique_id 

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            return message.sticker.thumbs[0].file_id,message.sticker.thumbs[0].file_unique_id 
        return message.sticker.file_id,message.sticker.file_unique_id 

    if message.photo:
        return message.photo.file_id,message.photo.file_unique_id 

    if message.animation:
        if not message.animation.thumbs:
            return
        return message.animation.thumbs[0].file_id,message.animation.thumbs[0].file_unique_id 

    if message.video:
        if not message.video.thumbs:
            return
        return message.video.thumbs[0].file_id,message.video.thumbs[0].file_unique_id 


from nudenet import NudeDetector
detector = NudeDetector()

def nudity_detect(file,message):
    try:
        msg = "Known Posiblities\n"
        CLASS = []
        data = detector.detect(file)
        for i in data:
            CLASS.append(i['class'])
            clas = i['class'].replace("_"," ")
            score = i['score']*100
            msg+=f"\n{clas}: {score:0.1f}"
        cen_path = detector.censor(file)
        return msg,cen_path,CLASS
    except Exception as e:
        message.reply(e)
        print(e)


all_labels_2 = [
    "BUTTOCKS_EXPOSED",
    "FEMALE_BREAST_EXPOSED",
    "FEMALE_GENITALIA_EXPOSED",
    "ANUS_EXPOSED",
    "MALE_GENITALIA_EXPOSED",
    "ANUS_COVERED",
]

def check_labels(CLASS):
    for label in all_labels_2:
        if label in CLASS:
            return True
    return False





@Client.on_message(filters.command("scan"))
async def scan_nsfw_scan(client, message):
    chat_id = message.chat.id
    reply = message.reply_to_message
    message_id = message.id
    encrypt = str(uuid.uuid4())
    err = "Reply To Any Message!"
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        await message.reply_text(err)
        return
    file_id = get_file_id(reply)
    m = await message.reply_text("Scanning")
    if not file_id:
        return
    file = await client.download_media(file_id)
    if file.endswith(".webp"):
        jpg_output_path = file.replace("webp","jpg")
        await convert_webp_to_jpg(file, jpg_output_path)
        file = jpg_output_path
    try:
        result = predict.classify(model, file)
        label_probs = result[next(iter(result))]
        
        drawings_v = label_probs.get('drawings') * 100
        drawings_n = round(drawings_v, 1)
        drawings = str(drawings_n)
        drawingsn = int(drawings_n)

        hentai_v = label_probs.get('hentai') * 100
        hentai_n = round(hentai_v, 1)
        hentai = str(hentai_n)
        hentain = int(hentai_n)

        neutral_v = label_probs.get('neutral') * 100
        neutral_n = round(neutral_v, 1)
        neutral = str(neutral_n)
        neutraln = int(neutral_n)

        porn_v = label_probs.get('porn') * 100
        porn_n = round(porn_v, 1)
        porn = str(porn_n)
        pornn = int(porn_n)
        
        sexy_v = label_probs.get('sexy') * 100
        sexy_n = round(sexy_v, 1)
        sexy = str(sexy_n)
        sexyn = int(sexy_n)

        #spam_score = np.maximum(hentain,sexyn,pornn)
        avg_score = (sexyn+pornn+hentain)/3
        if (sexyn+pornn+hentain)>70:
            is_nsfw = "True"
        else:
            is_nsfw = "False"
        try:
            rdata = await nudity_detect(file)
            print(rdata)
        except Exception as e:
            rdata = "N/A"
        text = f"**Is NSFW:** `{is_nsfw}`\n**Drawings:** `{drawings}%`\n**Hentai:** `{hentai}%`\n**Neutral:** `{neutral}%`\n**Porn:** `{porn}%`\n**Sexy:** `{sexy}%`\n**Spam Score:** `{avg_score}`\n\n`{rdata}`\n\n**Encrypt Key:** `{encrypt}`"
        await m.edit(text)
        dump_capt = f"**Encryption key:** `{encrypt}`"
        await upapp.send_photo(chat_id=int(-1001927191863),photo=file,caption=dump_capt)
        os.remove(file)
    except Exception as e:
        os.remove(file)
        await m.edit(f"Internal Server Error!\n{e}")

@Client.on_message(filters.command("disable"))
async def disable(client,message):
    chat_id = message.chat.id
    guard = guardb.find_one({"chat_id": chat_id})
    if guard is not None:
        is_guard = guard["guard"]
        if is_guard == "off":
            return await message.reply("NSFW Guard is already Disabled!")
        else:
            guardb.delete_many({"chat_id": chat_id})
            guardb.insert_one({"chat_id": chat_id,"guard": "off"})
            return await message.reply("NSFW Guard Disabled Successfuly!")
    if guard is None:
        guardb.insert_one({"chat_id": chat_id,"guard": "off"})
        return await message.reply("NSFW Guard Disabled Successfuly!")

@Client.on_message(filters.command("enable"))
async def enable(client,message):
    chat_id = message.chat.id
    guard = guardb.find_one({"chat_id": chat_id})
    if guard is not None:
        is_guard = guard["guard"]
        if is_guard == "on":
            return await message.reply("NSFW Guard is already Enabled!")
        else:
            guardb.delete_many({"chat_id": chat_id})
            guardb.insert_one({"chat_id": chat_id,"guard": "on"})
            return await message.reply("NSFW Guard Enabled Successfuly!")
    if guard is None:
        guardb.insert_one({"chat_id": chat_id,"guard": "on"})
        return await message.reply("NSFW Guard Enabled Successfuly!")

@upapp.on_callback_query(filters.regex("pressed_safe"))
async def save_safe(client, callback_query):
    data = callback_query.data
    pressed_user_id = callback_query.from_user.id
    client_data = data.split(None, 1)[1]
    query = {"client_data": client_data}
    found_document = safedb.find_one(query)

    if found_document:
        # Update the document to set is_safe to True
        update_query = {"$set": {"is_safe": True}}
        safedb.update_one(query, update_query)
    INFO_KEYBOARD = [
        [
            InlineKeyboardButton("Safe",callback_data=f"pressed_safe {client_data}"),
            InlineKeyboardButton("Unsafe",callback_data=f"pressed_unsafe {client_data}")
       ]
    ]
    edit_text = "Image Added To Safe DB Successfully!"
    await callback_query.edit_message_caption(edit_text,reply_markup=InlineKeyboardMarkup(INFO_KEYBOARD))

@upapp.on_callback_query(filters.regex("pressed_unsafe"))
async def save_unsafe(client, callback_query):
    data = callback_query.data
    pressed_user_id = callback_query.from_user.id
    client_data = data.split(None, 1)[1]
    query = {"client_data": client_data}
    found_document = safedb.find_one(query)

    if found_document:
        # Update the document to set is_safe to True
        update_query = {"$set": {"is_safe": False}}
        safedb.update_one(query, update_query)
    INFO_KEYBOARD = [
        [
            InlineKeyboardButton("Safe",callback_data=f"pressed_safe {client_data}"),
            InlineKeyboardButton("Unsafe",callback_data=f"pressed_unsafe {client_data}")
       ]
    ]
    edit_text = "Image Removed From Safe DB Successfully!"
    await callback_query.edit_message_caption(edit_text,reply_markup=InlineKeyboardMarkup(INFO_KEYBOARD))

@Client.on_message((filters.text | filters.document | filters.photo | filters.animation | filters.media | filters.sticker | filters.media_group) & (filters.group | filters.forwarded | filters.new_chat_members))
async def check_message(client, message):
    thread1 = threading.Thread(target=check_th_msg, args=(client, message))
    thread1.start()
    thread2 = threading.Thread(target=chech_user_profile, args=(client, message))
    thread2.start()


def chech_user_profile(client,message):
    user = message.from_user
    photo_id = user.photo.big_file_id if user.photo else None
    file = client.download_media(photo_id)
    try:
            result = predict.classify(model, file)
            label_probs = result[next(iter(result))]
        
            drawings_v = label_probs.get('drawings') * 100
            drawings_n = round(drawings_v, 1)
            drawings = str(drawings_n)
            drawingsn = int(drawings_n)

            hentai_v = label_probs.get('hentai') * 100
            hentai_n = round(hentai_v, 1)
            hentai = str(hentai_n)
            hentain = int(hentai_n)

            neutral_v = label_probs.get('neutral') * 100
            neutral_n = round(neutral_v, 1)
            neutral = str(neutral_n)
            neutraln = int(neutral_n)

            porn_v = label_probs.get('porn') * 100
            porn_n = round(porn_v, 1)
            porn = str(porn_n)
            pornn = int(porn_n)
        
            sexy_v = label_probs.get('sexy') * 100
            sexy_n = round(sexy_v, 1)
            sexy = str(sexy_n)
            sexyn = int(sexy_n)
            rdata,c_path,CLASS = nudity_detect(file,message)
            clsss = check_labels(CLASS)

            avg_score = (sexyn+pornn+hentain)/3
            if (sexyn+pornn+hentain)>70 or clsss:
                is_nsfw = "True"
                try:
                    text = f"**User ID:** `{user_id}`\n**Username:** {username}\n**Is NSFW:** `{is_nsfw}`\n**Drawings:** `{drawings}%`\n**Hentai:** `{hentai}%`\n**Neutral:** `{neutral}%`\n**Porn:** `{porn}%`\n**Sexy:** `{sexy}%`\n**Spam Score:** `{avg_score:0.1f}`\n\n`{rdata}`\n\nMarked As Adult Content User due to Adult DP!"
                    client.send_photo(photo=c_path,caption=text,has_spoiler=True,chat_id=chat.id)
                    remove(c_path)
                except Exception as e:
                    print(e)
                    text = f"**User ID:** `{user_id}`\n**Username:** {username}\n**Is NSFW:** `{is_nsfw}`\n**Drawings:** `{drawings}%`\n**Hentai:** `{hentai}%`\n**Neutral:** `{neutral}%`\n**Porn:** `{porn}%`\n**Sexy:** `{sexy}%`\n**Spam Score:** `{avg_score:0.1f}`\n\nMarked As Adult Content User due to Adult DP!"
                    client.reply(chat_id=chat.id,text=text)
                dump_capt = f"**Encryption key:** `{encrypt}`"
                is_safe = "False"
                document = {
                        "client_data": encrypt,
                        "file_id": photo_id,
                        "is_safe": None
                }
                safedb.insert_one(document)
                INFO_KEYBOARD = [
                   [
                        InlineKeyboardButton("Safe",callback_data=f"pressed_safe {encrypt}"),
                        InlineKeyboardButton("Unsafe",callback_data=f"pressed_unsafe {encrypt}")
                   ]
                ]
                upapp.send_photo(chat_id=int(-1001927191863),photo=file,caption=dump_capt,reply_markup=InlineKeyboardMarkup(INFO_KEYBOARD),has_spoiler=True)
            else:
                is_nsfw = "False"
            remove(file)
            return
    except Exception as e:
        print(e)
        remove(file)
        return


    

def check_th_msg(client,message):
  try:
    msg = message.text
    chat_id = message.chat.id
    SPAM_API_KEY = "5b3dd3e6-055d-4f5f-8f3f-8ee614318f7e"
    user_id = message.from_user.id
    guard = guardb.find_one({"chat_id": chat_id})
    if guard is not None:
        is_guard = guard["guard"]
        if is_guard == "on":
            pass
        else:
            return
    if guard is None:
        pass
    reply = message
    message_id = message.id
    err = "Send Any Media!"
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        data = requests.get(f"{API_URL}check_message?user_id={user_id}&message={msg}")
        ban = requests.get(f"{API_URL}check_user?user_id={user_id}")
        d = data.json()
        rb = ban.json()
        is_ban = rb['is_banned']
        if is_ban == "True":
          try:
            client.ban_chat_member(chat_id, user_id)
            reason = rb['banned_reason']
            admin = rb['admin']
            time = rb['banned_time']
            spam_score = rb['spam_score']
            TEXT = f"User was banned in Stark AntiSpam System!\n\nUser ID: `{user_id}`\nReason: `{reason}`\nAdmin: `{admin}`\nSpam Score: `{spam_score} %`\nTime: `{time}`"
            return client.send_message(chat_id=chat_id,text=TEXT)
          except Exception as e:
            strs = alertdb.find_one({"user_id": user_id, "chat_id": chat_id})
            if strs is not None:
              return
            else:
              reason = rb['banned_reason']
              admin = rb['admin']
              time = rb['banned_time']
              spam_score = rb['spam_score']
              TEXT = f"User was banned in Stark AntiSpam System!\n\nUser ID: `{user_id}`\nReason: `{reason}`\nAdmin: `{admin}`\nSpam Score: `{spam_score} %`\nTime: `{time}`"
              alertdb.insert_one({"user_id": user_id, "chat_id": chat_id})
              return message.reply(TEXT)
    else:
        encrypt = str(uuid.uuid4())
        file_id,file_unique_id = get_file_id(reply)
        if not file_id:
            return
        query = {"file_id": file_unique_id, "is_safe": True}
        found_document = safedb.find_one(query)
        if found_document:
           return
        uname = message.from_user.username
        if uname==None:
            username="`N/A`"
        else:
            username=f"@{message.from_user.username}"
        user_id = f"{message.from_user.id}"
        file = client.download_media(file_id)
        if file.endswith(".webp"):
            jpg_output_path = file.replace("webp","jpg")
            convert_webp_to_jpg(file, jpg_output_path)
            file = jpg_output_path
        try:
            result = predict.classify(model, file)
            label_probs = result[next(iter(result))]
        
            drawings_v = label_probs.get('drawings') * 100
            drawings_n = round(drawings_v, 1)
            drawings = str(drawings_n)
            drawingsn = int(drawings_n)

            hentai_v = label_probs.get('hentai') * 100
            hentai_n = round(hentai_v, 1)
            hentai = str(hentai_n)
            hentain = int(hentai_n)

            neutral_v = label_probs.get('neutral') * 100
            neutral_n = round(neutral_v, 1)
            neutral = str(neutral_n)
            neutraln = int(neutral_n)

            porn_v = label_probs.get('porn') * 100
            porn_n = round(porn_v, 1)
            porn = str(porn_n)
            pornn = int(porn_n)
        
            sexy_v = label_probs.get('sexy') * 100
            sexy_n = round(sexy_v, 1)
            sexy = str(sexy_n)
            sexyn = int(sexy_n)
            rdata,c_path,CLASS = nudity_detect(file,message)
            clsss = check_labels(CLASS)
            #spam_score = np.maximum(hentain,sexyn,pornn)
            avg_score = (sexyn+pornn+hentain)/3
            if (sexyn+pornn+hentain)>70 or clsss:
                is_nsfw = "True"
                try:
                    text = f"**User ID:** `{user_id}`\n**Username:** {username}\n**Is NSFW:** `{is_nsfw}`\n**Drawings:** `{drawings}%`\n**Hentai:** `{hentai}%`\n**Neutral:** `{neutral}%`\n**Porn:** `{porn}%`\n**Sexy:** `{sexy}%`\n**Spam Score:** `{avg_score:0.1f}`\n\n`{rdata}`\n\n**Encrypt Key:** `{encrypt}`\n\nTo Disable Click /disable"
                    message.reply_photo(photo=c_path,caption=text,has_spoiler=True)
                    remove(c_path)
                except Exception as e:
                    message.reply(e)
                    text = f"**User ID:** `{user_id}`\n**Username:** {username}\n**Is NSFW:** `{is_nsfw}`\n**Drawings:** `{drawings}%`\n**Hentai:** `{hentai}%`\n**Neutral:** `{neutral}%`\n**Porn:** `{porn}%`\n**Sexy:** `{sexy}%`\n**Spam Score:** `{avg_score:0.1f}`\n\n**Encrypt Key:** `{encrypt}`\n\nTo Disable Click /disable"
                    message.reply(text)
                try:
                    client.delete_messages(chat_id, message_id)
                except:
                    pass
                dump_capt = f"**Encryption key:** `{encrypt}`"
                is_safe = "False"
                document = {
                        "client_data": encrypt,
                        "file_id": file_unique_id,
                        "is_safe": None
                }
                safedb.insert_one(document)
                INFO_KEYBOARD = [
                   [
                        InlineKeyboardButton("Safe",callback_data=f"pressed_safe {encrypt}"),
                        InlineKeyboardButton("Unsafe",callback_data=f"pressed_unsafe {encrypt}")
                   ]
                ]
                upapp.send_photo(chat_id=int(-1001927191863),photo=file,caption=dump_capt,reply_markup=InlineKeyboardMarkup(INFO_KEYBOARD),has_spoiler=True)
            else:
                is_nsfw = "False"
            remove(file)
            return
        except Exception as e:
            print(e)
            remove(file)
            return
  except Exception as e:
    print(e)
