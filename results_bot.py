import asyncio
import json
import requests
from threading import Thread
from web3 import Web3

import discord
from discord.ext import commands


CHANNEL_ID = 937226359623798858

DISCORD_BOT_TOKEN = "OTM3MjI2MDQ5MjM2OTI2NDc1.GpLLPO.4qDmASwywdI3vJ04M3grGXedR8yXCN4f6PHsr8" #"ODk3NTU4NzQ3NTU4MzE0MDQ0.YWXauQ.XAstCrblSXDAvq2xmZWcHLvprr4" #os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="nftg-", intents=intents)

CONTRACT_ADDRESS = "0xc6e7874c19a904f9A77371883736940EF2e0623d"


with open("contracts/ABI.json") as f:
    ABI = json.load(f)


async def log_loop(event_filter):

    '''
    event MatchDone (
        address winner,
        uint256 winnerTokenId,
        uint256 winnerPowerLvl,
        address loser,
        uint256 loserTokenId,
        uint256 loserPowerLvl,
        string resultType
    )
    '''
    while True:
        for MatchDone in event_filter.get_new_entries():
            event_json = Web3.toJSON(MatchDone)
            print(event_json)
            channel = bot.get_channel(int(CHANNEL_ID))
            
            event_json = json.loads(event_json)
            event_json_args = event_json["args"]
            #wallet = event_json_args["_walletListed"]


            #token_id = (str(event_json).split(",")[1]).split(": ")[-1].replace("}", "").replace(" ", "") #(str(event_json).split(",")[0]).split(": ")[-1][0:-1]
            embed_channel = discord.Embed(title="Stonk #" + str(event_json_args["winnerTokenId"]) + " Won Against Stonk #" + str(event_json_args["loserTokenId"]), color=0xe67e22, url = "https://ftmscan.com/tx/" + event_json["transactionHash"], description="Winner Wallet Address : " + event_json_args["winner"] + "\n\nWinner Power Level (after randomization) : " + str(event_json_args["winnerPowerLvl"]) +"\n\nLoser Address : " + event_json_args["loser"] + "\n\nLoser Power Level (after randomization) : " + str(event_json_args["loserPowerLvl"]) + "\n\nMatch result was based on : " + event_json_args["resultType"])
            embed_channel.set_image(url="https://thestonksociety.mypinata.cloud/ipfs/QmPsQjZCtEeLHZLd18tM7BBK7BjPuhVJwE4x96s3x41RpE/" + str(event_json_args["winnerTokenId"]) + ".png")
            await channel.send(embed=embed_channel)
            
            await asyncio.sleep(3)
            #print(event_json["args"]["totalMinted"])
            
        await asyncio.sleep(1)

def track_mint_event():
    ftm = "wss://wsapi.fantom.network/"
    #print(ABI)
    #ftm = "https://rpc.testnet.fantom.network"
    web3 = Web3(Web3.WebsocketProvider(ftm))
    contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)
    #print(contract.events.TokenMinted)
    event_filter = contract.events.MatchDone.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter)))
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(DISCORD_BOT_TOKEN))
    loop.create_task(track_mint_event())
    loop.run_forever()