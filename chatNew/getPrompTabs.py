import functions as fun
import guiFunctions as guiFun
import PySimpleGUI as sg
global category,specializations,categories,specialization,catKeys,specializedSet,catLs,categoriesJs,specializations,info,tabIndex
import infoSheets as infoS
from infoSheets import mid,categories,parameters,specifications,choi,descriptions,endpoints,paramNeeds,models,engines,cats,info
from PIL import Image
import os
def changeGlob(x,y):
    globals()[x]=y
    return y
def changeGlob(x,y):
    globals()[x]=y
    return y
def openImage(x):
    return Image.open(x)
def addToLs(ls,ls2):
    for k in range(0,len(ls2)):
        ls.append(ls2[k])
    return ls
def mkType(ls):
    x,obj = ls
    if specializedSet['paramJs']['scale'] == 'upload':
        if ky in ['image','mask']:
            return str(x)#generate_from_masked_image(js[ky])
        return open(js[ky], "rb")
    if obj == 'float':
        return float(str(x).replace("'",'').replace("'",''))
    if obj == 'int':
        return int(str(x).split('.')[0].replace("'",'').replace("'",''))
    if obj == 'bool':
        return bool(x)
    else:
        return str(fun.eatAll(str(x),['"',"'"]))
def ifLsIsPieces(lsN,ls):
    for i in range(0,len(ls)):
        if fun.isLs(ls[i]):
            for k in range(0,len(ls[i])):
                lsN.append(ls[i][k])
    return lsN,ls
def isHowMany(ls):
    if fun.isLs(ls[0]):
        if len(ls[0]) > 1:
            return True
    if fun.isLs(ls[0]):
        return False
def getLongestLen(ls):
    highest = [len(str(ls[0])),0]
    for i in range(1,len(ls)):
        if len(str(ls[i]))>highest[0]:
            highest = [len(str(ls[i])),i]
    return highest[0]
def modelSpec(na):
        default,ls = fun.ifInJsWLs(['default','list'],infoS.getChoices(category)[na],['',[]])
        specializedSet['jsParams'].append(guiFun.mkParam(na,str(default),guiFun.dropDown({"ls":infoS.getChoices(category)[na]['list'],"key":na,"size":(getLongestLen(ls),len(ls)),"default_value":str(default)})))
def ifLang(i,na):
    if i == 0:
        return na
    elif typ == 'input':
        ls = txtInput(na,ls[0],ls[1])
    elif typ == 'file':
        guiFun.getBrwsSect(na,parameters[na]['description'],os.getcwd())
        ls = getFileBrowse(na,ls[0],ls[1],ls[2])
def promptSpec(promptJS):
    global category,specializations,categories,specialization,catKeys,specializedSet,catLs,categoriesJs
    if 'vars' in promptJS:
        vars = fun.getKeys(promptJS['vars'])
    vars,ls = fun.mkLs(vars),[]
    for i in range(0,len(vars)):
        if promptJS['vars'][vars[i]]['type'] == 'choice':
            modelSpec(vars[i])
        elif promptJS['vars'][vars[i]]['type'] in ['text','str','list']:
            guiFuns.getList(guiFun.getTxtInput({"title":"","size":(80,10),"font":None,"key":na,"autoscroll":None,"disabled":False,"pad":(0,0),"x_expand":True,"y_expand":True,"change_submits":False}),4,4)
def getlsFromBrac(x,obj):
    ls = str(x).replace('{','').replace('}','').replace(' ','').replace(':',',').split(',')
    for i in range(0,len(ls)):
        ls[i] = mkType([ls[i],obj])
    return ls
def mkAllInLine(ls):
    lsN = []
    ls = wrapAllIdiv(ls)
    for i in range(0,len(ls)):
        if fun.isLs(ls[i]):
            for k in range(0,len(ls[i])):
                lsN.append(ls[i][k])
        else:
            lsN.append(ls[i])
    return lsN
def wrapAllIdiv(ls):
    for k in range(0,len(ls)):
        ls[k] = fun.mkLs(ls[k])
    return ls
def getParamMenu(na,js):
    specializedSet['paramJs'] = js
    if na in infoS.getChoices(category):
        modelSpec(na)
        return
    if na in ['prompt','input']:
      getPrompts(category,specialization)
    else:
        defa,obj,scl = js['default'],js['object'],js['scale']
        if scl == 'upload':
                if 'fileUps' not in specializedSet:
                    specializedSet['fileUps'] = []
                specializedSet['content'] = 'multipart/form-data'
                specializedSet['fileUps'].append(na)
                return
        elif js['object'] == 'bool':
            specializedSet['jsParams'].append(guiFun.mkParam(na,mkType([defa,obj]),guiFun.checkBox({"title":"","visible":True,"key":na,"default":mkType([defa,obj]),"pad":(0,0),"enable_events":True})))
            return 
        elif js['object'] in ['float','int']:
            specializedSet['jsParams'].append(guiFun.mkParam(na,mkType([defa, obj]),guiFun.slider({"title":"","range":getlsFromBrac(str(js['range']),js['object']),"visible":True,"key":na,"default_value":mkType([defa,obj]),"resolution":mkType(["1",js['object']])*abs(mkType(["0.99",js['object']])-(mkType(["1",js['object']]))),"tick_interval":mkType(["0.01",js['object']]),"pad":(0,0),"orientation":'h',"disable_number_display":False,"enable_events":True})))
            return 
    specializedSet['notFound'].append(na)
    return
def getPrompts(category,specialization):
    js =info[category]["specifications"][specialization]["parameters"]['prompt']['vars']
    varKeys = fun.getKeys(js)
    typ,tabLay = ['File','txt'],[[]]
    end = guiFun.txtInputs({"title":"","size":(80,10),"font":'Tahoma 13',"key":'preview',"autoscroll":True,"disabled":False,'expand_x': True, 'expand_y': True,"pad":(0,0)})
    if str(category).lower() == 'images':
        typ = ['Image','png']
        #end = [guiFun.txtBox({"text":"imageConversionPath","change_submits":True,"key":'file_string_Image',"font":None,"background_color":None,"enable_events":True,"grab":False}),
        #       [guiFun.getButton({"title":"image conversion","visible":True,"key":"convert_image","enable_events":True,"button_color":None,"bind_return_key":True})],
        #       sg.Image(size=(300,300),key='preview')]
        
    #tabLay = [[guiFun.txtBox({"text":"upload"+typ[0],"change_submits":True,"key":'file_string_input',"font":None,"background_color":None,"enable_events":True,"grab":False}),guiFun.getFileBrowse({"type":typ[0],"key":specialization+"_browser","ext":typ[1],"enable_events":True}),guiFun.getButton({"title":"uploadIt","visible":True,"key":"upload_"+typ[0],"enable_events":True," button_color":None,"bind_return_key":True})]]
    #for k in range(0,len(specializedSet['fileUps'])):
    #    tabLay[0].append(guiFun.checkBox({"title":specializedSet['fileUps'][k],"visible":True,"key":str(specialization)+"_"+str(specializedSet['fileUps'][k])+'_upload',"default":False,"pad":(0,0),"enable_events":True}))  
    for k in range(0,len(varKeys)):
        varKey = varKeys[k]
        #tabLay[0].append(guiFun.checkBox({"title":str(varKey),"visible":True,"key":str(specialization)+"_"+str(varKey)+"_upload","default":False,"pad":(0,0),"enable_events":True}))  
        if js[varKey]['type'] == 'list':
            import PySimpleGUI as psg
            layout =[guiFun.txtBox({'text':str(js[varKey]['input']),"key":str(str(specialization)+"_"+str(varKey)+"_delimiter"),"font":None,"background_color":None,"enable_events":True,"grab":False}),psg.Input(key=varKey+'_0'), psg.Input(key=varKey+'_1'), psg.Input(key=varKey+'_02'), psg.Input(key=varKey+'_3'), psg.Input(key=varKey+'_4'), psg.Input(key=varKey+'_5')]
        elif js[varKey]['type'] == 'choice':
             layout = [guiFun.dropDown({"title":guiFun.txtBox({'text':str(js[varKey]['input']),"key":str(str(specialization)+"_"+str(varKey)+"_delimiter"),"font":None,"background_color":None,"enable_events":True,"grab":False}),"ls":info[category]['choices'][varKey]['list'],"key":str(str(specialization)+"_"+str(varKey)+"_delimite"),"size":(getLongestLen(info[category]['choices'][varKey]['list']),len(info[category]['choices'][varKey]['list'])),"default_value":''})]
        else:
            layout = [guiFun.txtInputs({"title":"","key":str(str(specialization)+"_"+str(varKey)+"_delimiter"),"size":(80,10),"font":'Courier 8',"key":str(specialization)+"_"+str(varKey),"autoscroll":True,"disabled":False,'expand_x': True, 'expand_y': True,"pad":(0,0),"enable_events":True,"change_submits":True,"k":'-ML MARKDOWN-'})]
        tabLay.append(guiFun.getTab({"title":str(specialization)+"_"+str(varKey),"layout":[layout],"key":str(specialization)+"_"+str(varKey)+'_tab',"visible":True," button_color":None}))
    tabLay[0] = addToLs(tabLay[0],fun.mkLs(end))
    tabLay[0] = guiFun.getTab({"title":str(specialization)+"_fileUpload","layout":[mkAllInLine(tabLay[0])],"key":str(specialization)+"_fileUpload_tab","visible":True,"button_color":None,"orientation":'h',"k":'-TABGROUP-'})
    specializedSet['jsList'].append([guiFun.getTabGroup({"title":'promptTabsGroup',"layout":[tabLay],"key":'promptTabsGroup',"visible":True,"key":None,"enable_events":True," button_color":None,"bind_return_key":True,"change_submits":True,"k":'-TABGROUP-'})])
def getParamNeeds(category,specialization):
    n = paramNeeds[category]
    if 'specialized' in fun.getKeys(n):
      n = n['specialized'][specialization]
    return n
def getParamColumn(category,specialization):
  
        changeGlob('category',category)
        changeGlob('specialization',specialization)
        optLs = ['required','optional']
        cou = 0
        txt0 = [guiFun.txtBox({"text":specialization,"key":None,"font":'Any 20',"background_color":None,"enable_events":True,"grab":False})]
        paramNeedCat = paramNeeds[category]
        k = 0
        if 'specialized' in fun.getKeys(paramNeedCat):
          paramNeedCat = paramNeedCat['specialized'][specialization]
        if category == 'moderation':
              paramNeedCat = paramNeedCat['moderate']
        for i in range(0,len(optLs)):
        
              specializedSet['opt'] = [True,False][i]
              paramNeedOPT = paramNeedCat[optLs[i]]
              for k in range(0,len(paramNeedOPT)):
                    specializedSet['prevKeys'].append(paramNeedOPT[k])
                    getParamMenu(paramNeedOPT[k],parameters[paramNeedOPT[k]])
                    cou +=1


def getScreen():
    import tkinter
    win= Tk()
    win.geometry("650x250")
    return [win.winfo_screenwidth(),win.winfo_screenheight()]
def findStrInLs(ls,x):
    lsN = []
    for k in range(0,len(ls)):
        if str(x) in str(ls[k]):
            lsN.append(ls[k])
    return lsN
def simpleEvent(layout):
  txt0 = guiFun.txtBox({"text":'parameters',"key":None,"font":'Any 20',"background_color":None,"enable_events":True,"grab":False})
  layout = [[txt0],[specializedSet['jsList']]]
  window = sg.Window('Dashboard PySimpleGUI-Style',[layout], margins=(5,5), element_padding=(5,5), background_color='blue', keep_on_top=False, no_titlebar=False, resizable=True, right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_VER_LOC_EXIT)
  while True:
        event, values = window.read()
        valKeys = fun.getKeys(values)[1:]
        print([event,values])
        if '_default_' in str(event):
            spl = event.split('_default_')
            defa = mkType([spl[1],parameters[spl[0]]['object']])
            if values[event] == True:
                window[spl[0]].update(value=mkType([spl[1],parameters[spl[0]]['object']]))
            if mkType([spl[1],parameters[spl[0]]['object']]) == defa:
                window[event].update(value=True)
        elif event in parameters['all']:
            defa,obj,eVal,defaultKey = parameters[event]['default'],parameters[event]['object'],values[event],findStrInLs(valKeys,event+'_default_')
            for k in range(0,len(defaultKey)):
                defa,eVal=mkType([defa,obj]),mkType([eVal,obj])
                if eVal == defa:
                    window[defaultKey[k]].update(value=True)
                elif eVal != defa:
                    window[defaultKey[k]].update(value=False)
        elif '_info' in event:
            req,na = 'optional',event.split('_info')[0]
            if na in getParamNeeds(category,specialization)['required']:
                req = 'required'
            sg.popup_scrolled('name:'+str(na)+',  | default:'+str(req)+' | type:'+str(parameters[na]['object'])+'\ndescription: ',parameters[na]['description'])
        elif 'upload_' in event:
            if specialization+'_browser' in values:
           
                path = values[specialization+'_browser']
                if path != '':
                    if event == 'upload_Image':
                        window['preview'].update(path)
                    if event == 'upload_File':
                        text = fun.reader(path)
                        window['preview'].update(value=text)
                        uploads = findStrInLs(valKeys,event+'_upload')
                        for k in range(0,len(uploads)):
                            if values[uploads[k].split('_upload')[0]] == True:
                                window[fun.getKeys(infoS.getAllThings(category,specialization)['prompt']['parse']['vars'])[0]].update(value=text)
                                len(text)
                                window.getScreen()
                        if len(uploads) == 0:
                            window[fun.getKeys(infoS.getAllThings(category,specialization)['prompt']['parse']['vars'])[0]].update(value=text)
        elif 'convert_image' in event:
                import demoImgh64
                try:
                    demoImgh64.main()
                except:
                    print('that didnt go well')
global info
info ={"completions":{"categories":["chat","translate","qanda","parse"],
                      "endpoints": {"chat": "https://api.openai.com/v1/completions", "chat": "https://api.openai.com/v1/completions", "translate": "https://api.openai.com/v1/completions", "qanda": "https://api.openai.com/v1/completions","parse": "https://api.openai.com/v1/completions", 'form':'application/json',"response": ["choices", "n", "text"]},
                      "choices":{"model":{'default': 'text-davinci-003', 'list': ['text-ada-001', 'text-davinci-003', 'text-curie-001', 'text-babbage-001']}},
                      "specifications":{
                        'chat':{'type': 'completions','refference':['completions','create'],"parameters":{'required':['model','prompt'],'optional':['user','stream','n','suffix','max_tokens','logit_bias','temperature','best_of','top_p','frequency_penalty','presence_penalty','stop','echo'],'prompt':{"task":"chat","structure": '','vars': {'prompt':{"input":"what would you like to say to the bot?","delimiter":''}}}}
                                },
                        "chat": {"type": "completions", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": "chat", "structure": "", "vars": {"prompt": {"input": "what would you like to say to the bot?", "type": "str","ogVar":"prompt", "delimiter": ""}}}}
                                 },
                        "translate": {"type": "completions", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": "task: translate text", "structure": "languages to translate to:[languages];translate the following text:[text]", "vars": {"languages": {"input": "specify the target languages", "type": "list","ogVar":"prompt", "delimiter": "languages to translate to:\n"}, "text": {"input": "input the text you would like to have translated", "type": "text","ogVar":"prompt", "delimiter": "translate the following text:\n"}}}}
                                      },
                        "qanda": {"type": "completions", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": "task: question and answer", "structure": "[question]- input a question,question mark will auto add, [answer] - proposed answer to a question", "vars": {"question": {"input": "pose a question to have answered", "type": "str","ogVar":"prompt","delimiter": "Q:"}, "answer": {"input": "pose answer to a proposed question", "type": "str","ogVar":"prompt", "delimiter": "A:"}}}}
                                  },
                        "parse": {"type": "completions", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": "task: parse text,", "structure": " a [summary] of the [data] will be given in order to parse specific [subjects]:", "vars": {"summary": {"input": "summarize the text you would like to parse", "type": "text","ogVar":"prompt", "delimiter": "summary of data:\n"}, "subjects": {"input": "specific subjects you want to have parsed", "type": "list","ogVar":"prompt", "delimiter": "subjects:\n"}, "data": {"input": "text you would like to have parsed", "type": "text","ogVar":"prompt", "delimiter": "data to parse:\n"}}}}
                                  }
                        }
                      },
       
       "coding": {"categories":["writecode","editcode","debugcode","convertcode"],
                  "endpoints": {"editcode": "https://api.openai.com/v1/completions", "debugcode": "https://api.openai.com/v1/completions", "convertcode": "https://api.openai.com/v1/completions", "writecode": "https://api.openai.com/v1/completions", "form":"application/json", "response": ["choices", "n", "text"]},
                  "choices": {"language": {"default": "python", "list": ["Python", "Java", "C++", "JavaScript", "Go", "Julia", "R", "MATLAB", "Swift", "Prolog", "Lisp", "Haskell", "Erlang", "Scala", "Clojure", "F#", "OCaml", "Kotlin", "Dart"]},
                              "model": {"default": "code-davinci-002", "list": ["code-cushman-001", "text-davinci-003", "code-davinci-002"]}},
                  "specifications": {
                    "writecode": {"type": "coding", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": '#task: write code', "structure": "write code in [language] from [description]", "vars": {"description": {"input": "describe what you are looking for, be specific", "type": "str","ogVar":"prompt", "delimiter": "instructuions:\n"}, "language": {"input": "which language would you like the code to be written in?", "type": "choice","ogVar":"prompt", "delimiter": "language:\n,"}}}}},
                    "editcode": {"type": "coding", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": '#task: edit code', "structure": "edit [code] via [instructions]", "vars": {"instruction": {"input": "provide specific instructions on what you are looking to have edited about this code:", "type": "str","ogVar":"prompt", "delimiter": "instructions:\n"}, "code": {"input": "enter the code you would like to have edited:", "type": "str","ogVar":"prompt", "delimiter": "code:\n"}}}}},
                    "debugcode": {"type": "coding", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": '#task: debug code:', "structure": "debug the following code:\n", "vars": {"code": {"input": "the code you would like to have debugged", "type": "str","ogVar":"prompt", "delimiter": ""}}}}},
                    "convertcode": {"type": "coding", "refference": ["completions", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "suffix", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": '#task: convert code', "structure": "convert the following [code] to [language]", "vars": {"language": {"input": "the language you would like the code converted to:", "type": "choice","ogVar":"prompt", "delimiter": "language:\n"}, "code": {"input": "the code you would like to have converted", "type": "str","ogVar":"prompt", "delimiter": "code:\n"}}}}}
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       },
       "images": {"categories":["image_variation","image_create","image_edit"],
                  "endpoints": {"image_create": "https://api.openai.com/v1/images/generations", "image_variation": "https://api.openai.com/v1/images/variations", "image_edit": "https://api.openai.com/v1/images/edits", "form":"multipart/form-data","response": ["data", "n", "response_format"]},
                  "choices": {"response_format": {"default": "url", "list": ["url", "b64_json"]}, "size": {"default": "1024x1024", "list": ["256x256", "512x512", "1024x1024"]}},
                  "specifications": {
                    "image_variation": {"type": "images", "refference": ["image", "create", "image_variation"], "parameters": {"required": ["image"], "optional": ["prompt", "size", "n", "response_format", "user", "n", "suffix", "max_tokens", '#logit_bias', "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop", "echo"], "prompt": {"task": "image variation", "structure": "getnerate [image] variation from [description] if given:\n", "vars": {"instructions": {"input": "describe what you would like to have done with the image(s):", "type": "str","ogVar":"prompt", "delimiter": "description:\n"}}}}},
                    "image_create": {"type": "images", "refference": ["image", "create", "image_create"], "parameters": {"required": ["prompt"], "optional": ["size", "n", "response_format", "user", "suffix", "logit_bias"], "prompt": {"task": '#image creation', "structure": "create an image from [description]:\n", "vars": {"description": {"input": "describe the image you would like to create:", "type": "str","ogVar":"prompt", "delimiter": "instructions:"}}}}},
                    "image_edit": {"type": "images", "refference": ["image", "create", "image_edit"], "parameters": {"required": ["image", "prompt"], "optional": ["mask", "size", "n", "response_format", "user", "suffix", "max_tokens", "logit_bias"], "prompt": {"task": "image_edit", "structure": "[image]-main image; [mask] secondary image;[prompt]-:", "vars": {"instructions": {"input": "[image]-main image; [mask] secondary image;[prompt]- instructions on how it should be edited:", "type": "str","ogVar":"prompt", "delimiter": "instructions:"}}}}}}
                  },
       "edit": {"categories":["edits"],
                "endpoints": {"edit": "https://api.openai.com/v1/embeddings",  "form:":"application/json", "response": ["data", "n", "embedding"]}, "choices": {"model": {"default": "text-ada-001", "list": ["text-ada-001", "text-davinci-003", "text-curie-001", "text-babbage-001"]}},
                "specifications": {
                  "edits": {"type": "edits", "refference": ["edits", "create"], "parameters": {"required": ["model", "prompt"], "optional": ["user", "stream", "n", "max_tokens", "logit_bias", "temperature", "best_of", "top_p", "frequency_penalty", "presence_penalty", "stop"], "prompt": {"task": "edit text", "structure": "[image]-main image; [mask] secondary image;[prompt]- input how you would like to have it edited", "vars": {"instructions": {"input": "provide instructions describing what you would like to have edited:", "type": "str","ogVar":"prompt", "delimiter": "instructions:"}}}}
                            }
                  }
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             },
       "moderation": {"categories":["moderate"],
                      "endpoints": {"moderate": "https://api.openai.com/v1/moderations", "form":"application/json", "response": ["results", "n", "text"]}, "choices": {"model": {"default": "None", "list": ["text-moderation-004", "davinci"]}},
                      "specifications": {
                        "moderate": {"type": "moderation", "refference": ["moderation"], "parameters": {"required": ["input"], "optional": ["model"], "prompt": {"task": "moderation", "structure": "text to moderate:\n", "vars": {"input": {"input": "provide the text you would like to have moderated", "type": "text","ogVar":"prompt", "delimiter": "moderate the following"}}}}}}
                      }
       }
changeGlob('specializedSet',{'notFound':[],'fileUps':[],'inputTabKeys':{'types':[],'inputLs':[],'index':1,'names':[],'descriptions':[]},'jsList':[],'jsParams':[sg.Text('Parameters', font='Any 20')],'prevKeys':[]})
layouts = []

keys = fun.getKeys(categories)
layers = []
def getTabs():
    for k in range(0,len(keys)):
        category = keys[k]
        specializationLs = categories[category]
        for i in range(0,len(specializationLs)):
            specialization = specializationLs[i]
            getParamColumn(category,specialization)
            txt0 = guiFun.txtBox({"text":'parameters'+str(k),"key":None,"font":'Any 20',"background_color":None,"enable_events":True,"grab":False})
            layouts.append(specializedSet['jsList'])
            layers.append([guiFun.getTab({"title":specialization,"layout":specializedSet['jsList'],"key":str(specialization)+'_Tab_',"visible":True,"disabled":False,"title_color":None,"change_submits":True,"enable_events":True})])
            changeGlob('specializedSet',{'notFound':[],'fileUps':[],'inputTabKeys':{'types':[],'inputLs':[],'index':1,'names':[],'descriptions':[]},'jsList':[],'jsParams':[sg.Text('Parameters', font='Any 20')],'prevKeys':[]})
    return [guiFun.getTabGroup({"title":'allTabs',"layout":layers,"key":'allTabs',"visible":True,"enable_events":True,'expand_x': True, 'expand_y': True," button_color":None,"bind_return_key":True,"change_submits":True},)]
