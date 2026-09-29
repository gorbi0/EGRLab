# R1 → R2 — decyzje i dowody

| Uwaga | Poprawka | Stan |
|---|---|---|
| R1-01: Q1 otwiera się przy szybkim VS mimo OFF | C5 220n→10n, C6 47n→1µ, R21 4k7→100k, R22 100k→470k, R27 47Ω→10Ω. Q2 PNP→P-MOS, D9 15V. | W CAD/BOM/modelu; rachunek tolerancji i SPICE; stara R1 odrzucona przez test. Do recenzji i pomiarów. |
| R1-02: start PSU maskuje hotplug | Oddzielna próba dołączenia ustalonego napięcia, rzeczywiste zbocze VS i prąd gałęzi Q1. | Nowa sekcja7 ODBIOR: przebiegi, kryteria, AUX OFF, bounce, precharge. Sprzęt niewykonany. |
| R1-03: niepewne PTH pod2,5mm² | J7 Ø2,4→3,2mm, pad5,2→6,0mm; raster7,62 i kotwy12,5 bez zmian. | Większy margines, nadal test rzeczywistej linki i kuponu. Przekrój nie określa średnicy wiązki drutów. |
| R1-04: brak mate BAT | EXT/J_BATA Phoenix1786174 IC2,5/2-ST-5,08 ↔1757019 na H_BAT. | Para potwierdzona na stronie producenta, dodana raz do BOM zewnętrznego. |

Opus prawidłowo wskazał kierunek zmiany C5/C6. Zestaw22n/680n przy ±5% i typowym
Crss dawał około0,835V przy24V wobec celu0,8V; przy48V zapas znikał. Większa C6
z małym Q2 wydłużałaby czas wyłączenia zależny od niegwarantowanego hFE.
R2 rozdziela ten kompromis: mała C5, duża C6, mocny zacisk i dobrane razem R21/R22.

Q2.1=OFF_BASE (historyczna nazwa, teraz bramka), Q2.2=OFF_COL, Q2.3=VS.
D9.K=VS, D9.A=OFF_BASE. Q4 pozostaje PNP EBC. Bez ENABLE R23 włącza Q2,
Q2 przez R27 podciąga GATE do VS. Z ENABLE Q4 wyłącza Q2.
Tab Q2=OFF_COL; nie łączyć z masą, VS ani innym radiatorem. Dla prądów bramki
Q2 nie wymaga radiatora; jego mocowanie i odstępy trzeba uwzględnić w placement.

Złącza zachowują numerację. OVP/UVLO/AUX/SAFE mają te same wartości i połączenia.
`design/changes.json` zawiera jawne zmiany elektryczne wobec zamrożonej bazy.
Nie zmieniano firmware ani innych PCB. P07 nadal HOLD.
