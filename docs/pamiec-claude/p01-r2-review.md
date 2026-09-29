---
name: p01-r2-review
description: P01-R2 review (2026-09-23) outcome — no schematic blocker; two pre-layout decisions (restart dropout, measurability)
metadata:
  type: project
---

P01-R2-review recenzja 2026-09-23 (`P01-R2-recenzja/RECENZJA-P01-R2.md`, dowody SPICE w `model/`, ngspice.dll z KiCad 10 przez ctypes, bez numpy): R2 zmienił bramkę Q1 na C5=10n, C6=1µ, R21=100k, R22=470k, R27=10Ω, Q2 = P-MOS SUP53P06-20 + D9 15 V. R1-01 naprawione (0,595 V przy 48 V/1 µs, powtórzone). Brak błędu blokującego w schemacie.

Otwarte decyzje przed layoutem: R2-01 — każde zadziałanie OVP/UVLO/INHIBIT ≥ ~50 µs zdejmuje VPROT na 10–27 ms (R1: 0,1–0,3 ms) → restart CORE; nieodłączne dla C6/C5≥60 i łagodnego startu; rekomendacja: przyjąć i opisać. R2-02 — kryteria ODBIOR 7 (VGS ≤0,1 V, ładunek gałęzi Q1) niemierzalne bez sondy różnicowej/prądowej; propozycja: ΔVPROT jako PASS, DHO804 pływający na power banku z masą na TP1. Drobne: złącze BAT męskie po stronie akumulatora (zamienić), C6 w TME tylko hurtowo, J7 szprychy/TP przy Q1.

**Why:** Kolejne rewizje P01 będą recenzowane; ustalenia R2 mają nie wracać jako „nowe”.

**How to apply:** Przy P01-R3 sprawdź decyzje R2-01/R2-02 i czy ODBIOR ma kryterium ΔVPROT. Zob. [[p01-r1-gate-coupling]], [[egrlab-review-rules]].
