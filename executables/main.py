import discord
import json
import asyncio
import time 
import random
import re
from os.path import join as pathjoin

jsonf = open("waifu_settings.json")
settings = json.load(jsonf)
jsonf.close()

mudae = 432610292342587392

with open("cmds.txt","r") as f:
    mudae_roll_cmds = [line.rstrip() for line in f]

def parse_settings_message(msg):
    if msg == None:
        return None
    val_parse = re.compile(r'\*\*(\S+)\*\*').findall
    num_parse = re.compile(r'(\d+)').findall
    num_parsedec = re.compile(r'(\d*[.,]?\d+)').findall

    settings_p = re.findall(r'\w+: (.*)',msg)
    settings = dict()

    settings['prefix'] = val_parse(settings_p[0])[0]
    settings['prefix_len'] = len(settings['prefix'])
    settings['claim_reset'] = int(num_parse(settings_p[2])[0]) # in minutes
    settings['reset_min'] = int(num_parse(settings_p[3])[0])
    settings['shift'] = int(num_parse(settings_p[4])[0])
    settings['max_rolls'] = int(num_parse(settings_p[5])[0])
    settings['expiry'] = float(num_parse(settings_p[6])[0])
    settings['claim_snipe'] = [float(v) for v in num_parsedec(settings_p[15])]
    settings['kak_snipe'] = [float(v) for v in num_parsedec(settings_p[16])]
    

    settings['claim_snipe'][0] = int(settings['claim_snipe'][0])
    # pad out claim/kak snipe for default '0 second cooldown'
    if len(settings['claim_snipe']) < 2:
        settings['claim_snipe'] += [0.0]
    if len(settings['kak_snipe']) < 2:
        settings['kak_snipe'] += [0.0]
    settings['claim_snipe'][0] = int(settings['claim_snipe'][0])
    settings['kak_snipe'][0] = int(settings['kak_snipe'][0])

    settings['pending'] = None
 
    return settings

kak_finder = re.compile(r'\*\*??([0-9]+)\*\*<:kakera:469835869059153940>')

def get_snipe_time(rolled,msg):
    # Returns delay for when you are able to snipe a given roll
    r,d = settings['claim_snipe']
    if r == 0:
        # Anarchy FTW!
        return 0.0
    
    is_roller = (rolled == discord.self.user.id)
    if (r < 4 or r == 5) and is_roller:
        # Roller can insta-snipe
        return 0.0
    if r == 2 and not is_roller:
        # Not the roller.
        return d
    
    wished_for = msg.raw_mentions
    
    # Wish-based rules
    if not len(wished_for):
        # Not a WISHED character
        if r > 4:
            # Combined restriction, roller still gets first dibs
            return 0.0 if is_roller else d
        return 0.0

    if r > 2 and discord.self.user.id in wished_for:
        # Wishers can insta-snipe
        return 0.0
    
    if r == 1 and rolled not in wished_for:
        # Roller (who is not us) did not wish for char, so can insta-snipe
        return 0.0
    
    return d

def get_server_settings(guild_id,channel_id):
    try:
        with open(pathjoin('channeldata',f'{channel_id}.txt'),'r') as textsettings:
            print(f"Reading from File for channel {channel_id}")
            return textsettings.read()
    except IOError:
        print(f"File Not Found using Different Method")

def is_rolled_char(msg):
    embeds = msg.embeds

    if msg.author.id == mudae and msg.components != [] and "author" in embeds and "image" in embeds and "proxy_icon_url" not in str(embeds):
        return True
    else:
        return False

def find_roller(msg):
    rollerBuffer = None
    if msg.interaction != None and is_rolled_char(msg):
        rollerBuffer = msg.interaction.user.id
        return rollerBuffer

    
    authorId = msg.author.id
    if rollerBuffer != None and int(authorId) != mudae and msg.content.startswith(settings['prefix']):
        cmdBuffer = msg.content.strip(settings['prefix'])
        if cmdBuffer.strip(' ')[0] in mudae_roll_cmds:
            rollerBuffer = authorId
    return rollerBuffer

    

class Client(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user.id)

client = Client()
client.run(settings['authToken'])