"""Recenzja P05-R1, P5-02: progi okna DAQ_OK wobec dokładności 5V_SYS.
Model narożników identyczny z src/verify_electrical.py P05-R1 (rezystory 0,1 % + 25 ppm/K x 100 K,
referencja 0,1 %, Vos 5,5 mV, Ib 20 nA; wszystkie kombinacje znaków).
Zasilanie: TRACO TSR 2-2450, dokładność ustawienia +/-2 % (reference/TRACO_TSR2.txt z P01-R3),
5VA_P05 = 5V_SYS - I(R1) x 1 ohm. Uruchomienie: python okno_DAQ_OK.py
"""
import itertools

R = {'R3': 15e3, 'R4': 10e3, 'R5': 5.90e3, 'R6': 20e3, 'R7': 5.23e3, 'R8': 24.9e3}
tol = .001 + 25e-6 * 100; referr = .001; vos = .0055; ib = 20e-9


def par(a, b):
    return 1 / (1 / a + 1 / b)


def corner(top, bot):
    vals = []
    for e in itertools.product([-1, 1], repeat=6):
        rt, rb, tt, tb = [r * (1 + s * tol) for r, s in zip([R['R3'], R['R4'], top, bot], e[:4])]
        sense = rb / (rt + rb); ref = 2.5 * (1 + e[4] * referr) * tb / (tt + tb)
        err = vos + ib * (2 * par(rt, rb) + par(tt, tb))
        vals.append((ref + e[5] * err) / sense)
    return min(vals), max(vals)


def nominal(top, bot):
    return 2.5 * bot / (top + bot) * 2.5


print('R1:  prog dolny  %.4f V, naroza %.4f..%.4f V' % ((nominal(5.90e3, 20e3),) + corner(5.90e3, 20e3)))
print('R1:  prog gorny  %.4f V, naroza %.4f..%.4f V' % ((nominal(5.23e3, 24.9e3),) + corner(5.23e3, 24.9e3)))
print('R5 = 6,04k: prog dolny %.4f V, naroza %.4f..%.4f V' % ((nominal(6.04e3, 20e3),) + corner(6.04e3, 20e3)))
# I(R1) z karty AD7606B Rev. B (s. 7): AVCC 7,5/9,5 mA spoczynek, 8/10 mA przy 10 kSPS, 43/47,5 mA przy 800 kSPS;
# przy nadprobkowaniu x8 i 10 kSPS (80 kSPS wewnetrznie) ok. 11 mA; do tego LDO 3V3_DAQ ok. 4-6 mA i dzielnik R3/R4 0,2 mA.
# TSR 2-2450: ustawienie +/-2 %, wspolczynnik temperaturowy +/-0,02 %/K (przy 60 C: -0,7 %).
lo_now, lo_new = corner(5.90e3, 20e3)[1], corner(6.04e3, 20e3)[1]
for i_ma in (12, 20):
    for label, vsys in (('TSR -2 %, 25 C', 4.90), ('TSR -2 %, 60 C', 4.90 * (1 - 0.0002 * 35))):
        v = vsys - i_ma / 1e3
        print('I(R1) = %2d mA, %s: 5VA = %.3f V; zapas do gornego naroza progu: R1 %+.0f mV, R5 = 6,04k %+.0f mV'
              % (i_ma, label, v, (v - lo_now) * 1e3, (v - lo_new) * 1e3))
print('gorny prog: 5VA przy TSR +2 %% i 12 mA = %.3f V, zapas do dolnego naroza %.0f mV' % (5.10 - .012, (corner(5.23e3, 24.9e3)[0] - (5.10 - .012)) * 1e3))
# Gorny prog: TSR +2 % i dryft +0,7 % przy 60 C (znak wspolczynnika temperaturowego nieznany, liczony w obie strony).
hi_now, hi_new = corner(5.23e3, 24.9e3)[0], corner(5.11e3, 24.9e3)[0]
print('R7 = 5,11k: prog gorny %.4f V, naroza %.4f..%.4f V' % ((nominal(5.11e3, 24.9e3),) + corner(5.11e3, 24.9e3)))
for label, vsys in (('TSR +2 %, 25 C', 5.10), ('TSR +2 %, 60 C', 5.10 * (1 + 0.0002 * 35))):
    v = vsys - 0.012
    print('I(R1) = 12 mA, %s: 5VA = %.3f V; zapas do dolnego naroza progu gornego: R7 5,23k %+.0f mV, R7 = 5,11k %+.0f mV'
          % (label, v, (hi_now - v) * 1e3, (hi_new - v) * 1e3))
