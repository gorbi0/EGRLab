---
name: p05-r1-review
description: "P05 DAQ (AD7606B): R1 Astry 25.09 → moja recenzja 27–28.09 (P5-01…09); przed PCB: odsprzęganie U1 + DOUT pod U1, okno DAQ_OK (R5 6,04k, R7 5,11k); karta AD7606B Rev. B w recenzji/zrodla"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-27T16:27:20.552Z
---

P05-R1 (Astra, 25.09; `Plytki/P05-R1-review`, 151 plików, pakiet nietknięty). Moja recenzja 27.09: `Plytki/P05-R1-recenzja/RECENZJA-P05-R1.md` + `skrypty/` (odsprzęganie U1, sąsiedztwo analog/cyfra, masy U1, okno DAQ_OK, model zwarcia 5V, suma pojemności 5 V) + `dowody/`.

Ustalenia: logika DAQ_OK (okno TLV1702 + ADR4525, MCP120-300/-450), MEAS_PERMIT = MEAS_EN ∧ DAQ_OK, bufory LVC125 Ioff, G6K (+ pin 1, COM 3/6, NO 4/5), TBD62083 poprawne; świeże ERC 0 / DRC 0/0/0.
- **P5-01 (przed PCB):** C5–C7, C9–C13 przy prawej stronie AD7606B 7–21 mm drogi od pinów (REFCAP C13 12 mm, REFIN/OUT 14–21 mm), obok wolne miejsce; `verify_pcb` ma tylko „≤15 mm”.
- **P5-02 (przed PCB):** okno 4,826/5,165 V (narożniki ±48 mV) vs TSR 2-2450 ±2 % i ±0,02 %/K; I(R1) z karty 12–20 mA (AD7606B AVCC 8–11 mA); przy 60 °C zapas −28…−6 mV → R5 6,04k (4,800 V) i R7 5,11k (5,186 V), narożniki 4,753/5,234 wciąż w 4,75–5,25; odbiór: 5V_SYS 4,93–5,07 V w 23 °C.
- P5-03 przekaźniki w upale (katalog 80 %@23°C ×1,13 → 4,5 V przy 60°C) — próba w ODBIOR (≤3,9 V przy 23°C); P5-05 R13 10k→47k (zasilanie wsteczne 0,30 V); P5-06 opcja 1N5817 3V3_DAQ→5VA (bez: 0,58 V przy zwarciu); P5-07 5V_SYS ≈538 µF z 600 µF TSR; P5-08 dokumenty (w rejestrze zakupów TSW-108-07 zamiast -08-NA).
- **P5-04 zamknięte 28.09:** użytkownik dał kartę AD7606B Rev. B (`Plytki/P05-R1-recenzja/zrodla/AD7606B-RevB.pdf`): 64/64 piny OK (WR bez funkcji w trybie szeregowym, DOUTB/C/D „leave unconnected”, N/A do AGND); REFIN/REFOUT — karta niespójna (tab. 9: 100 nF, rozdz. Reference: 10 µF przy referencji wewn.), P05 ma oba. Też: pod U1 biegnie DOUT po B.Cu (P5-01), rejestry CHx_OFFSET ±128 LSB i gain ≤65 kΩ nie wystarczą → kalibracja w firmware. URL analog.com nie działa w WebFetch ani w przeglądarce (wymusza pobranie).

**P05 R2 (29.09):** schemat w chmurze (PR #3, scalony 37bd3e3): R5 6,04k, R7 5,11k, R13 47k, U2 REF5025ID (klasa wysoka), CH7 VBAT_SENSE, arkusze AUX_IN/ZLACZA; ERC 0, 421/421, 23/23, 12/12. Layout przejdzie do formatu S1; wzór odsprzęgania U1 w `Plytki/P05-R2-review/wip-layout-obrys-R1/`. SW1 nadal C&K w schemacie — zamiennik E-Switch 100DP1T1B1M2REH do wpisania przy S1.

**Why:** schemat pracy Claude ↔ Astra ([[user-pcb-background]]); zasady recenzji [[egrlab-review-rules]].
**How to apply:** R2 P05: najpierw wartości (R5, R7, R13), potem przestawienie odsprzęgania i DOUT przy U1. Karta AD7606B jest lokalnie w folderze recenzji — nie pobierać ponownie. Zob. [[p03-r1-state]] (B2B), [[p02-r1-state]] (TSR 2-2450).
