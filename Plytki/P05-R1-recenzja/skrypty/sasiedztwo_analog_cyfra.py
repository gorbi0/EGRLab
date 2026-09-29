import pcbnew as p, math, collections, re
b = p.LoadBoard('eda/P05.kicad_pcb')
def n(t): return t.GetNetname().split('/')[-1]
ANALOG = re.compile(r'^(ADC_CH\d|TAP_P\d|VPROT_SENSE|AUX_IN|AUX_HI|AUX_LO|AUX_SHUNT|ADC_REF|REFCAP|REGCAP_A|REGCAP_D)$')
DIGITAL = re.compile(r'^(ADC_SCLK.*|ADC_CS.*|ADC_SDI.*|ADC_CONVST.*|ADC_RESET.*|AD_BUSY_LOCAL|BUSY_SER|ADC_BUSY|AD_DOUT_LOCAL|DOUT_SER|ADC_DOUTA|MEAS_EN.*|MEAS_PERMIT|MEAS_COIL_LOW|DAQ_OK.*|DAQ_.*)$')
segs = [(n(t), t.GetLayer(), (p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y)), (p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y)), p.ToMM(t.GetWidth()))
        for t in b.GetTracks() if not isinstance(t, p.PCB_VIA)]
def dseg(q, a, c):
    ax, ay = a; cx, cy = c; dx, dy = cx - ax, cy - ay; L = dx*dx + dy*dy
    t = 0 if L == 0 else max(0, min(1, ((q[0]-ax)*dx + (q[1]-ay)*dy) / L))
    return math.dist(q, (ax + t*dx, ay + t*dy))
res = collections.defaultdict(lambda: collections.defaultdict(float))
dig = [s for s in segs if DIGITAL.match(s[0])]
for na, L, a, c, w in segs:
    if not ANALOG.match(na): continue
    length = math.dist(a, c); k = max(1, int(length / 0.2))
    for i in range(k):
        q = (a[0] + (c[0]-a[0]) * (i+.5)/k, a[1] + (c[1]-a[1]) * (i+.5)/k)
        best = None
        for nd, Ld, ad, cd, wd in dig:
            if Ld != L: continue
            d = dseg(q, ad, cd) - (w + wd) / 2  # edge to edge
            if d < 0.6 and (best is None or d < best[1]): best = (nd, d)
        if best: res[na][best[0]] += length / k
for na in sorted(res):
    print(na, {k: round(v, 1) for k, v in sorted(res[na].items(), key=lambda x: -x[1])})
# total analog length per net
tot = collections.defaultdict(float)
for na, L, a, c, w in segs:
    if ANALOG.match(na): tot[(na, 'F' if L == p.F_Cu else 'B')] += math.dist(a, c)
print({f'{k[0]}:{k[1]}': round(v, 1) for k, v in sorted(tot.items())})
