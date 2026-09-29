"""Porównanie: ENABLE jako idealne źródło (model autora R2) vs rzeczywisty tor OK→R14→D7/D8→Q6→ENABLE
z R16 i trzema bazami (Q3, Q5, Q8) wiszącymi na ENABLE. Talie bazowe: off_0.cir / off_1.cir z pakietu R2."""
import re, sys
from spice import Spice
import pathlib
P = str(pathlib.Path(__file__).resolve().parents[2] / "P01-R2-review" / "simulation" / "decks") + "/"
REAL = """VAUX aux5 0 5
V33 v33 0 3.3
R13 aux5 ok 2200
S1 ok 0 cmp_ctl 0 swmod
Vcmp cmp_ctl 0 PWL(0 0 50u 0 50.05u 1)
.model swmod SW(vt=0.5 vh=0.1 ron=30 roff=1e9)
R8 ok ovref 220000
Vovref ovref 0 2.5
R11 ok uvs 249000
Vuvs uvs 0 3.6
R14 ok bufd1 4700
D7 bufd1 bufd2 d4148
D8 bufd2 bufbase d4148
R15 bufbase 0 100000
Q6 aux5 bufbase p01_enable npm
R16 p01_enable 0 10000
R32 p01_enable q8b 10000
R33 q8b 0 47000
Q8 faultb q8b 0 npm
R30 v33 faultb 10000
R31 faultb 0 100000
Q7 safen faultb 0 npm
Rsafepu v33 safen 10000
Rsafepd safen 0 100000
.model d4148 D(is=2.52n n=1.752 rs=0.568 cjo=4p tt=20n bv=100)
"""
def first(t, y, cond, t0):
    for ti, yi in zip(t, y):
        if ti >= t0 and cond(yi): return (ti - t0)*1e6
    return None
sim = Spice()
for corner in ("off_0", "off_1"):
    base = open(P + corner + ".cir", encoding="ascii").read()
    ideal = base
    real = re.sub(r"^Venable .*$", REAL.strip(), base, flags=re.M)
    real = real.replace(".tran 1e-07 0.0003 0 1e-07", ".tran 5e-08 0.0004 0 5e-08")
    ideal = ideal.replace(".tran 1e-07 0.0003 0 1e-07", ".tran 5e-08 0.0004 0 5e-08")
    vi = ["time", "v(p01_vs)", "v(p01_gate)", "v(p01_enable)", "v(p01_off_base)", "v(p01_release_base)"]
    a = sim.run(ideal, vi)
    b = sim.run(real, vi + ["v(ok)", "v(safen)", "v(p01_on_base)"])
    for name, r in (("ENABLE idealne (autor)", a), ("tor rzeczywisty OK→Q6→ENABLE", b)):
        t = r["time"]; vsg = [s - g for s, g in zip(r["v(p01_vs)"], r["v(p01_gate)"])]
        q2on = [s - ob for s, ob in zip(r["v(p01_vs)"], r["v(p01_off_base)"])]
        t0 = 50e-6
        e1 = first(t, r["v(p01_enable)"], lambda v: v < 1.0, t0)
        e03 = first(t, r["v(p01_enable)"], lambda v: v < 0.3, t0)
        q5 = first(t, r["v(p01_release_base)"], lambda v: v < 0.4, t0)
        q2 = first(t, q2on, lambda v: v > 3.0, t0)
        g = first(t, vsg, lambda v: v < 0.5, t0)
        shelf = [v for ti, v in zip(t, r["v(p01_enable)"]) if t0 + 2e-6 <= ti <= t0 + 4e-6]
        extra = ""
        if "v(safen)" in r:
            sn = first(t, r["v(safen)"], lambda v: v < 0.8, t0)
            extra = f", SAFE_N<0,8 V po {sn:5.1f} us" if sn is not None else ", SAFE_N: brak"
        print(f"{corner} | {name:30s}: ENABLE<1 V {e1:5.2f} us, <0,3 V {e03 if e03 is None else round(e03,1)} us,"
              f" ENABLE 2-4 us po zboczu ~{sum(shelf)/max(len(shelf),1):.2f} V, baza Q5<0,4 V {q5 and round(q5,1)} us,"
              f" Q2 VGS<-3 V {q2 and round(q2,1)} us, VSG(Q1)<0,5 V {g and round(g,1)} us{extra}")
