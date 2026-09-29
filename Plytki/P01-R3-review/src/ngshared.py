"""Minimal synchronous shared-ngspice wrapper. Public API: sharedspice.h.
Every requested vector must exist and contain data. Circuit options are explicit.
"""
from pathlib import Path
import ctypes as C,os
import numpy as np
class Vec(C.Structure):
 _fields_=[('name',C.c_char_p),('type',C.c_int),('flags',C.c_short),('real',C.POINTER(C.c_double)),('complex',C.c_void_p),('length',C.c_int)]
class Spice:
 def __init__(self):
  default=Path(__file__).resolve().parents[2]/'.egrlab-toolchains/kicad/runtime/bin/ngspice.dll'
  dll=Path(os.environ.get('NGSPICE_LIBRARY',str(default)))
  self.cookie=os.add_dll_directory(str(dll.parent)) if os.name=='nt' else None
  self.lib=C.CDLL(str(dll));self.messages=[]
  cb=C.CFUNCTYPE(C.c_int,C.c_char_p,C.c_int,C.c_void_p)
  self.cb=cb(lambda s,i,p:self.messages.append(s.decode(errors='replace')) or 0)
  self.lib.ngSpice_Init(self.cb,None,None,None,None,None,None)
  self.lib.ngSpice_Command.argtypes=[C.c_char_p]
  self.lib.ngSpice_Circ.argtypes=[C.POINTER(C.c_char_p)]
  self.lib.ngGet_Vec_Info.argtypes=[C.c_char_p];self.lib.ngGet_Vec_Info.restype=C.POINTER(Vec)
 def cmd(self,s):
  result=self.lib.ngSpice_Command(s.encode())
  if result:raise RuntimeError((s,result,self.messages[-15:]))
 def run(self,deck,vectors):
  self.cmd('destroy all');self.messages=[]
  lines=deck.splitlines();arr=(C.c_char_p*(len(lines)+1))(*[s.encode() for s in lines],None)
  rc=self.lib.ngSpice_Circ(arr)
  if rc:raise RuntimeError(self.messages)
  self.cmd('run')
  if any('Error:' in s or 'run simulation(s) aborted' in s for s in self.messages):raise RuntimeError(self.messages[-30:])
  out={}
  for name in vectors:
   v=self.lib.ngGet_Vec_Info(name.encode())
   if not v or not v.contents.length or not v.contents.real:raise RuntimeError(('missing vector',name,self.messages[-20:]))
   out[name]=np.ctypeslib.as_array(v.contents.real,shape=(v.contents.length,)).copy()
  return out
if __name__=='__main__':
 s=Spice();v=s.run('test\nV1 in 0 pulse(0 1 1u 1n 1n 10u 20u)\nR1 in out 1k\nC1 out 0 1n\n.tran 10n 5u\n.end',['time','v(out)']);print(len(v['time']),v['v(out)'][-1])
