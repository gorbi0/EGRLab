import re,json
class Atom(str):pass
def parse(t):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',t);i=0
 def read():
  nonlocal i
  v=tokens[i];i+=1
  if v=='(':
   out=[]
   while tokens[i]!=')':out.append(read())
   i+=1;return out
  return json.loads(v) if v.startswith('"') else Atom(v)
 return read()
def dump(v):
 if isinstance(v,list):return '('+' '.join(map(dump,v))+')'
 return str(v) if isinstance(v,Atom) else json.dumps(v,ensure_ascii=False)
def sub(v,key):return [x for x in v if isinstance(x,list) and x and x[0]==key]
def one(v,key):return next(x for x in v if isinstance(x,list) and x and x[0]==key)
