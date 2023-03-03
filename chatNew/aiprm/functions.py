import os
import json
def changeGlob(x,y):
    globals()[x] = y
    return y
def crPa(x,y):
    return os.path.join(str(x),str(y))
def isFile(x):
    return os.path.isfile(crPa(home,x))
def homeIt():
    changeGlob('home',os.getcwd())
    if changeGlob('slash','/') not in home:
        changeGlob('slash','\\')
    return home,slash
def exists(x):
    try:
        x = reader(x)
        return True
    except:
        return False
def getKeys(js):
  lsN = []
  try:
    for key in js.keys():
      lsN.append(key)
    return lsN
  except:
    return lsN
def getVals(js):
  lsN = []
  try:
    for key in js.values():
      lsN.append(key)
    return lsN
  except:
    return lsN
def pen(x,p):
  with open(p, 'w',encoding='UTF-8') as f:
    f.write(str(x))
    return p
def reader(x):
  with open(x, 'r',encoding='UTF-8') as f:
    return f.read()
def isLs(ls):
  if type(ls) is list:
    return True
  return False
def mkLs(ls):
  if isLs(ls) == False:
    ls = [ls]
  return ls
def exists(x):
    if isFile(x):
        return True
    return False
def reader(fi):
    with open(fi, 'r') as f:
        text = f.read()
        return text
def existJsRead(x,y):
    if exists(y) == False:
        pen(x,y)
    return jsIt(reader(y))
def jsRead(x):
    return jsIt(reader(x))
def existRead(x,y):
    if exists(y) == False:
        pen(str(x),y)
    return reader(y)
def existJsRead(x,y):
    if exists(str(y)) == False:
        pen(str(x),str(y))
    return jsRead(str(y))
def get_alph():
    alph = 'a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg,hh,ii,jj,kk,ll,mm,nn,oo,pp,qq,rr,ss,tt,uu,vv,ww,xx,yy,zz,aaa,bbb,ccc,ddd,eee,fff,ggg,hhh,iii,jjj,kkk,lll,mmm,nnn,ooo,ppp,qqq,rrr,sss,ttt,uuu,vvv,www,xxx,yyy,zzz'
    sp = alph.split(',')
    return sp
def quoteIt(st,ls):
    lsQ = ["'",'"']
    for i in range(0,len(ls)):
        for k in range(0,2):
            if lsQ[k]+ls[i] in st:
                st = st.replace(lsQ[k]+ls[i],ls[i])
            if ls[i]+lsQ[k] in st:
                st = st.replace(ls[i]+lsQ[k],ls[i])
        st = st.replace(ls[i],'"'+str(ls[i])+'"')
    return st
def jsIt(x):
    return json.loads(quoteIt(str(x),['False','None','True']).replace("'",'"'))
def find_it_alph(x,k):
    i = 0
    while str(x[i]) != str(k):
        i = i + 1
    return i
def eatInner(x,ls):
    for i in range(0,len(x)):
        if x[0] not in ls:
            return x
        x = x[1:]
    return ''
def eatOuter(x,ls):
    for i in range(0,len(x)):
        if x[-1] not in ls:
            return x
        x = x[:-1]
    return ''
def eatAll(x,ls):
    return eatOuter(eatInner(x,ls),ls)
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
        return str(x)
    if obj == 'bool':
        return bool(x)
    if obj == 'float':
        return float(x)
    if obj == 'map':
        return map(x)
    if obj == 'int':
        return int(str(x).split('.')[0])
    return x
def ifInJsWLs(ls,js,ls2):
    for i in range(0,len(ls)):
        if ls[i] in js:
            ls2[int(i)] = js[ls[int(i)]]
    return ls2
