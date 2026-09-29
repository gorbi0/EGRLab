from spice import Spice
import pathlib
P = str(pathlib.Path(__file__).resolve().parents[2] / "P01-R2-review" / "simulation" / "decks") + "/"
sim = Spice()
for name, off_at in (("hot_48_1e-06_1", None), ("off_1", 50e-6), ("start_slow_corner", None), ("ovp_17_24_delay20us", 50.2143e-6)):
    d = open(P + name + ".cir", encoding="ascii").read()
    r = sim.run(d, ["time", "v(p01_vs)", "v(p01_gate)", "v(vprot)", "i(vq1i)"])
    t, vs, vg, vp, i = r["time"], r["v(p01_vs)"], r["v(p01_gate)"], r["v(vprot)"], r["i(vq1i)"]
    t0m = 50e-6 if name.startswith(("off", "ovp")) else 0.0
    vsg = [a - b for a, b in zip(vs, vg)]
    pk_vsg = max(v for ti, v in zip(t, vsg) if ti >= t0m); pk_i = max(x for ti, x in zip(t, i) if ti >= t0m)
    off = None
    if off_at is not None:
        off = next(((ti - off_at)*1e6 for ti, v in zip(t, vsg) if ti >= off_at and v < 0.5), None)
    s95 = next(((ti - 1e-3)*1e3 for ti, a, b in zip(t, vs, vp) if ti >= 1e-3 and a > 5 and b >= 0.95*a), None) if name.startswith("start") else None
    print(f"{name:22s} VSG szczyt {pk_vsg:7.3f} V, Id szczyt {pk_i:7.3f} A, wyłączenie {off and round(off,2)} us, start 95% {s95 and round(s95,1)} ms")
