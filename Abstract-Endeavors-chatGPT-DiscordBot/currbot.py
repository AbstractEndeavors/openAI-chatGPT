import discord
from discord import app_commands
from typing import Optional
from disnake.ext import commands
import openai
import json
import log
import sys
from asgiref.sync import sync_to_async
import random
from discord.ext import commands
from dislash import InteractionClient, SelectMenu, SelectOption
import os
import os.path
def mkDir(x):
    pa = clearHomePa(x)
    if isDir(pa) == False:
        os.mkdir(pa)
    return x
def cleanLs(ls,lsN):
    for i in range(0,len(lsN)):
        if lsN[i] in ls:
            ls.remove(lsN[i])
    return ls
def cleanSplit(x,y,ls):
    if y in str(x):
        x = cleanLs(str(x).split(str(y)),ls)
    return x
def findItI(x,y):
    for i in range(0,len(x)):
        if x[i] == y:
            return i
    return False
def combLs(ls,lsN):
    for i in range(0,len(lsN)):
        ls.append(lsN[i])
    return ls
def clearHomePa(x):
    z,y = mkLs(cleanSplit(x,'/',[''])),mkLs(cleanSplit(home,'/',['']))
    if y[-1] in z:
        k = findItI(y[-1],z)
        x = z[k+1:]
    return crPa(combLs(mkLs(home),z))
def isDir(x):
    return os.path.exists(x)
def isFile(x):
    return os.path.isfile(x)
def crPa(ls):
    ls = mkLs(ls)
    y = ls[0]
    for i in range(1,len(ls)):
        y = os.path.join(y, ls[i])
    return y
def changeGlob(x,v):
    globals()[x] = v
def tryItN():
   try:
        n +=1
   except:
        n = 0
        return False
def makeQuote(x):
  for i in range(0,2):
    x = whileIn(x,0-i,['"',"'"])
  return '"'+x+'"'
def whileIn(x,n,ls):
  if n == -1:
    while x[n] in ls:
      x = x[:-1]
  elif n == 0:
    while x[n] in ls:
      x = x[1:]
  return x
def numLs():
  return str('0,1,2,3,4,5,6,7,8,9,0').split(',')
def isNum(x):
  if isInt(x):
    return True
  if isFloat(x):
    return True
  if isStr(x) == False:
    x = str(x)
  num,cou = numLs(),0
  for i in range(0,len(x)):
    if x[i] not in num:
      if x[i] != '.':
        return False
      elif x[i] == '.' and cou >0:
        return False
      elif x[i] == '.' and cou ==0:
        cou +=1
  return True
def isLs(ls):
    if type(ls) is list:
        return True
    return False
def isStr(x):
  if type(x) is str:
    return True
  return False  
def isInt(x):
  if type(x) is int:
    return True
  return False
def isFloat(x):
  if type(x) is float:
    return True
  return False
def isBool(x):
    if type(x) is bool:
        return True
    return False
def mkFloat(x):
  if isFloat(x):
    return x
  if isInt(x):
    return float(str(x))
  if isNum(x):
    return float(str(x))
  z = ''
  for i in range(0,len(x)):
    if isNum(x[i]):
      z = z + str(x[i])
  if len(z) >0:
    return float(str(z))
  return float(str(1))
def isOutInRange(js,key):
  x = js[key]
  param = parameters[key]
  obj = param['object']
  if x is None and param['default'] == 'null':
      return 'null'
  if obj == 'int':
    if isInt(x) == False:
      if isNum(x):
        x = int(x)
    if x is None:
      return int(param['default'])
    scale = param['scale']
    if scale =='range':
      print(param['range'])
      y = json.loads(str(param['range']).replace(' ','').replace('{','["').replace('}','"]').replace(':','","'))
      if int(x) < int(y[0]) and int(x)>int(y[1]):
        return x
      if x> int(y[1]):
        x = int(y[1])
      if x < int(y[0]):
        x = int(y[0])
    return int(x)
  elif obj == 'float':
    if isFloat(x) == False:
      if isNum(x):
        x = float(str(x))
    
    if x is None:
      return float(param['default'])
    x = mkFloat(x)
    scale = param['scale']
    if scale =='range':
      print(param['range'])
      y = json.loads(str(param['range']).replace(' ','').replace('{','["').replace('}','"]').replace(':','","'))
      if x < float(y[0]) and x>float(y[1]):
        return x
      if x> float(y[1]):
        x = float(y[1])
      if x < float(y[0]):
        x = float(y[0])
        return float(x)
  elif obj == 'bool':
      if x is None:
          x = param['default']
      return mkBool(x)
  else:
      if x is None:
          x = param['default']
      return makeQuote(x)
def getSpecDef(na,spec):
    if na in parameters:
        defs = grabDefVars(na)
        input(grabDefVars(na))
        if spec in defs:
            return defs[spec]
    return False
def mkBool(x):
    if isBool(x):
        return x
    boolJS = {'0':'True','1':'False','true':'True','false':'False'}
    if str(x) in boolJS:
        return bool(str(boolJs[str(x)]))
    return None
def mkStr(x):
    if isStr(x):
        return x
    return str(x)
def getObjObj(obj,x):
    if obj in ['str','file','image','mask','input','prompt']:
        return 'str('+mkStr(x)+')'
    if obj == 'bool':
        return 'bool('+mkBool(x)+')'
    if obj == 'float':
        return 'float('+mkFloat(x)+')'
    if obj == 'map':
        return 'map('+map(x)+')'
    return x
def getScaleDefs(st):
    scaleLs = [getSpecDef(st,'scale'),getSpecDef(st,'object')]
    y = getSpecDef(st,scaleLs[0])
    if isLs(y):
        ls = y
    elif scaleLs[0] =='range':
      y = json.loads(str(getSpecDef(st,scaleLs[0])).replace(' ','').replace('{','["').replace('}','"]').replace(':','","'))
      ls = getObjObj(scaleLs[1],y[0]),getObjObj(scaleLs[1],y[1])
    return [scaleLs,ls]
def getScaleFun(st):
    scaleLs,ls = getScaleDefs(st)
    if scaleLs[0] == 'range':
        return minMax(st,ls[0],ls[1])
    if scaleLs[0] == 'choice':
        return 
    if scaleLs[0] == 'inherit':
        return ls[0]
    return False
def reader(file):
    with open(file, 'r') as f:
        text = f.read()
        return text
def getKeys(js):
  lsN = []
  try:
    for key in js.keys():
      lsN.append(key)
    return lsN
  except:
    return lsN
def createPrompt(type,js):
    params = ''
    keys = getKeys(js)
    for i in range(0,len(keys)):
        key = keys[i]
        if js[key] is None:
            js[key] = parameters[key]['default']
            js[key] = isOutInRange(js,key)
        if str(key).lower() in ['file','image','mask']:
            params = params + key+'='+'open('+str(js[key])+',"rb"),'
        else:
            params = params + key+'='+str(js[key])+','
    return getEndPoint(typ,js)
def pen(x,p):
    with open(p, 'w',encoding='UTF-8') as f:
        return f.write(str(x))
def getC(i):
  if i == 0:
    return ''
  return ','
changeGlob('home',os.getcwd())
##---------------------------------------------------------------------------------------------------------------------------createLog
changeGlob('logger',log.setup_logger(__name__))
##---------------------------------------------------------------------------------------------------------------------------makeBotPublic
changeGlob('isPrivate',False)
##----------------------------------------------------------------------------------------------------------------------------@ConnectBot
class aclient(discord.Client):
    def __init__(self) -> None:
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.Activity(type=discord.ActivityType.watching, name="/chat | /help")
#-----------------------------------------------------------------------------------------------------------------------------accessBotConfigFile
def getConfig():
    with open('config.json', 'r') as f:
        changeGlob('config',json.load(f))
#-----------------------------------------------------------------------------------------------------------------------------connectOpenAi.env
def ConnectOpenAiAccount():
    config = getConfig()
    openai.api_key = config['openAI_key']
#-----------------------------------------------------------------------------------------------------------------------------logMessageInfo
def getInfo(x):
    changeGlob('channel',str(discord.Interaction.user))
    changeGlob('username',str(discord.Interaction.channel))
    logger.info(f"\x1b[31m{username}\x1b[0m : '{x}' ({channel})")
def isUntend(msg):
    if authId(msg) not in unTend:
        unTend[authId(msg)]
    unTend[authId(msg)].append(magId(msg))
def answer(msg):
    unTend[authId(msg)].remove(msgId(msg))
def logFrom(msg):
    logger.info(f"[Auth{getAth(msg)},authId{getAthId(msg)},msgId{getId(msg)},Auth{getAthNme(msg)},Cont{getCnt(msg)}\x1b[0m : '{x}' ({channel})")
    isUntend(msg)
#-------------------------------------------------------------------------------------------get message IDs
def getAth(msg):
    return msg.author
def getMsgChn(msg):
    return msg.channel
def getCnt(msg):
    return msg.content
def getAthNme(msg):
    return getAth(msg).name
def getId(x):
    return x.id
def getAthId(msg):
    return getId(getAth(msg))
#-------------------------------------------------------------------------------------------isIt the bot?
def isClient(msg,client):
    if getId(getAth(msg)) == client.user.id:
        return True
    return False
#-------------------------------------------------------------------------------------------makeTextAString
def mkStr(x):
    return str(x)
#-------------------------------------------------------------------------------------------IndentYourMessageand@yourRecipient
def indent(msg):
    x = mkStr(getAthId(msg))
    return ('> **' + getCnt(msg) + '** - <@' + \
            x + '>\n\n')
#-------------------------------------------------------------------------------------------@therecipient
def AtThem(msg):
    return ('<@' + \
            mkStr(getAthId(msg)) + '>\n\n')
def AtThem(user,msg):
    return ('<@' +str(user)+ '>\n\n'+msg)
#-------------------------------------------------------------------------------------------indentYourMessage
def indentIt(x):
    return '> **' + x 
#-------------------------------------------------------------------------------------------initiateBotClient
def ready():
    @client.event
    async def on_ready():
        await send_start_prompt()
        await client.tree.sync()
        logger.info(f'{client.user} is now running!')
        return
#-------------------------------------------------------------------------------------------handleClientMessages

#-------------------------------------------------------------------------------------------runYourBot

#-------------------------------------------------------------------------------------------startBotOncePerRun
def helpStr():
    return ':star:**BASIC COMMANDS**   \n\n(optional input) top_p -  the model considers the results of the tokens with top_p probability mass; range(-2.0:2.0); input(integer) i.e. 15 will transate to 1.5; So 0.1 means only the tokens comprising the top 10% probability mass are considered; default: 0.0  \n\n(optional input) max_tokens - The maximum number of tokens to generate in the completion. range(0:2048); default: 100 - 2048. \n\n(optional input) n - How many edits to generate for the input and instruction. range(0,10); default 1. \n\n(optional input) size - The size of the generated images. Must be one of 256x256, 512x512, or 1024x1024. default: 1024x1024. \n\n(imageFiles) =- The image to edit. Must be a valid PNG file, less than 4MB, and square. If mask is not provided, image must have transparency, which will be used as the mask.\n\n response_format -  \n\n maskImage - imgedit: [file] 1st image, [filetwo] upload 2nd image, [prompt] write a prompt explaining your intent. \n\nimgvariation [file] upload the image youd like to have changed. \n\nrandom [prompt] input text for randomized response. \n\nmention [@] mentions the bot and returns randomized response. \n\ncode [prompt] input your desired outcome, [code] input your code. \n\nchat [message] input your message and Have a chat with ChatGPT. \n\nimage [prompt] input text and get an  image from a description \n\npublic Toggle public access. \n\nprivate Toggle private access  \n\nhelp Show help for the bot \n\nqanda questions and answers. \n\ntrans translate one language to another \n\nparse [summerize] -" a table summarizing fruits from Goocrux";[subjects] -"Fruit,Color,Flavor".'
def openIt(x):
    if x != '':
        return open(str(x),'rb')
    return x
def lsToStr(ls):
    lsN,n = [],''
    for i in range(0,len(ls)):
        n = n+' '+ls[i]
        print(ls[i])
    return n
def chopItUp(x):
    if isLs(x):
        x = lsToStr(x)
    lsN = []
    while len(x)>1900:
        if '\n' in x:
            lsN.append(x[:1900 - len(x[:1900].split('\n')[-1])])
            x = x[len(lsN[-1]):]
        else:
             lsN.append(x[:1900 - len(x[:1900].split('.')[-1])])
             x = x[len(lsN[-1]):]
    lsN.append(x)
    return lsN
def openImage(x):
    import requests
    response = requests.get(str(x))
    name = str(x).split('/')[-1]
    if response.status_code:
        fp = open(name,'wb')
        fp.write(response.content)
        fp.close()
    return open(name,'rb')
def ConOpenAi():
    return config['openAI_key']
def getDefs(js):
    keys = getKeys(js)
    for i in range(0,len(keys)):
        key = keys[i]
        if js[key] is None:
            js[key] = parameters[key]['default']
    return js
def getSpecIntLs(k):
    ls = []
    for i in range(0,k):
        ls.append(i+1)
    return ls
def getSpecNumLs(k):
    ls = []
    for i in range(0,k):
        ls.append(str(i+1))
    return ls
def exists(x):
    if isFile(x):
        return True
    return False
def existJsRead(x,y):
    pa = clearHomePa(x)
    if exists(pa) == False:
        pen(y,pa)
    return json.loads(reader(pa))
def existRead(x,y):
    print(y)
    pa = clearHomePa(x)
    if exists(pa) == False:
        pen(str(y),pa)
    return reader(pa)

def addJs(js,st,x):
    js[st] = x
    return js
async def getEndPoint(interaction,typ,js,spec):
    openai.api_key = ConOpenAi()
    start_sequence = specifications[spec]['delims'][0]
    restart_sequence = specifications[spec]['delims'][1]
    if 'model' in js:
        if js['model'] is None and 'model' in specifications[spec]:
            js['model'] = specifications[spec]['model']['default']
    
    try:
        if typ == 'Completion':
            sp = ['choices',int(js["n"])-1,'text']
            response = await sync_to_async(openai.Completion.create)(model=str(js["model"]),prompt = str(js["prompt"]),user = str(js["user"]),stream = mkBool(False),n =int(js["n"]),max_tokens =int(js["max_tokens"]),temperature = float(js["temperature"]),best_of =int(js["best_of"]),top_p =float(js["top_p"]),frequency_penalty =float(js["frequency_penalty"]),presence_penalty = int(js["presence_penalty"]),stop = str(js["stop"]),echo = bool(js["echo"]))
        elif typ == 'image_create':
            sp = ['data',0,js['response_format']]
            response = await sync_to_async(openai.Image.create)(prompt = str(js["prompt"]),user=str(js["user"]),size=str(js["size"]),n=int(js["n"]))
        elif typ == 'image_edit':
            sp = ['data',0,js['response_format']]
            response = await sync_to_async(openai.Image.create_edit)(image=openImage(js['image']),mask=openImage(js['mask']),prompt=str(js["prompt"]),user=str(js["user"]),size=str(js["size"]),n=int(js["n"]))
        elif typ == 'image_variation':
            sp = ['data',0,js['response_format']]
            response = await sync_to_async(openai.Image.create_variation)(image =openImage(js["image"]),user=str(js["user"]),size=str(js["size"]),n=int(js["n"]))
        elif typ == 'embedding':
            sp = ['data',0,'embedding']
            response = await sync_to_async(openai.Embedding.create)(model="text-embedding-ada-002",input =str(js["input"]),user = str(js["user"]))
        elif typ == 'moderation':
            sp = ['choices',int(js["n"])-1,'text']
            response = await sync_to_async(openai.Moderation.create)(input=str(js['input']))
        elif typ == 'edit':
            sp = ['choices',0,'text']
            response = await sync_to_async(openai.Edit.create)(model="text-davinci-edit-001",input=str(js['input']),instruction=str(js['instruction']))
        resp = response
        resp['Oginput'] = js
        hist = mkDir(crPa([mkDir('history'),typ]))
        pen(resp,crPa([hist,str(response["created"])+'.json']))
        return response[sp[0]][sp[1]][sp[2]]
    except openai.error.APIError as e:
      #Handle API error here, e.g. retry or log
      await interaction.followup.send("> **Error: Something went wrong, please try again later!**")
      logger.exception(f"OpenAI API returned an API Error: {e}")
      print(f"OpenAI API returned an API Error: {e}")
      pass
    except openai.error.APIConnectionError as e:
      #Handle connection error here
      await interaction.followup.send("> **Error: Something went wrong, please try again later!**")
      logger.exception(f"Failed to connect to OpenAI API: {e}")
      print(f"Failed to connect to OpenAI API: {e}")
      pass
    except openai.error.RateLimitError as e:
      #Handle rate limit error (we recommend using exponential backoff)
      await interaction.followup.send("> **Error: Something went wrong, please try again later!**")
      logger.exception(f"OpenAI API request exceeded rate limit: {e}")
      print(f"OpenAI API request exceeded rate limit: {e}")
      pass
            
def getInfo(interaction):
    logger.info(f"\x1b[31m{username}\x1b[0m : '{interaction}' ({channel})")
    return
def mkLs(ls):
    if isLs(ls):
        return ls
    return [ls]
def addLsToStr(ls):
    st,ls = '',mkLs(ls)
    for i in range(0,len(ls)):
        end = ','
        if i == len(ls)-1 and len(ls) != 1:
            end = ' and '
        elif len(ls) == 1:
            end = ' '
        st = st +end+ str(ls[i])
    return st
def addColDrop(x):
    return x + ':\n'
def putQu(x):
    if x[-1] != '?':
        x = x + '?'
    return x
def autoQ(x,ls):
    x = ls[0]+x
    x = putQu(x)
    x = x + ls[1]
    return x
def roundIt(k):
    if '.' in str(k):
        rou = str(k).split('.')[1]
        if int(rou[0]) >=5:
            return int(str(k).split('.')[0])+1
        return int(str(k).split('.')[0])
    return k
def tokenPerc(inp,var):
    if var == None:
        return roundIt(float(len(inp))*float(1.1))
    return var
def atIt(message):
    response = ' ** - <@' + \
            str(message.user.id) + '>\n\n'
    return response
def qandaIt(client,spec):
    if spec == "qanda":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        @boolIt('echo')
        @boolIt('stream')
        async def qanda(interaction: discord.Interaction,model: Optional[str],prompt: str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            prompt = autoQ(prompt,specifications[spec]['delims'])
            js = {"model":model,"prompt":str(prompt),"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def transIt(client,spec):
    if spec == "translate":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        @boolIt('echo')
        @boolIt('stream')
        async def translate(interaction: discord.Interaction,model: Optional[str],languages:str,prompt: str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            prompt = 'translate this into '+addColDrop(str(addLsToStr(languages.split(','))))+prompt                      
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def writecodeIt(client,spec):
    if spec == "writecode":
        @isDesc(client,spec)
        @mulChoices(['Python','Java','C++','JavaScript','Go','Julia','R','MATLAB','Swift','Prolog','Lisp','Haskell','Erlang','Scala','Clojure','F#','OCaml','Kotlin','Dart'],'language')
        @mulModel(specifications[spec]['models']['choices'])
        async def writecode(interaction: discord.Interaction,model: Optional[str],prompt: str,language:str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            prompt = 'write a code with the following specifications in '+language+':\n'+prompt
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec) 
def editcodeIt(client,spec):
    if spec == "editcode":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def editcode(interaction: discord.Interaction,model: Optional[str],instructions: str,code:str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            prompt = instructions+'\n'+code
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":tokenPerc(code,max_tokens),"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
            
def debugcodeIt(client,spec):
    if spec == "debugcode":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def debugcode(interaction: discord.Interaction,model: Optional[str],specifications: str,code:str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            prompt = 'with a focus on:\n'+str(specifications)+'\ndebug the following code:\n'+code
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def convertcodeIt(client,spec):
    if spec == "convertcode":
        @isDesc(client,spec)
        @mulChoices(['Python','Java','C++','JavaScript','Go','Julia','R','MATLAB','Swift','Prolog','Lisp','Haskell','Erlang','Scala','Clojure','F#','OCaml','Kotlin','Dart'],'language')
        @mulModel(specifications[spec]['models']['choices'])
        async def convertcode(interaction: discord.Interaction,code:str,language:app_commands.Choice[str],model: Optional[str],prompt: str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            prompt = 'convert the following code to '+str(language)+':\n'+str(code)+'\n'
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def chatIt(client,spec):
    if spec == 'chat':
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        @boolIt('echo')
        @boolIt('stream')
        async def chat(interaction: discord.Interaction,model: Optional[str],prompt: str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def publicIt(client,spec):
    if spec == 'public':
        @isDesc(client,spec)
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
            return await makeItHappen(interaction,client)
def privateIt(client,spec):
    if spec == 'private':
        @isDesc(client,spec)
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
            return await makeItHappen(interaction,client)
def helpIt(client,spec):
    if spec == 'help':
        @isDesc(client,spec)
        async def help(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=isPrivate)
            lsN = chopItUp(":star:**BASIC COMMANDS** \n "+str(helpAll()))
            for i in range(0,len(lsN)):
                await interaction.channel.send(lsN[i])
def parseIt(client,spec):
    if spec == "parse":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        @boolIt('echo')
        @boolIt('stream')
        async def parse(interaction: discord.Interaction,model: Optional[str],prompt: str,summarize:str,subjects:str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def randomIt(client,spec):
    if spec == "random":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        @boolIt('echo')
        @boolIt('stream')
        async def random(interaction: discord.Interaction,model: Optional[str],prompt: str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def mentionIt(client,spec):
    if spec == "mention":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        @boolIt('echo')
        @boolIt('stream')
        async def mention(interaction: discord.Interaction,model: Optional[str],prompt: str,user: Optional[str],stream: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],suffix: Optional[str],max_tokens: Optional[app_commands.Range[int,1,2048]],maplow: Optional[int],temperature: Optional[app_commands.Range[float,-2.0,2.0]],best_of: Optional[app_commands.Range[int,1,10]],top_p: Optional[app_commands.Range[float,0.0,1.0]],frequency_penalty: Optional[app_commands.Range[float,-2.0,2.0]],presence_penalty: Optional[app_commands.Range[float,-2.0,2.0]],log_probs: Optional[int],stop: Optional[str],echo: Optional[app_commands.Choice[str]],):
            js = {"model":model,"prompt":prompt,"user":user,"stream":stream,"n":n,"suffix":suffix,"max_tokens":max_tokens,"temperature":temperature,"best_of":best_of,"top_p":top_p,"frequency_penalty":frequency_penalty,"presence_penalty":presence_penalty,"log_probs":log_probs,"stop":stop,"echo":echo}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)            
def image_createIt(client,spec):
    if spec == "image_create":
        @isDesc(client,spec)
        @imageSize()
        @mulChoices(['url','b64_json'],'response_format')
        async def image_create(interaction: discord.Interaction,prompt: str,user: Optional[str],size: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],response_format: Optional[app_commands.Choice[str]],):
            js = {"prompt":prompt,"user":user,"size":size,"n":n,"response_format":response_format}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)         
def image_editIt(client,spec):
    if spec == "image_edit":
        @isDesc(client,spec)
        @imageSize()
        @mulChoices(['url','b64_json'],'response_format')
        async def image_edit(interaction: discord.Interaction,image: discord.Attachment,prompt: str,mask:discord.Attachment,user: Optional[str],size: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],response_format: Optional[app_commands.Choice[str]],):
            js = {"image":str(image),"prompt":prompt,"mask":mask,"user":user,"size":size,"n":n,"response_format":response_format}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def image_variationIt(client,spec):
    if spec == "image_variation":
        @isDesc(client,spec)
        @imageSize()
        @mulChoices(['url','b64_json'],'response_format')
        async def image_variation(interaction: discord.Interaction,image: discord.Attachment,prompt:str,mask: Optional[discord.Attachment],user: Optional[str],size: Optional[app_commands.Choice[str]],n: Optional[app_commands.Range[int,1,10]],response_format: Optional[app_commands.Choice[str]],):
            js = {"image":image,"mask":mask,"user":user,"prompt":prompt,"size":size,"n":n,"response_format":response_format}
            return await send_message(interaction,prompt,js,specifications[spec]['type'],spec)
def text_search_docIt(client,spec):
    if spec == "text_search_doc":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def text_search_doc(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def similarityIt(client,spec):
    if spec == "similarity":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def similarity(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def text_similarityIt(client,spec):
    if spec == "text_similarity":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def text_similarity(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def text_search_queryIt(client,spec):
    if spec == "text_search_query":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def text_search_query(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def text_embeddingIt(client,spec):
    if spec == "text_embedding":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def text_embedding(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def text_insertIt(client,spec):
    if spec == "text_insert":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def text_insert(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def text_editIt(client,spec):
    if spec == "text_edit":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def text_edit(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def search_documentIt(client,spec):
    if spec == "search_document":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def search_document(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def search_queryIt(client,spec):
    if spec == "search_query":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def search_query(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
def instructIt(client,spec):
    if spec == "instruct":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def instruct(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec) 
def code_editIt(client,spec):
    if spec == "code_edit":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def code_edit(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
            
def code_search_codeIt(client,spec):
    if spec == "code_search_code":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def code_search_code(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
            
def code_search_textIt(client,spec):
    if spec == "code_search_text":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def code_search_text(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user,}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
            
def moderationIt(client,spec):
    if spec == "moderation":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def code_search_text(interaction: discord.Interaction,model: Optional[str],input: str,user: Optional[str],):
            js = {"model":model,"input":input,"user":user}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
            
def editIt(client,spec):
    if spec == "edit":
        @isDesc(client,spec)
        @mulModel(specifications[spec]['models']['choices'])
        async def edit(interaction: discord.Interaction,model: Optional[str],input:str,instruction:str,user:Optional[str]):
            input = addColDrop(instruction)+addColDrop('edit the following text in regard to the instructions listed above')+input
            js = {"model":model,"input":input,"user":user,"instruction":instruction}
            return await send_message(interaction,input,js,specifications[spec]['type'],spec)
async def send_start_prompt():
    @client.event
    async def on_message(msg):
        if isClient(msg,client) == False:
            if client.user.mentioned_in(msg):
                response = indent(msg)
            await msg.channel.send(indentIt(mkStr(getCnt(msg))))
def isMessage():
    @client.event
    async def on_message(msg):
        if isClient(msg,client) == False:
            async def chat(interaction: discord.Interaction, *,top_p: Optional[app_commands.Range[float,0.0,1.0]],temperature: Optional[app_commands.Range[float,-2.0,2.0]], message: str):
              if interaction.user != client.user:
                js = {"top_p":top_p,"temperature":temperature,"message":message}
                return await send_message(interaction,message,js,'Completion','chat')
async def on_message(message):
    if 'happy birthday' in message.content.lower():
        await message.channel.send('Happy Birthday! 🎈🎉')
                
            
def clearDelims(x,typ):
    ls = specifications[typ]['delims']
    for i in range(0,len(ls)):
        found,z = False,''
        for k in range(0,len(x)):
            z = z + x[k]
            if z[-len(ls[i]):] == ls[i] and found == False:
                z = z[:-len(ls[i])]
                found = True
        x = z
    return z
global optimizations,comms,descs,send_defs
def getDefs(js):
    keys = getKeys(js)
    for i in range(0,len(keys)):
        key = keys[i]
        if js[key] == None:
            js[key] = parameters[key]['default']
    return js
async def send_message(interaction,user_message,js,type,spec):
    await interaction.response.defer(ephemeral=isPrivate)
    try:
        inp,space,target,response = str(user_message),' ',mkStr(atIt(interaction)),mkStr(await getEndPoint(interaction,type,getDefs(js),spec))
        if type in ['Completion','moderation','edit','embedding']:
            response = response[len(str(user_message)):]
        logger.info(f"{target}{inp}{response}")
        lsN = mkLs(chopItUp(response))
        print(response)
        await interaction.followup.send(indentIt(clearDelims(inp,spec)+space+target))
        for i in range(0,len(lsN)):
            input(lsN)
            await interaction.channel.send(lsN[i])
    except Exception as e:
        await interaction.followup.send("> **Error: Something went wrong, please try again later!**")
        logger.exception(f"Error while sending message: {e}")
def isDesc(client,spec):
  changeGlob('found',True)
  return client.tree.command(name= spec, description=descriptions[spec])

def mulModel(ls):
    n = 'app_commands.choices(model=['
    for i in range(0,len(ls)):
      n = n + getC(i)+'app_commands.Choice(name="'+ls[i]+'", value="'+ls[i]+'")'
    n = n + '])'
    pen('from discord import app_commands\nfrom discord.ext import commands\nfrom dislash import InteractionClient, SelectMenu, SelectOption\ndef getMuls():\n\treturn '+n,'getEm.py')
    import importlib
    import getEm
    importlib.reload(getEm) 
    return getEm.getMuls()
def mulChoices(ls,na):
    if 'getChoice' in sys.modules:  
        del sys.modules["getChoice"]
    n = 'app_commands.choices('+str(na)+'=['
    for i in range(0,len(ls)):
      n = n + getC(i)+'app_commands.Choice(name="'+ls[i]+'", value="'+ls[i]+'")'
    n = n + '])'
    pen('from discord import app_commands\nfrom discord.ext import commands\nfrom dislash import InteractionClient, SelectMenu, SelectOption\ndef getChoi():\n\treturn '+n,'getChoice.py')
    import importlib
    import getChoice
    importlib.reload(getChoice)
    return getChoice.getChoi()
def boolIt(na):
    ls = ['True','False']
    if 'getChoice' in sys.modules:  
        del sys.modules["getChoice"]
    n = 'app_commands.choices('+str(na)+'=['
    for i in range(0,len(ls)):
      n = n + getC(i)+'app_commands.Choice(name="'+ls[i]+'", value="'+ls[i]+'")'
    n = n + '])'
    pen('from discord import app_commands\nfrom discord.ext import commands\nfrom dislash import InteractionClient, SelectMenu, SelectOption\ndef getChoi():\n\treturn '+n,'getChoice.py')
    import getChoice
    return getChoice.getChoi()
def imageSize():
    return app_commands.choices(size=[app_commands.Choice(name='256x256', value='256x256'),app_commands.Choice(name='512x512', value='512x512'),app_commands.Choice(name='1024x1024', value='1024x1024'),])
def minMax(name,min,max):
    return app_commands.Argument(name=str(name),min_value=min,max_value=max)
def helpAll():
    return "temp:pick the randomness of your interaction\n\nqanda:[prompt]- input a questionquestion mark will auto add\n\ntranslate:[prompt] - enter the text you would like to translate; [language] - enter the desired languages seperated by commas\n\ntext_search_doc:a\n\nwritecode:[prompt]- describe the code; [language] - specify the target language\n\ndebugcode:[prompt]- describe what your focus is;[code]- enter your code\n\neditcode:[prompt]- describe what your focus is;[code]- enter your code\n\nsimilarity:where results are ranked by relevance to a query string\n\ntext_similarity:Captures semantic similarity between pieces of text.\n\ntext_search_query:Semantic information retrieval over documents.\n\ntext_embedding:Get a vector representation of a given input that can be easily consumed by machine learning models.\n\ntext_insert:a\n\ntext_edit:a\n\nsearch_document:where results are ranked by relevance to a document\n\nsearch_query:a\n\ncode_edit:specify the revisions that you are looking to make in the code\n\ncode_search_code:Find relevant code with a query in natural language.\n\ncode_search_text:a\n\nimage_edit:[image]-main image; [mask] secondary image;[prompt]- input how you would like to have it editedimage_variation:[image]- upload an image of your choice; [prompt]- input how you would like it edited\n\nmention:[prompt] - input what youd like to say to the bot\n\nchat:[prompt] - input what youd like to say to the bot Have a chat with ChatGPT\n\nimage_create:[prompt]- input what image you would like to have formulated\n\npublic:Toggle public access\n\nprivate:Toggle private access\n\nhelp:will display all descriptions\n\ntemp:Temperature will allow you to pick the randomness of your interaction; range(0:2) _ input(integer) i.e. 15 will transate to 1.5\n\nparse:[summerize]-summarize what the text is;[subjects]- comma seperated subjects to parse;[prompt]-enter your text\n\nmoderation:[input] - input text you would like to have moderated\n\nedit:[input]-enter your text; [instruction]- tell it what you want it to do."
def getComms(client,k):
    changeGlob('best_of',int(10))
    transIt(client,comms[k])
    qandaIt(client,comms[k])
    chatIt(client,comms[k])
    parseIt(client,comms[k])
    mentionIt(client,comms[k])
    writecodeIt(client,comms[k])
    editcodeIt(client,comms[k])
    debugcodeIt(client,comms[k])
    convertcodeIt(client,comms[k])
    image_createIt(client,comms[k])
    image_editIt(client,comms[k])
    image_variationIt(client,comms[k])
    text_search_docIt(client,comms[k])
    similarityIt(client,comms[k])
    text_similarityIt(client,comms[k])
    text_search_queryIt(client,comms[k])
    text_embeddingIt(client,comms[k])
    text_insertIt(client,comms[k])
    text_editIt(client,comms[k])
    search_documentIt(client,comms[k])
    search_queryIt(client,comms[k])
    code_editIt(client,comms[k])
    code_search_codeIt(client,comms[k])
    code_search_textIt(client,comms[k])
    moderationIt(client,comms[k])
    editIt(client,comms[k])
    privateIt(client,comms[k])
    publicIt(client,comms[k])
    helpIt(client,comms[k])
def run_discord_bot():
    getConfig()
    changeGlob('client',aclient())
    @client.event
    async def on_ready():
        await client.tree.sync()
        logger.info(f'{client.user} is now running!')
    
    for k in range(0,len(comms)):
        getComms(client,k)
    client.run(config['discord_bot_token'])
global parameters,specifications,comms,descriptions
changeGlob('home',os.getcwd())
parameters={'model':{'object':'str','scale':'inherit','default':'text-davinci-003'},
            'max_tokens':{'object':'int','scale':'range','range':{0:2048},'default':2000,},
            'logit_bias':{'object':'map','scale':'range','range':{-100:100},'default':''},
            'size':{'object':'str','default':'1024x1024','scale':'choice','choices':['256x256','512x512','1024x1024']},
            'temperature':{'object':'float','default':float(0.7),'scale':'range','range':{-2.0:2.0}},
            'best_of':{'object':'int','default':1,'scale':'range','range':{0:10}},
            'top_p':{'object':'float','default':float(0.0),'scale':'range','range':{0.0:1.0}},
            'frequency_penalty':{'object':'float','default':float(0.0),'scale':'range','range':{-2.0:2.0}},
            'presence_penalty':{'object':'float','default':float(0.0),'scale':'range','range':{-2.0:2.0}},
            'log_probs':{'object':'int','default':int(1),'scale':'range','range':{1:10}},
            'stop':{'object':'str','default':'','scale':'array','range':{0:4}},
            'echo':{'object':'bool','default':'False','scale':'choice','choice':['True','False']},
            'n':{'object':'int','default':1,'scale':'range','range':{1:10}},
            'stream':{'object':'bool','default':'False','scale':'choice','choice':['True','False']},
            'suffix':{'object':'str','default':'','scale':'range','range':{0:1}},
            'prompt':{'object':'str','default':'""','scale':'inherit'},
            'model':{'object':'str','default':'text-davinci-003','scale':'array','array':['completion','edit','code','embedding']},
            'input':{'object':'str','default':'""','scale':'inherit'},
            'instruction':{'object':'str','default':"''",'scale':'inherit'},
            'response_format':{'object':'str','default':"url",'scale':'choice','choice':['url','b64_json']},
            'image':{'object':'str','default':'""','scale':'upload','upload':{'type':['PNG','png'],'size':{'scale':{0:4},'allocation':'MB'}}},
            'mask':{'object':'str','default':'""','scale':'upload','upload':{'type':['PNG','png'],'size':{'scale':{0:4},'allocation':'MB'}}},
            'file':{'object':'str','default':'""','scale':'upload','upload':{'type':['jsonl'],'size':{'scale':{0:'inf'}},'allocation':'MB'}},
            'purpose':{'object':'str','default':'""','scale':'inherit'},'file_id':{'object':'str','default':'','scale':'inherit'},
            'user':{'object':'str','default':'defaultUser','scale':'inherit'}
            }
specifications={"translate":{'type':'Completion','delims':['translate this text:\n','\n\nto these languages:\n'],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "qanda":{'type':'Completion','delims':['Q:\n','\n\nA:\n'],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "chat":{'type':'Completion','delims':['',''],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "parse":{'type':'Completion','delims':['below is the summary of the data:\n','\n\nparse these variables:\n'],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "random":{'delims':['',''],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "mention":{'type':'Completion','delims':['Q:\n','\n\nA:\n'],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "writecode":{'delims':['in this language:\n','\n\nwrite a code with these specifications:\n'],'models':{'default':'code-cushman-001','choices':['code-cushman-001','code-davinci-002']}},
                "editcode":{'type':'Completion','delims':['',''],'models':{'default':'code-cushman-001','choices':['code-cushman-001','code-davinci-002']}},       
                "debugcode":{'type':'Completion','delims':['',''],'models':{'default':'code-cushman-001','choices':['code-cushman-001','code-davinci-002']}},
                "convertcode":{'type':'Completion','delims':['',''],'models':{'default':'code-cushman-001','choices':['code-cushman-001','code-davinci-002']}},
                "image_create":{'type':'image_create','delims':['','']},
                "image_edit":{'type':'image_edit','delims':['','']},
                "image_variation":{'type':'image_variation','delims':['','']},
                "moderation":{'type':'moderation','delims':['',''],'models':{'default':"text-moderation-001",'choices':["text-moderation-001"]}},
                "edit":{'type':'edit','delims':['',''],'models':{'default':"text-davinci-edit-001",'choices':["text-davinci-edit-001"]}},
                "text_search_doc":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "similarity":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "text_similarity":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "text_search_query":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "text_embedding":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "text_insert":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "text_edit":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "search_document":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "search_query":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "instruct":{'type':'embedding','delims':['',''],'models':{'default':'text-embedding-ada-002','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "code_edit":{'type':'embedding','delims':['',''],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "code_search_code":{'type':'embedding','delims':['',''],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                "code_search_text":{'type':'embedding','delims':['',''],'models':{'default':'text-davinci-003','choices':['text-ada-001','text-davinci-003','text-curie-001','text-babbage-001']}},
                }
comms = ["translate","qanda","chat","parse","mention","writecode","editcode","debugcode","convertcode","image_create","image_edit","image_variation","text_search_doc","similarity","text_similarity","text_search_query","text_embedding","text_insert","text_edit","search_document","search_query","instruct","code_edit","code_search_code","code_search_text","moderation","edit","private","public","help"]            
descriptions= {'range':'range',
               'temp':'pick the randomness of your interaction',
                'qanda':'[prompt]- input a question,question mark will auto add',
                'translate':'[prompt] - enter the text you would like to translate;[language] -enter the desired languages',
                'text_search_doc':'a',
                'writecode':'[prompt]-describe the code; [language] - specify the target language',
                'debugcode':'[prompt]-describe what your focus is;[code]- enter your code',
                'editcode':'[prompt]-describe what your focus is;[code]- enter your code',
                'convertcode':'[code]-input your code;[language]-input the language youd like to convert to',
                'image_variation':'[image]- upload an image of your choice; [prompt]- input how you would like it edited',
                'mention':'[prompt] - input what youd like to say to the bot',
                'chat':'[prompt] - input what youd like to say to the bot, Have a chat with ChatGPT',
                'image_create':'[prompt]- input what image you would like to have formulated',
                'public':'Toggle public access',
                'private':'Toggle private access',
                'help':'will display all descriptions',
                'temp':'Temperature will allow you to pick the randomness of your interaction; range(0:2) _ input(integer)',
                'parse':'[summerize]-summarize the text;[subjects]-comma seperated subjects to parse;[prompt]-entertext',
                'moderation':'[input] - input text you would like to have moderated',
                'edit':'[input]-enter your text; [instruction]- tell it what you want it to do.',
                'shouldBeAllGood':'below-----------^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^',
                'stillInTesting':'below-----------VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV',
                'similarity':'where results are ranked by relevance to a query string',
                'text_similarity':'Captures semantic similarity between pieces of text.',
                'text_search_query':'Semantic information retrieval over documents.',
                'text_embedding':'Get a vector representation of a given input that can be easily consumed by machine learning models',
                'text_insert':'insert text',
                'text_edit':'edit text',
                'search_document':'where results are ranked by relevance to a document',
                'search_query':'search query ',
                'code_edit':'specify the revisions that you are looking to make in the code',
                'code_search_code':'Find relevant code with a query in natural language.',
                'code_search_text':'text search in code',
                'image_edit':'[image]-main image; [mask] secondary image;[prompt]- input how you would like to have it edited'}

global n,untend
untend = {}
if tryItN() == False:
        run_discord_bot()
