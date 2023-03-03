import PySimpleGUI as sg
import functions as fun
import json
"""
    These 8 "Constructs" or Design Patterns demonstrate numerous ways of "generating" or building your layouts
    0 - A simple list comprehension to build a row of buttons
    1 - A simple list comprehension to build a column of buttons
    2 - Concatenation of rows within a layout
    3 - Concatenation of 2 complete layouts [[ ]] + [[ ]] = [[ ]]
    4 - Concatenation of elements to form a single row [ [] + [] + [] ] = [[ ]]
    5 - Questionnaire - Using a double list comprehension to build both rows and columns in a single line of code
    6 - Questionnaire - Unwinding the comprehensions into 2 for loops instead
    7 - Using the * operator to unpack generated items onto a single row 
    8 - Multiple Choice Test - a practical use showing list comprehension and concatenated layout
"""
def getDefs(js,jsDef):
    keys = fun.getKeys(js)
    for k in range(0,len(keys)):
        key = keys[k]
        jsDef[key] = js[key]
    return jsDef
def eatAll(x,ls):
    while x[0] in ls:
        x = x[1:]
    while x[-1] in ls:
        x = x[:-1]
    return x
def addAll(x,ls):
    x = eatAll(x,ls)
    while x[0] in ls:
        x = x[1:]
    while x[-1] in ls:
        x = x[:-1]
    x = ls[0]+str(x)+ls[0]
    return x
def mkJs(n,x,y):
    return n +str(addAll(x,['"',"'"]))+'=js['+addAll(y,['"',"'"])+'],'
def mkJsReturn(n,x):
    return n +str(eatAll(x,['"',"'"]))+'=js['+addAll(x,['"',"'"])+'],'
def mkReturnJS(js):
    n,keys = '',fun.getKeys(js)
    for i in range(0,len(keys)):
        n = mkJsReturn(n,eatAll(keys[i]))
    return n[:-1]
def mkReturnls(ls):
    name,sgName,ls = ls
    n,js = '',{}
    for i in range(0,len(ls)):
        spl = fun.mkLs(ls[i].replace(' =','=').replace('= ','=').split('='))
        js[eatAll(spl[0],['"',"'"])] = ""
        if '=' in ls[i]:
            js[eatAll(spl[0],['"',"'"])] = boolIt(spl[1])
        n = mkJsReturn(n,spl[0])
    n = 'def '+name+'(js):\n\tjs = getDefs(js,'+str(js)+'):\n\treturn '+sgName+'('+n[:-1]+')'
    return n
def boolIt(x):
    if str(x) in ['None','True','False']:
        return bool(x)
    if [str(x)[0],str(x)[-1]] == ['(',')']:
        return eatAll(x,['"',"'"])
    return x
stri = '''Graph(canvas_size,
    graph_bottom_left,
    graph_top_right,
    background_color = None,
    pad = None,
    p = None,
    change_submits = False,
    drag_submits = False,
    enable_events = False,
    motion_events = False,
    key = None,
    k = None,
    tooltip = None,
    right_click_menu = None,
    expand_x = False,
    expand_y = False,
    visible = True,
    float_values = False,
    border_width = 0,
    metadata = None)'''
def ifNotInParse(x,ls,delim):
    input(x)
    name,end= x.split('(')[0],x.split(')')[-1]
    x = x[len(name+'('):-len(')'+end)]
    input(x)
    input(x)
    z,lsN,parse = '',[],True
    for i in range(0,len(x)):
        if x[i] == ls[0]:
            parse = False
        elif x[i] == ls[1]:
            parse = True
        elif x[i] == delim and parse == True:
            lsN.append(eatAll(z,['\n','\t',' ',',']))
            z = ''
        z = z + x[i]
    input(lsN)
    return [name,'sg.'+name,lsN]
#input(mkReturnls(ifNotInParse(stri,['(',')'],',')))
def getButton(js):
	js = getDefs(js,{"title":"","visible":True,"key":None,"enable_events":False," button_color":None,"bind_return_key":None})
	return sg.Button(js["title"],visible=js["visible"],key=js["key"],enable_events=js["enable_events"],bind_return_key=js["bind_return_key"])
def parseRaw(raw):
    raw,js = raw.split('\n'),{}
    for k in range(0,len(raw)):
        spl = raw[k].split(' = ')
        js[str(spl[0])]=spl[1]
def txtBox(js):
    js = getDefs(js,{"text":"","key":None,"font":None,"background_color":None,"enable_events":False,"grab":None})
    return  sg.Text(js["text"],key=js["key"],font=js["font"],background_color=js["background_color"],enable_events=js["enable_events"], grab=js["grab"])
def pushBox(js):
	js = getDefs(js,{"background_color":None})
	return  sg.Push(background_color=js["background_color"])
def getT(js):
    js = getDefs(js,{"title":"","key":None,"font":None,"background_color":None,"enable_events":False,"grab":None})
    title = js["title"]
    return sg.T(title,key=js["key"])
def getOutput(js):
    return sg.Output(size=js["size"], font=js["font"])
def slider(js):
	js = getDefs(js,{"title":"","range":(1,1),"visible":True,"key":None,"default_value":None,"resolution":1,"tick_interval":1,"pad":(0,0),"orientation":'h',"disable_number_display":False,"enable_events":False,"size":(25,15)})
	return  sg.Slider(range=js["range"],visible=js["visible"],key=js["key"],size=js["size"],default_value=js["default_value"],resolution=js["resolution"],pad=js["pad"],orientation=js["orientation"],disable_number_display=js["disable_number_display"], enable_events=js["enable_events"])
def checkBox(js):
	js = getDefs(js,{"title":"","visible":True,"key":None,"default":None,"pad":(0,0),"enable_events":False,"element_justification":None})
	return  sg.Checkbox(js["title"],visible=js["visible"],key=js["key"],default=js["default"],pad=js["pad"],enable_events=js["enable_events"])
def dropDown(js):
	js = getDefs(js,{"ls":"","key":None,"size":(25,15),"default_value":None,"auto_size_text":True,"enable_events":True,"pad":(0,0),"enable_events":False,"element_justification":None})
	return  sg.Combo(js["ls"],key=js["key"],size=js["size"],default_value=js["default_value"],auto_size_text=["auto_size_text"],pad=js["pad"],enable_events=js["enable_events"])
def txtInputs(js):
	js = getDefs(js,{"title":"","size":(max,10),"font":None,"key":None,"autoscroll":None,"disabled":False,"pad":(0,0),"change_submits":False,"expand_y":True,"expand_x":True,"scrollable":True,"autoscroll":True,"k":None})
	return sg.Multiline(js["title"],size=js["size"],expand_x=js["expand_x"],expand_y=js["expand_y"],font=js["font"],key=js["key"],autoscroll=js["autoscroll"],disabled=js["disabled"],change_submits=js["change_submits"],k=js["k"])
def vertSep(js):
        js = getDefs(js,{"title":"","size":None,"font":None,"key":None,"autoscroll":None,"disabled":False,"pad":(0,0)})
        return sg.VerticalSeparator(pad=js["pad"])
def getTab(js):
	js = getDefs(js,{"title":"","layout":"","key":None,"visible":True,"disabled":False,"title_color":None,"change_submits":True,"enable_events":True})
	print(js)
	layout,na = js["layout"],js['title']
	return sg.Tab(na,layout,key=js["key"],visible=js["visible"],disabled=js["disabled"],title_color=js["title_color"])
def getFileBrowse(js):
        js = getDefs(js,{"type":"file","key":None,"ext":"txt","enable_events":False})
        return sg.FileBrowse(file_types=((js["type"], "*."+str(js["ext"])),),key=js["key"],enable_events=js["enable_events"])
def getTabGroup(js):
	js = getDefs(js,{"layout":"","key":None,"visible":True,"key":None,"enable_events":False," button_color":None,"bind_return_key":None,"change_submits":False})
	tabs = js["layout"]
	return  sg.TabGroup(tabs,key=js["key"],enable_events=js["enable_events"],visible=js["visible"],change_submits=js["change_submits"])
def getFrame(js):
	js = getDefs(js,{'title': '', 'layout': '', 'title_color': True, 'background_color': True, 'title_location': True, 'relief': "groove", 'size': (None, None), 's': (None, None), 'font': True, 'pad': True, 'p': True, 'border_width': True, 'key': True, 'k': True, 'tooltip': True, 'right_click_menu': True, 'expand_x': True, 'expand_y': True, 'grab': True, 'visible': True, 'element_justification': "l", 'vertical_alignment': True})
	title=js["title"]
	layout=js["layout"]
	return sg.Frame(title,layout,title_color=js["title_color"],background_color=js["background_color"],title_location=js["title_location"],relief=js["relief"],size=js["size"],s=js["s"],font=js["font"],pad=js["pad"],p=js["p"],border_width=js["border_width"],key=js["key"],k=js["k"],tooltip=js["tooltip"],right_click_menu=js["right_click_menu"],expand_x=js["expand_x"],expand_y=js["expand_y"],grab=js["grab"],visible=js["visible"],element_justification=js["element_justification"],vertical_alignment=js["vertical_alignment"])
def getColumn(js):
    js = getDefs(js,{"layout":'',"pad":(0,0),"expand_x":True, "expand_y":True, "grab":True,"scrollable":True,  "vertical_scroll_only":False,"horizontal_scroll_only":False,"element_justification":'c',"size_subsample_height":5})
    layout = js["layout"]
    return sg.Column(layout,pad=js["pad"],expand_x=js["expand_x"],expand_y=js["expand_y"],grab=js["grab"],scrollable=js["scrollable"],vertical_scroll_only=js["vertical_scroll_only"],element_justification=js["element_justification"],size_subsample_height=js["size_subsample_height"])
def adjustablescreen():
    column_layout = [[sg.Text(f'Line {i+1:0>3d}'), sg.Input()] for i in range(100)]
    layout = [[sg.Column(column_layout, scrollable=True,  vertical_scroll_only=True, size_subsample_height=5)]]
    return sg.Window('Title', layout).read(close=True)
def getList(layout,colR,rowR):
        return [[layout for col in range(colR)] for row in range(rowR)]
def getFullParams(js):
        return [[checkBox({"title":"def","visible":True,"key":js["title"]+'_default_'+str(js["default"]),"default":js["default"],"pad":(len('default'),len('default')),"enable_events":True})],[js["layout"]],[getButton({"title":js["title"],"visible":True,"key":js["title"]+"_info","enable_events":True,"button_color":None,"bind_return_key":True})]]
def mkParam(na,defa,layout):
        return [getFullParams({"title":na,"default":defa,"layout":layout})]
def ButtonMenu(js):
	js = getDefs(js,{'button_text': '', 'menu_def': '', 'tooltip': True, 'disabled': True, 'image_source': True, 'image_filename': True, 'image_data': True, 'image_size': (None, None), 'image_subsample': True, 'image_zoom': True, 'border_width': True, 'size': (None, None), 's': (None, None), 'auto_size_button': True, 'button_color': True, 'text_color': True, 'background_color': True, 'disabled_text_color': True, 'font': True, 'item_font': True, 'pad': True, 'p': True, 'expand_x': True, 'expand_y': True, 'key': True, 'k': True, 'tearoff': True, 'visible': True, ',auto_size_button': 'None,button_color'})
	return sg.ButtonMenu(button_text=js["button_text"],menu_def=js["menu_def"],tooltip=js["tooltip"],disabled=js["disabled"],image_filename=js["image_filename"],image_data=js["image_data"],image_size=js["image_size"],image_subsample=js["image_subsample"],border_width=js["border_width"],size=js["size"],s=js["s"],auto_size_button=js["auto_size_button"])
#ButtonMenu({'button_text': ''})
stri = '''
def txtBox(js):
    js = getDefs(js,{"text":"","key":None,"font":None,"background_color":None,"enable_events":False,"grab":None})
    return  sg.Text(js["text"],key=js["key"],font=js["font"],background_color=js["background_color"],enable_events=js["enable_events"], grab=js["grab"])
def pushBox(js):
	js = getDefs(js,{"background_color":None})
	return  sg.Push(background_color=js["background_color"])
def slider(js):
	js = getDefs(js,{"title":"","range":(1,1),"visible":True,"key":None,"default_value":None,"resolution":1,"tick_interval":1,"pad":(0,0),"orientation":'h',"disable_number_display":False,"enable_events":False,"size":(25,15)})
	return  sg.Slider(range=js["range"],visible=js["visible"],key=js["key"],size=js["size"],default_value=js["default_value"],resolution=js["resolution"],pad=js["pad"],orientation=js["orientation"],disable_number_display=js["disable_number_display"], enable_events=js["enable_events"])
def checkBox(js):
	js = getDefs(js,{"title":"","visible":True,"key":None,"default":None,"pad":(0,0),"enable_events":False})
	return  sg.Checkbox(js["title"],visible=js["visible"],key=js["key"],default=js["default"],pad=js["pad"],enable_events=js["enable_events"])
def dropDown(js):
	js = getDefs(js,{"ls":"","key":None,"size":(25,15),"default_value":None})
	return  sg.Combo(js["ls"],key=js["key"],size=js["size"],default_value=js["default_value"])
def getButton(js):
	js = getDefs(js,{"title":"","visible":True,"key":None,"enable_events":False," button_color":None,"bind_return_key":None})
	return sg.Button(js["title"],visible=js["visible"],key=js["key"],enable_events=js["enable_events"],bind_return_key=js["bind_return_key"])
def txtInputs(js):
	js = getDefs(js,{"title":"","size":None,"font":None,"key":None,"autoscroll":None,"disabled":False,"pad":(0,0),"change_submits":False})
	return sg.Multiline(js["title"],size=js["size"],font=js["font"],key=js["key"],autoscroll=js["autoscroll"],disabled=js["disabled"],change_submits=js["change_submits"],enable_events=js["enable_events"])
def vertSep(js):
        js = getDefs(js,{"title":"","size":None,"font":None,"key":None,"autoscroll":None,"disabled":False,"pad":(0,0)})
        return sg.VerticalSeparator(pad=js["pad"])
def getTab(js,layout):
	js = getDefs(js,{"title":"","layout":"","key":None,"visible":True,"disabled":False,"title_color":None,change_submits=js["change_submits"],enable_events=js["enable_events"]})
	return sg.Tab(js["title"],layout,key=js["key"],visible=js["visible"],disabled=js["disabled"],title_color=js["title_color"],enable_events=js["enable_events"])
def getFileBrowse(js):
        js = getDefs(js,{"type":"file","key":None,"ext":"txt","enable_events":False})
        return sg.FileBrowse(file_types=((js["type"], "*."+str(js["ext"])),),key=js["key"],enable_events=js["enable_events"])
def getTabGroup(js):
	js = getDefs(js,{"tabs":"","key":None,"visible":True,"key":None,"enable_events":False," button_color":None,"bind_return_key":None})
	return  sg.TabGroup(js["tabs"],key=js["key"],enable_events=js["enable_events"],bind_return_key=js["bind_return_key"])
def getTab(na,layout):
    return sg.Tab(na, layout)
def getTabGroup(tabs,key):
    return sg.TabGroup(tabs,key=key)
def column(layout):
    return sg.Column(layout, scrollable=True,  vertical_scroll_only=True, size_subsample_height=5)
def adjustablescreen():
    column_layout = [[sg.Text(f'Line {i+1:0>3d}'), sg.Input()] for i in range(100)]
    layout = [[sg.Column(column_layout, scrollable=True,  vertical_scroll_only=True, size_subsample_height=5)]]
    sg.Window('Title', layout).read(close=True)
def getList(layout,colR,rowR):
        return [[layout for col in range(colR)] for row in range(rowR)]
def getFullParams(js):
        return [[checkBox({"title":"def","visible":True,"key":js["title"]+'_default_'+str(js["default"]),"default":js["default"],"pad":(len('default'),len('default')),"enable_events":True})],[js["layout"]],[getButton({"title":js["title"],"visible":True,"key":js["title"]+"_info","enable_events":True,"button_color":None,"bind_return_key":True})]]
def mkParam(na,defa,layout):
        return [getFullParams({"title":na,"default":defa,"layout":layout})]'''
def makeJs():
    stris=stri.split('def ')
    for k in range(1,len(stris)):
        spl = stris[k].split('\n')
        name = spl[0].split('(')[0].replace(' ','')
        vars = spl[0].split('(')[1].replace(' ','').split('):')[0]
        for i in range(0,len(spl)):
            if 'js = getDefs(js,{' in spl[i]:
                defaults = spl[i].split('js = getDefs(js,{')[1].split('})')[0]
            if 'return ' in spl[i]:
                returns = spl[i].split('return ')[1]
                sg = returns.split('(')[0]
        default = defaults.split(',')
        retsLs,rets = returns = returns.split(','),[]
        de,ans,defLs,retLs = '','',[],[]
        for i in range(0,len(rets)):
            retsLs.append(rets[i].split('=')[0])
        for i in range(0,len(default)):
            currDef = default[i].split(':')
            if currDef[0][0] in ['"',"'"]:
                currDef[0] = currDef[0][1:]
            if currDef[0][-1] in ['"',"'"]:
                currDef[0] = currDef[0][:-1]
            defLs.append(currDef)
        for i in range(0,len(retLs)):
            if retLs[i] not in defLs:
                defLs.append(retLs[i][0])
        for i in range(0,len(defLs)):
            if defLs not in retLs:
                retLs.append(defLs[i][0])
            input(str('{'+defaults+'}').replace("'",'"'))
        defa,jsNew =  json.loads(str('{'+str(defaults)+'}').replace("'",'"').replace('None','"None"').replace('False','"False"').replace('True','"True"')),{}
        for i in range(0,len(defLs)):
            jsNew[defLs[i][0]] = defa[defLs[i][0]]
            if defa[defLs[i][0]] in ["None","False","True"]:
                jsNew[defLs[i][0]] = bool(defa[defLs[i][0]])
            
            ans = ans + defLs[i][0]+'=js["'+str(defLs[i][0])+'"],'
            
        func = 'def '+str(name)+'('+vars+'):\n\t getDefs(js,'+json.dumps(jsNew)+'\n\treturn '+str(sg)+'('+str(ans)+')'

stri = '''button_text = "",
    button_type = 7,
    target = (None, None),
    tooltip = None,
    file_types = (('ALL Files', '*.* *'),),
    initial_folder = None,
    default_extension = "",
    disabled = False,
    change_submits = False,
    enable_events = False,
    image_filename = None,
     image_data = None,
    image_size = (None, None),
    image_subsample = None,
    image_zoom = None,
    image_source = None,
    border_width = None,
    size = (None, None),
    s = (None, None),
    auto_size_button = None,
    button_color = None,
    disabled_button_color = None,
    highlight_colors = None,
    mouseover_colors = (None, None),
    use_ttk_buttons = None,
    font = None,
    bind_return_key = False,
    focus = False,
    pad = None,
    p = None,
    key = None,
    k = None,
    right_click_menu = None,
    expand_x = False,
    expand_y = False,
    visible = True,
    metadata = None
'''
def eatAll(x,ls):
    for i in range(0,1):
        if len(x) == 0:
                return ""
        while x[-i] in ls:
            
            if i == 0:
                x = x[1:]
            else:
                x = x[:-1]
            if len(x) == 0:
                return ""
    return x
def parseBut():
    name,stri = 'Button',stri.split('\n')
    js,n,extra = {},'',''
    for k in range(0,len(stri)):
        part,single = stri[k],False
        part = eatAll(part,[',',' ','','\t'])
        part = fun.mkLs(part.replace(' =','=').replace('= ','=').split('='))
        if len(part)==1:
            part.append("None")
            single = True
        for i in range(0,2):
            part[i] = eatAll(part[i],[',',' ','','\t',"'",'\n'])
        if part[1][-1] == ',':
            part[1] = part[1][:-1]
        js[str(part[0])] = part[1]
        n = n + part[0]+'=js["'+part[0]+'"],'
        if single == True:
            extra = extra + part[0]+'=js["'+part[0]+'"]\n'
            single = False

    whole = str('\ndef get'+str(name)[0].upper()+str(name)[1:].lower()+'(js):\n\tgetDefs(js,'+str(js)+')\n\t'+extra+'\n\treturn sg.'+name+'('+str(n)+')').replace("'True'","True").replace("'None'","None").replace("'False'","False").replace(',=js[""],','').replace('=js[""]','').replace("'"+'""'+"'",'""').replace("'(",'(').replace(")'",')')
    input(whole)       
'''txtBox({"title":"","key":None,"font":None,"background_color":None,"enable_events":False," grab":None})
slider({"title":"","range":None,"visible":True,"key":None,"default_value":None,"resolution":None,"tick_interval":None,"pad":(0,0),"orientation":None,"disable_number_display":None,"enable_events":False})
checkBox({"title":"","visible":True,"key":None,"default":None,"pad":(0,0),"enable_events":False})
dropDoiwn{"ls":"","key":None,"size":None,"default_value":None})
getButton({"title":"","visible":True,"key":None,"enable_events":False," button_color":None,"bind_return_key":None})
txtInputs({"title":"","size":None,"font":None,"key":None,"autoscroll":None,"disabled":False,"sg.VerticalSeparator(pad":None})
getTab({"title":"","layout":"","key":None,"visible":True,"disabled":False,"title_color":None})
getTabGroup({"tabs":"","key":None})
getList({"title":"",'''
