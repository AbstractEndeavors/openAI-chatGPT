import discord
from discord import app_commands
from src import responses
from src import log
from typing import Optional
import openai
import json
from asgiref.sync import sync_to_async
import random
logger = log.setup_logger(__name__)
config = responses.get_config()
isPrivate = False
def getRndmNum():
  return random.random()
def getRndmNumRa(i,k):
  return random.randint(i,k)
def getRndmNumLs(ls):
  return getRndmNumRa(0,len(ls))
def getContRndmLs(ls):
  return getRndmNumRa(getRndmNumLs(ls),len(ls))
def getChaosNumLs(ls):
  return ls[getContRndmLs(ls)]
def ifSingleMkRa(ls):
  ls = mkLs(ls)
  if len(ls) == 0:
    return [0,getRndmNum()]
  if len(ls) == 1:
    return [0,ls[0]]
  return ls
def rndmFloatRa(ls,exp):
  if len(ls) == 1:
    ls = ifSingleMkRa(ls)
  return float(getRndmNumRa(ls[0]*exp,ls[1]*exp))/float(10)
def changeGlob(x,v):
    globals()[x] = v
def retNums():
  return str('0,1,2,3,4,5,6,7,8,9').split(',')
def isFloat(x):
  if type(x) is float:
    return True
  return False
def isLs(x):
  if type(x) is list:
    return True
  return False
def isInt(x):
  if type(x) is int:
    return True
  return False
def isNum(x):
  if x == '':
      return False
  if isInt(x):
    return True
  if isFloat(x):
    return True
  x,nums = str(x),retNums()
  for i in range(0,len(x)):
    if x[i] not in nums:
      return False
  return True
def mkLs(ls):
  if isLs(ls) == False:
    ls = [ls]
  return ls
def mkLsLs(ls):
  lsN = []
  for i in range(0,len(ls)):
    lsN.append(mkLs(ls[i]))
  return lsN
def mkInt(i):
  if isNum(ls) == False:
    return False
  return int(i)
def mkFloat(k):
  if isNum(ls) == False:
    return False
  return float(k)
def mkIntOrFloat(k):
    if isNum(k):
        if '.' in str(k):
            return mkFloat(k)
        return mkInt(k)
    return False
def matchNumType(k,k2):
    k = mkIntOrFloat(k)
    if isFloat(k):
        return mkFloat(k2)
    if isInt(k):
        return mkInt(k2)
    return k
def sendLogInfo(x,y):
  logger.info(createDispPrompt(x,y))
def ifLenThenRetVal(x,k,st):
  if str(x) == '[]':
      return st
  if len(x)-1<=k:
    return x[k]
  return st
def lsTolsLen(ls):
  for i in range(0,len(ls)):
    n = ls[i]
    if isNum(n) == False: 
        ls[i] = len(n)
  return ls
def returnHigher(ls):
  ls.sort()
  return ls[-1]
def createDispPrompt(x,y):
  x,y = mkLsLs([x,y])
  n = '"'
  while len(x)+len(x) >0:
    if len(x) != 0:
        n = n + x[0]
        x = x[1:]
        if len(x) >1:
            x = x[1:]
        elif len(x) ==1:
            x = []
    if len(y) != 0:
        n = n + ' {'+y[0]+'}'
        if len(y) >1:
            y = y[1:]
        elif len(y) ==1:
            y = []
  return n
def getTemp(x,temp):
    if x[0] == '(':
        num = x.split('(')[1].split(')')[0]
        if isNum(num):
          temp = float(num)
          if float(temp) >float(1):
              temp = float(1)
          elif float(temp) < float(0):
              temp = float(0)
        return x[len(str(num))+2:],temp
    return x,temp
def getIntyeraction(interaction,top_p,temp,message,k):
  username,channel = str(interaction.user),str(interaction.channel)
  logger.info(f"\x1b[31m{username}\x1b[0m : '{message}' ({channel})")
  defs = defaults[comms[k]]
  if temp is not None:
     temp = float(temp/10)
     if temp > 2:
         temp = float(2)
     defs['temperature'] = temp  
  if top_p is not None:
      top_p = float(top_p/10)
      if top_p > 1:
         top_p = float(1)
      defs['top_p'] = top_p
  changeGlob('send_defs',defs)
  return message
def lsToStr(ls):
    lsN,n = [],''
    for i in range(0,len(ls)):
        n = n+' '+ls[i]
        print(ls[i])
    return n
def chopItUp(x):
    print(x)
    if isLs(x):
        x = lsToStr(x)
    lsN = []
    print(len(x))
    while len(x)>1900:
        if '\n' in x:
            lsN.append(x[:1900 - len(x[:1900].split('\n')[-1])])
            x = x[len(lsN[-1]):]
        else:
             lsN.append(x[:1900 - len(x[:1900].split('.')[-1])])
             x = x[len(lsN[-1]):]
        print(len(lsN[-1]))
    lsN.append(x)
    return lsN
async def handle_response(message,botType) -> str:
    response = await sync_to_async(openai.Completion.create)(
        model=botType,
        prompt=message,
        temperature=1,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].text
class aclient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/chat | /help")

async def send_message(message, user_message):
    await message.response.defer(ephemeral=isPrivate)
    try:
        response = '> **' + user_message + '** - <@' + \
            str(message.user.id) + '>\n\n'
        response = f"{response}{user_message}{await responses.handle_response(user_message,send_defs)}"
        lsN = chopItUp(response)
        for i in range(0,len(lsN)):
            await message.followup.send(lsN[i])
    except Exception as e:
        await message.followup.send("> **Error: Something went wrong, please try again later!**")
        logger.exception(f"Error while sending message: {e}")
async def send_start_prompt(client):
    import os
    import os.path
    config_dir = os.path.abspath(__file__ + "/../../")
    prompt_name = 'starting-prompt.txt'
    prompt_path = os.path.join(config_dir, prompt_name)
    try:
        if os.path.isfile(prompt_path) and os.path.getsize(prompt_path) > 0:
            with open(prompt_path, "r") as f:
                prompt = f.read()
                logger.info(f"Send starting prompt with size {len(prompt)}")
                message = getIntyeraction(discord.Interaction,1,0.7,prompt,1)
                
                responseMessage = await responses.handle_response(message,send_defs)
                if (config['discord_channel_id']):
                    channel = client.get_channel(int(config['discord_channel_id']))
                    await channel.send(responseMessage)
            logger.info(f"Starting prompt response:{responseMessage}")
        else:
            logger.info(f"No {prompt_name}. Skip sending starting prompt.")
    except Exception as e:
        logger.exception(f"Error while sending starting prompt: {e}")
def getC(ls,x):
    if len(ls) == 0:
        return ''
    return x
def getCls(ls,i,lsN):
    if k == 0:
        return ''
    if len(ls)-i == 1:
        return lsN[1]
    return lsN[0]
def addIt(k,i):
    k = mkIntOrFloat(k)
    if k == False:
        return False
    return k+matchNumType(k,i)
def createNumStrLs(n,ls,l):
    k = 0
    for i in range(0,len(ls)):
        if ls[i] != None:
            k = addIt(k,1)
            n = n + getCls(ls,i, [', ',' and '])+str(k)+'. '+ls[i]
    if n[-1] != ':':
        n = n + ':'
    return n
def addLines(ls):
    n = ''
    for i in range(0,len(ls)):
        n = n +getC(ls,'\n\n')+ str(ls[i])
    return n
def subFence(x):
    while ' ,' in x:
        x = x.replace(' ,',',')
    while ', ' in x:
        x = x.replace(', ',',')
    while ' ' in x[-1]:
        x = x[:-1]
    while ' ' in x[0]:
        x = x[1:]
    return '| '+x.replace(',',' | ')+' |'
def ifVarExists(var):
    try:
        var
        return True
    except NameError:
        return False
def ifFgo(x):
    if x == False:
        return True
    return False
def msgit(client,k):
    from discord.ext import commands

    client = commands.Bot(command_prefix=">",intents=discord.Intents.default())

    @client.event    
    async def on_message(message):
        for x in message.mentions:
            if(x==client.user):
                await message.channel.send(f":sauropod: did someone mention me?")

        await client.process_commands(message)        
def parseIt(client,k):
    if comms[k] == 'parse':
      @isDesc(client,k)
      async def parse(interaction: discord.Interaction, *,top_p: Optional[int],temperature: Optional[int],summarize: str,subjects:str,data:str):
        if interaction.user != client.user:
            if summarize[-1] != ':':
                summarize = summarize+':'
            print(addLines([summarize+':',subFence(subjects),data]))
            await send_message(interaction, getIntyeraction(interaction,top_p,temperature,addLines([summarize,subFence(subjects),data]),k))
def transIt(client,k):
    if comms[k] == 'trans':
      @isDesc(client,k)
      async def trans(interaction: discord.Interaction, *,top_p: Optional[int],temperature: Optional[int], text:str,target_languagea: str,target_languageb: Optional[str],target_languagec: Optional[str]):
        if interaction.user != client.user:
            await send_message(interaction, getIntyeraction(interaction,top_p,temperature,createNumStrLs('\nTranslate this into  ',[target_languagea,target_languageb,target_languagec],':\n\n'),k))
def qaIt(client,k):
    if comms[k] == 'qanda':
      @isDesc(client,k)
      async def qanda(interaction: discord.Interaction, *,top_p: Optional[int],temperature: Optional[int], question: str):
        if interaction.user != client.user:
            await send_message(interaction, getIntyeraction(interaction,top_p,temperature,"\nQ:"+question+"\n\nA: ",k))
def codeIt(client,k):
    if comms[k] == 'code':
      @isDesc(client,k)
      async def code(interaction: discord.Interaction, *,top_p: Optional[int],temperature: Optional[int], message: str):
        if interaction.user != client.user:
            await send_message(interaction, getIntyeraction(interaction,top_p,temperature,message,k))
def chatIt(client,k):
    if comms[k] == 'chat':
      @isDesc(client,k)
      async def chat(interaction: discord.Interaction, *,top_p: Optional[int],temperature: Optional[int], message: str):
          if interaction.user != client.user:
            await send_message(interaction, getIntyeraction(interaction,top_p,temperature,message,k))
          
def imgIt(client,k):
    if comms[k] == 'image':
      @isDesc(client,k)
      async def image(interaction: discord.Interaction, *,top_p: Optional[int],temperature: Optional[int], message: str):
          if interaction.user != client.user:
            await send_message(interaction, getIntyeraction(interaction,top_p,temperature,message,k))
def publicIt(client,k):
    if comms[k] == 'public':
        @isDesc(client,k)
        async def public(interaction: discord.Interaction):
            global isPrivate
            await interaction.response.defer(ephemeral=False)
            if isPrivate:
                isPrivate = not isPrivate
                await interaction.followup.send("> **Info: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
                logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
            else:
                await interaction.followup.send("> **Warn: You already on public mode. If you want to switch to private mode, use `/private`**")
                logger.info("You already on public mode!")
def privateIt(client,k):
    if comms[k] == 'private':
        @isDesc(client,k)
        async def private(interaction: discord.Interaction):
            global isPrivate
            await interaction.response.defer(ephemeral=False)
            if not isPrivate:
                isPrivate = not isPrivate
                logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
                await interaction.followup.send("> **Info: Next, the response will be sent via private message. If you want to switch back to public mode, use `/public`**")
            else:
                logger.info("You already on private mode!")
                await interaction.followup.send("> **Warn: You already on private mode. If you want to switch to public mode, use `/public`**")
def helpIt(client,k):
    if comms[k] == 'help':
        @isDesc(client,k)
        async def help(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(":star:**BASIC COMMANDS** \n    `/image [description]` get image from a description \n `/code [message]` Chat with ChatGPT!\n `/chat [message]` Chat with ChatGPT!\n   `/private` ChatGPT switch to private mode \n `/public` ChatGPT switch to public mode \n,\n `/public`Show help for the bot")
            logger.info("\x1b[31mSomeone need help!\x1b[0m")
def isDesc(client,k):
  return client.tree.command(name= comms[k], description=descs[comms[k]])
def asit(client,k):
      codeIt(client,k)
      chatIt(client,k)
      imgIt(client,k)
      privateIt(client,k)
      publicIt(client,k)
      helpIt(client,k)
      qaIt(client,k)
      transIt(client,k)
      parseIt(client,k)
      msgit(client,k)
def run_discord_bot():
    client = aclient()
    @client.event
    async def on_ready():
        await send_start_prompt(client)
        await client.tree.sync()
        logger.info(f'{client.user} is now running!')
    @client.event
    async def on_message(message):
            print(discord.Interaction)
            if client.user.mentioned_in(message):
                response = '> **' + message.content + '** - <@' + \
                str(message.author) + '>\n\n'
                response = f"{response}{message.content}{await responses.handle_response(message.content,defaults['random'])}"
                response = await responses.handle_response(message.content,defaults['random'])
                lsN = chopItUp(response)
                for i in range(0,len(lsN)):
                    print(lsN[i])
                    await message.channel.send(lsN[i])#message.channel.send(lsN[i])
    for i in range(0,len(comms)):
      asit(client,i)
    TOKEN = config['discord_bot_token']
    client.run(TOKEN)
global optimizations,comms,descs,send_defs
optimizations = {'configs':['temperatures', 'lengths', 'top_p', 'frequency', 'presence_penalty', 'best_of', 'models'],
                 'commandNames':['code','chat','image','public','private','help','qanda','trans','parse','mention','random'],
                'settings':{'size':['256x256','512x512','1024x1024'],'n':[1,10],'temperature':[0,1],'max_tokens':[1,2048],'top_p':[0,1],'frequency':[0,2],'presence_penalty':[-2,2],'best_of':[0,1],'frequency_penalty':[-2,2]},'models':{'code':['code-cushman-001','code-davinci-002'],'chat':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001'],'edit':['text-davinci-edit-001']}
                'defaults':{
                'random':{'type':'random','model':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001'][getRndmNumRa(0,3)],'temperature':rndmFloatRa([0,1],10),'max_tokens':2000,'top_p':rndmFloatRa([0,1],10),'frequency':rndmFloatRa([0,2],10),'presence_penalty':rndmFloatRa([0,2],10),'best_of':rndmFloatRa([0,1],10),'frequency':rndmFloatRa([0,20],10)},
                'image':{'type':'image','size':'1024x1024','temperature':0.7,'n':1,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':2048},
                'code':{'type':'code','model':'code-cushman-001','temperature':0.7,'best_of':1,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':2000},
                'chat':{'type':'chat','model':'text-davinci-003','temperature':0.7,'best_of':1,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':2048},
                'mention':{'mention':'chat','model':'text-davinci-003','temperature':0.7,'best_of':1,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':2048},
                'qanda':{'type':'qanda','model':'text-davinci-003','temperature':0,'best_of':1,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':100},
                'parse':{'type':'parse','model':'text-davinci-003','temperature':0,'best_of':0,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':100},
                'trans':{'type':'trans','model':'text-davinci-003','temperature':0.7,'best_of':1,'top_p':1,'frequency_penalty':0,'presence_penalty':0,'max_tokens':2048}
                },
                'descriptions':{'random':'randomized interaction','mention':'mentions the bot','code':"Write Some Code",'chat':"Have a chat with ChatGPT",'image':"get image from a description",'public':"Toggle public access",'private':"Toggle private access",'help':"Show help for the bot",'temp':'Temperature will allow you to pick the randomness of your interaction; range(0:2) - input(integer) i.e. 15 will transate to 1.5','qanda':'questions and answers','trans':'translate one language to another','parse':'[summerize] -" a table summarizing fruits from Goocrux";[subjects] -"Fruit,Color,Flavor"'}}
defaults,comms,descs,send_defs = optimizations['defaults'],optimizations['commandNames'],optimizations['descriptions'],'chat'
