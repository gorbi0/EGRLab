# M1-PCB-R1 — paczka z warstwami pasty (szablon SMT)

*9.10.2026.* `DO-ZAMOWIENIA_M1-PCB-R1-z-pasta.zip` = ZIP z `M1-PCB-R1-zamowienie` (sha256 824058fb…) **bajtowo bez zmian** + dwie warstwy pasty wyeksportowane z tego samego `projekt/eda/M1.kicad_pcb` (KiCad 10.0.6, precyzja 6, bez makr apertur):

| Plik | Pola | Części |
|---|---:|---|
| `M1-F_Paste.gtp` | 237 | wszystkie SMD na górze (C, R, D1, RSH1, U3–U8), także DNP R25 / R27 |
| `M1-B_Paste.gbp` | 8 | C8, C9, C10, C13 (spód, pod AD7606B) |

Pola przewodów, punkty pomiarowe, THT (TSR, oprawka F1, moduły) — bez pasty. Kontrola: 11 plików paczki identycznych, liczby pól zgodne z listą części SMD, obrys zgodny z paczką.

JLCPCB: SMT-Stencil → **Top** (spód — 4 kondensatory — lutownicą po rozpływie góry), stencil bez ramki wystarcza do ręcznego nakładania. Na DNP R25 / R27 przykleić taśmę na otwory albo zdjąć pastę po nałożeniu.
