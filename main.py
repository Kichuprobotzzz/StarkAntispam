from StarkGPT.main import *
import asyncio

from pyrogram import *
from pyrogram.types import *

from aiohttp import web
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "running"})

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
mongo_dbb = MongoClient(MONGO_URL)
db = mongo_dbb["STARKANTISPAMROBOT"]
tokensdb = db['TOKENS']


async def get_all_session():
    lol = [n async for n in tokensdb.find({})]
    return lol

async def add_session(client):
    tokensdb.insert_one({"token": client})

async def del_session_id(user_id):
    tokensdb.delete_many({"_id": user_id})


asdb = mongo_dbb["STRING"]
astokensdb = asdb['TOKENS']
asalivedb = asdb['ALIVE-BOTS']

async def fuck():
    wapp = web.AppRunner(await web_server())
    await wapp.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(wapp, "0.0.0.0", 7860).start()
    await app.start()
    await upapp.start()
    TOKENS = await get_all_session()
    for i in TOKENS:
        try:
            try:
                if i['is_start'] == "yes":
                    y = Client(f"{i['token']}",api_id=API_ID,api_hash=API_HASH,bot_token=f"{i['token']}", plugins={"root": "StarkGPT.modules"},workdir="./Sessions")
                    await y.start()
                else:
                    y = Client(f"{i['token']}",api_id=API_ID,api_hash=API_HASH,bot_token=f"{i['token']}", plugins={"root": "StarkGPT.plugins"},workdir="./Sessions")
                    await y.start()
            except:
                y = Client(f"{i['token']}",api_id=API_ID,api_hash=API_HASH,bot_token=f"{i['token']}", plugins={"root": "StarkGPT.modules"},workdir="./Sessions")
                await y.start()
            user = await y.get_me()
            username = user.username
            print(f"Client @{username} Started Success fully!")
        except Unauthorized as ua:
            print(f"Client Dosen't Started Reason {ua}")
            await del_session_id(f"{i['token']}")
        except FloodWait as fw:
            print(f"Client Dosen't Started Reason {fw}")
        except BaseException as e:
            print(f"Client Dosen't Started Reason {e}")
    print("[INFO]: GPT Clones Starting Success!")
    await idle()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(fuck())
