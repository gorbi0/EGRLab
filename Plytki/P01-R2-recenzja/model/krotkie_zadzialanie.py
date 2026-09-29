"""Krótkie zadziałanie OVP/INHIBIT: ENABLE opada na 50 us i wraca. Ile czasu brak VPROT?
Obciążenie: 220 uF + odbiornik stałej mocy (TSR-y za VPROT) 3 W, z wyłączeniem poniżej 6,5 V.
Talie: R2 = off_0.cir (wartości z XML R2), R1 = regression_R1_hot24.cir (wartości z XML R1)."""
import re
from spice import Spice
import pathlib
P = str(pathlib.Path(__file__).resolve().parents[2] / "P01-R2-review" / "simulation" / "decks") + "/"
def mk(fname, vt, bf, tr):
    d = open(P + fname, encoding="ascii").read()
    d = re.sub(r"^Vinput .*$", "Vinput input 0 14", d, flags=re.M)
    d = re.sub(r"^Venable .*$", "Venable p01_enable 0 PWL(0 2.7 5m 2.7 5.00001m 0 5.05m 0 5.05001m 2.7)", d, flags=re.M)
    d = re.sub(r"^Bload .*$", "Bload vprot 0 I=(v(vprot)>6.5)*3/max(v(vprot),6.5)", d, flags=re.M)
    d = re.sub(r"^\.model pm VDMOS\(pchan vto=-[\d.]+ kp=[\d.]+", f".model pm VDMOS(pchan vto=-{vt} kp=10", d, flags=re.M)
    d = re.sub(r"bf=\d+ (.*?)tr=[\de.-]+", lambda m: f"bf={bf} {m.group(1)}tr={tr}", d)
    d = re.sub(r"^\.tran .*$", ".tran 2e-06 0.2 0 2e-06", d, flags=re.M)
    return d
def first(t, y, cond, t0):
    for ti, yi in zip(t, y):
        if ti >= t0 and cond(yi): return ti
    return None
sim = Spice()
for label, fname in (("R1", "regression_R1_hot24.cir"), ("R2", "off_0.cir")):
    for vt, bf, tr in ((1, 50, 1e-6), (2, 50, 1e-6), (3, 30, 3e-6)):
        r = sim.run(mk(fname, vt, bf, tr), ["time", "v(p01_vs)", "v(p01_gate)", "v(vprot)"])
        t, vs, vg, vp = r["time"], r["v(p01_vs)"], r["v(p01_gate)"], r["v(vprot)"]
        vsg = [a - b for a, b in zip(vs, vg)]
        t_off = first(t, vsg, lambda v: v < vt, 5e-3)
        t_on = first(t, vsg, lambda v: v > vt + 0.5, (t_off or 5e-3) + 1e-6)
        vmin = min(v for ti, v in zip(t, vp) if ti > 5e-3)
        t_low = first(t, vp, lambda v: v < 6.5, 5e-3)
        t_back = first(t, vp, lambda v: v > 0.95*14, (t_low or 5e-3) + 1e-6) if t_low else None
        gap = f"VPROT < 6,5 V (TSR stop) od {1e3*(t_low-5e-3):5.1f} ms do {1e3*(t_back-5e-3) if t_back else float('nan'):5.1f} ms" if t_low else "VPROT nie spada poniżej 6,5 V"
        print(f"{label} Vt={vt} V BF={bf} TR={tr*1e6:.0f}us: Q1 wył. przez {1e3*((t_on or t[-1])-(t_off or 5e-3)):6.2f} ms, VPROT min {vmin:5.2f} V; {gap}")
