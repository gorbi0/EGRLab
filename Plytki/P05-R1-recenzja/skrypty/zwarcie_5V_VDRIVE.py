"""Recenzja P05-R1, P5-06: VDRIVE - AVCC przy twardym zwarciu 5V_SYS do GND (pytanie 2 z docs/DLA-RECENZENTA.md).
Model uproszczony (Euler, krok 0,1 us), zalozenia jawne:
- C1 470 uF rozladowuje sie przez R1 1 ohm do zwarcia; AD7606B pobiera 20 mA z AVCC (proporcjonalnie ponizej 2 V);
- 3V3_DAQ: ok. 3 uF (C3 2,2 uF + 7 x 100 nF), obciazenie ok. 470 ohm (R2 1k + logika);
- MCP1700: reguluje 3,3 V przy VIN >= 3,31 V; przy 2,3 V <= VIN < 3,31 V tranzystor w pelni otwarty (ok. 1 ohm, w obie strony);
  ponizej 2,3 V (minimalne VIN z karty) wylaczony, zostaje dioda podlozowa VOUT -> VIN (ok. 0,6 V przy 10 mA).
  Karta MCP1700 (DS20001826F) nie opisuje ochrony przed pradem wstecznym.
- Opcja: dioda Schottky 3V3_DAQ (anoda) -> 5VA_P05 (katoda): BAT85 (0,30 V przy 1 mA) albo 1N5817 (ok. 0,20 V przy 10 mA).
Wynik to rzad wielkosci, nie zamiennik pomiaru.
"""
import math


def sim(Is=0.0, nvt=0.03, C1=470e-6, R1=1.0, C3=3.0e-6, Rl3=470.0, I_adc=0.020, dt=1e-7, T=20e-3):
    va, v3, t, q = 4.97, 3.30, 0.0, 0.0
    worst = (-9.0, 0.0, 0.0, 0.0)
    while t < T:
        if va >= 3.31:
            i_ldo = max(v3 / Rl3 + (3.3 - v3) / 0.5, 0.0)
        elif va >= 2.3:
            i_ldo = (va - v3) / 1.0
        else:
            d = v3 - va; i_ldo = -(1e-12 * (math.exp(d / 0.026) - 1)) if d > 0 else 0.0
        d = v3 - va; i_s = Is * (math.exp(d / nvt) - 1) if (Is and d > 0) else 0.0
        i_adc = I_adc * min(1.0, va / 2.0)
        va += (-va / R1 - i_adc - max(i_ldo, 0) + max(-i_ldo, 0) + i_s) / C1 * dt
        v3 += (i_ldo - v3 / Rl3 - i_s) / C3 * dt
        t += dt; q += i_s * dt
        if v3 - va > worst[0]:
            worst = (v3 - va, t, va, v3)
    return worst, q


for name, Is, nvt in (('bez diody', 0.0, 0.03), ('BAT85', 1.9e-7, 0.035), ('1N5817', 1.27e-5, 0.030)):
    (w, t, va, v3), q = sim(Is, nvt)
    print(f'{name:10}: max VDRIVE - AVCC = {w:.2f} V po {t * 1e3:.2f} ms (AVCC {va:.2f} V, VDRIVE {v3:.2f} V); ladunek przez diode {q * 1e6:.1f} uC')
