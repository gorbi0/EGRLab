"""Wspólny wrapper ngspice (DLL z KiCad 10): ustaw ścieżkę DLL w Spice(dll=...), jeśli inna."""
"""Minimalny wrapper shared-ngspice (DLL z KiCad) bez numpy."""
import ctypes as C, os
class Vec(C.Structure):
    _fields_=[('name',C.c_char_p),('type',C.c_int),('flags',C.c_short),
              ('real',C.POINTER(C.c_double)),('complex',C.c_void_p),('length',C.c_int)]
class Spice:
    def __init__(self, dll=r"C:\Program Files\KiCad\10.0\bin\ngspice.dll"):
        self.cookie = os.add_dll_directory(os.path.dirname(dll))
        self.lib = C.CDLL(dll); self.msg = []
        cb = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
        self.cb = cb(lambda s,i,p: self.msg.append(s.decode(errors='replace')) or 0)
        self.lib.ngSpice_Init(self.cb, None, None, None, None, None, None)
        self.lib.ngSpice_Command.argtypes = [C.c_char_p]
        self.lib.ngSpice_Circ.argtypes = [C.POINTER(C.c_char_p)]
        self.lib.ngGet_Vec_Info.argtypes = [C.c_char_p]
        self.lib.ngGet_Vec_Info.restype = C.POINTER(Vec)
    def run(self, deck, vectors):
        self.lib.ngSpice_Command(b'destroy all'); self.msg = []
        lines = deck.splitlines()
        arr = (C.c_char_p*(len(lines)+1))(*[s.encode() for s in lines], None)
        if self.lib.ngSpice_Circ(arr): raise RuntimeError(self.msg[-20:])
        self.lib.ngSpice_Command(b'run')
        bad = [m for m in self.msg if 'Error' in m or 'aborted' in m or 'singular' in m.lower()]
        if bad: raise RuntimeError(bad[-10:])
        out = {}
        for n in vectors:
            v = self.lib.ngGet_Vec_Info(n.encode())
            if not v or not v.contents.length: raise RuntimeError(('brak wektora', n, self.msg[-10:]))
            out[n] = [v.contents.real[i] for i in range(v.contents.length)]
        return out
if __name__ == '__main__':
    s = Spice(); r = s.run('t\nV1 in 0 pulse(0 1 1u 1n 1n 10u 20u)\nR1 in out 1k\nC1 out 0 1n\n.tran 10n 5u\n.end', ['time','v(out)'])
    print(len(r['time']), r['v(out)'][-1])
