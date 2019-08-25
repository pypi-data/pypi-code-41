import asyncio
import requests

class Client:
    def __init__(self, bot, token):
        self.bot = bot
        self.bot_id=bot.user.id
        self.base="botcordapi.glitch.me/v1/"
        self.token=token
        print('init')
        

    def post_guild_count(self):
        print('valid')
        fullurl=self.base+"bot/"+self.bot_id+"/stats"
        print(fullurl)
        print(self.bot.guilds)
        print(self.bot.shards)
        #r = requests.post(fullurl, data={"token":self.token,"server_count":self.bot.guilds,"shard_count":-1})
