"""Model węzła bramki Q1 w P01 PROTECT (P01-R1-review) — dowód do uwagi R1-01.

Uruchomienie:  python model_bramki_Q1.py      (tylko biblioteka standardowa, kilka minut)

Model uproszczony, do PORÓWNANIA wariantów, nie jako gwarancja:
- Q1 SUP53P06-20: P-MOS kwadratowy, Vt = 2,0 V (katalog 1..3 V; sprawdzane też 1,0 V),
  K = 3,125 A/V^2 (20 mOhm przy VSG = 10 V), Ciss ~3 nF, Crss ~0,4 nF.
- Q2 2N5401 + R27: źródło prądu do VS, ograniczone beta*IB, IB = (VS-0,7)/R23, beta = 60,
  bez opóźnienia załączenia (optymistycznie dla projektu).
- Q3 + R21: pull-down bramki do ~0,1 V. R22 = 100 k G-S. D4 BZX55C15 jako zacisk 15 V / 0,7 V.
- Obciążenie VPROT: 220 uF || 50 Ohm (limit pojemności z dokumentacji P01).
- Nie modeluje czasów magazynowania Q4/Q5/Q6/Q8 ani komparatora — dodają się jednakowo
  w obu wariantach. Liczby potwierdza dopiero ODBIOR na stole.
"""

K_Q1, CISS, CRSS = 3.125, 3e-9, 0.4e-9
C_LOAD, R_LOAD = 220e-6, 50.0
BETA_Q2, R23 = 60, 2200.0


def _id(vsg, vsd, vt):
    if vsg > vt and vsd > 0:
        ov = vsg - vt
        return K_Q1*ov*ov if vsd >= ov else K_Q1*(2*ov*vsd - vsd*vsd)
    return 0.0


def _i_gate(VS, VG, R21, R27, q2_on, q3_on):
    """Prądy rezystancyjne wpływające do bramki."""
    i = (VS - VG)/100e3                                             # R22
    if q2_on and VS > 0.7:
        i += min(BETA_Q2*(VS - 0.7)/R23, max(0.0, (VS - 0.1 - VG)/R27))
    if q3_on:
        i -= max(0.0, (VG - 0.1)/R21)
    if VS - VG > 15:
        i += (VS - VG - 15)/1.0                                     # D4 zener
    if VG - VS > 0.7:
        i -= (VG - VS - 0.7)/1.0                                    # D4 w kierunku przewodzenia
    return i


def sim_idealne(p, tr, V0=0.0, V1=14.0, VP0=0.0, VG0=None, q2_on=True, q3_on=False,
                Tend=None, vt=2.0, rc5=0.0, pomiar_wyl=False):
    """VS wymuszone rampą (źródło idealne). rc5 > 0: rezystor szeregowo z C5 (wariant odrzucony)."""
    C5, C6, R21, R27 = p
    Cgs = C6 + CISS
    VS, VG, VP = V0, (V0 if VG0 is None else VG0), VP0
    VC5 = VP0 if rc5 > 0 else None
    t, Tend = 0.0, (Tend or max(20*tr, 2e-3))
    w = dict(Ipk=0.0, VSGmax=0.0, VPmax=VP, VPend=VP, t2=None, t05=None)
    while t < Tend:
        dt = 2e-9 if t < 3*tr + 30e-6 else 50e-9
        VSn = V0 + (V1 - V0)*min((t + dt)/tr, 1.0)
        dVS = (VSn - VS)/dt
        Id = _id(VS - VG, VS - VP, vt)
        dVP = (Id - VP/R_LOAD)/C_LOAD
        i = _i_gate(VS, VG, R21, R27, q2_on, q3_on)
        if rc5 > 0:
            iR = (VG - VC5)/rc5
            i -= iR
            VC5 += (dVP + iR/C5)*dt
            dVG = (i + Cgs*dVS + CRSS*dVP)/(Cgs + CRSS)
        else:
            Cgd = C5 + CRSS
            dVG = (i + Cgs*dVS + Cgd*dVP)/(Cgs + Cgd)
        VG += dVG*dt; VP += dVP*dt; VS = VSn; t += dt
        w['Ipk'] = max(w['Ipk'], Id); w['VSGmax'] = max(w['VSGmax'], VS - VG)
        w['VPmax'] = max(w['VPmax'], VP); w['VPend'] = VP
        if pomiar_wyl:
            if w['t2'] is None and VS - VG < 2.0: w['t2'] = t
            if w['t05'] is None and VS - VG < 0.5: w['t05'] = t; break
    return w


def sim_wiazka(p, tr, V1=14.0, Rs=0.05, C1=10e-6, vt=2.0):
    """Wpięcie zasilania: rampa źródła przez Rs (wiązka + D2) do węzła VS z C1; Q1 ma być OFF."""
    C5, C6, R21, R27 = p
    Cgs, Cgd = C6 + CISS, C5 + CRSS
    VS = VG = VP = 0.0; t = 0.0; E = 0.0
    w = dict(Ipk=0.0, VSGmax=0.0, VPmax=0.0)
    while t < 40*tr + 100e-6:
        dt = 1e-9 if t < 3*tr + 30e-6 else 20e-9
        Vsrc = V1*min((t + dt)/tr, 1.0)
        Id = _id(VS - VG, VS - VP, vt)
        dVS = ((Vsrc - VS)/Rs - Id)/C1
        dVP = (Id - VP/R_LOAD)/C_LOAD
        i = _i_gate(VS, VG, R21, R27, True, False)
        dVG = (i + Cgs*dVS + Cgd*dVP)/(Cgs + Cgd)
        E += Id*max(VS - VP, 0.0)*dt
        VG += dVG*dt; VP += dVP*dt; VS += dVS*dt; t += dt
        w['Ipk'] = max(w['Ipk'], Id); w['VSGmax'] = max(w['VSGmax'], VS - VG)
        w['VPmax'] = max(w['VPmax'], VP)
    w['E_mJ'] = E*1e3
    return w


def wylaczenie(p, VS=18.5):
    C5, C6, R21, R27 = p
    vsg0 = VS*100e3/(100e3 + R21)                                   # ustalony VSG w stanie ON
    return sim_idealne(p, 1e-9, V0=VS, V1=VS, VP0=VS - 0.05, VG0=VS - vsg0,
                       q2_on=True, q3_on=False, Tend=2e-3, pomiar_wyl=True)


def start(p, rc5=0.0):
    return sim_idealne(p, 1e-9, V0=14, V1=14, VP0=0.0, q2_on=False, q3_on=True,
                       Tend=40e-3, rc5=rc5)


WARIANTY = {
    "R1 obecny   C5=220n C6=47n  R21=4k7 R27=47": (220e-9, 47e-9, 4700.0, 47.0),
    "poprawka    C5=22n  C6=680n R21=47k R27=33": (22e-9, 680e-9, 47000.0, 33.0),
}

if __name__ == "__main__":
    for nazwa, p in WARIANTY.items():
        C5, C6, R21, R27 = p
        print(f"=== {nazwa}   (VSG z samego dzielnika C5/C6 przy skoku 24 V: {24*C5/(C5+C6+CISS):.2f} V)")
        print("  A) wpięcie zasilania, Q1 ma być OFF (Rs = 50 mOhm, C1 = 10 uF):")
        for V1 in (14.0, 24.0):
            for tr in (1e-6, 10e-6):
                w = sim_wiazka(p, tr, V1=V1)
                print(f"     0->{V1:.0f} V, zbocze {tr*1e6:3.0f} us: Id szczyt {w['Ipk']:6.1f} A, VSG max {w['VSGmax']:5.2f} V,"
                      f" VPROT max {w['VPmax']:5.2f} V, energia w Q1 {w['E_mJ']:6.2f} mJ")
        w = sim_wiazka(p, 1e-6, V1=24.0, vt=1.0)
        print(f"     najgorszy Vt = 1,0 V, 0->24 V / 1 us: Id szczyt {w['Ipk']:6.1f} A, VSG max {w['VSGmax']:5.2f} V")
        print("  B) stan OVP-OFF: VS 18 V, VPROT 17 V, skok VS do 30 V (źródło idealne):")
        for tr in (1e-6, 10e-6):
            w = sim_idealne(p, tr, V0=18, V1=30, VP0=17)
            print(f"     zbocze {tr*1e6:3.0f} us: Id szczyt {w['Ipk']:6.1f} A, VPROT max {w['VPmax']:5.2f} V")
        w = start(p)
        print(f"  C) normalny start przy 14 V do 220 uF: prąd szczytowy {w['Ipk']:.2f} A, VPROT końcowe {w['VPend']:.2f} V")
        w = wylaczenie(p)
        iq2 = min(BETA_Q2*(18.5 - 0.7)/R23, 18.5*100e3/(100e3 + R21)/R27)
        print(f"  D) wyłączenie OVP przy 18,5 V: |VGS| < 2 V po {w['t2']*1e6:5.1f} us, < 0,5 V po {w['t05']*1e6:5.1f} us,"
              f" szczyt Q2 ~{iq2*1e3:.0f} mA")
        print()
    print("=== wariant ODRZUCONY: rezystor szeregowo z C5 (C5=220n, C6=47n, R21=4k7)")
    p = WARIANTY["R1 obecny   C5=220n C6=47n  R21=4k7 R27=47"]
    for rc5 in (1000.0, 2200.0, 4700.0):
        w = start(p, rc5=rc5)
        print(f"  R szer. = {rc5:5.0f} Ohm: normalny start, prąd szczytowy {w['Ipk']:5.1f} A (obecny projekt: patrz C)")
