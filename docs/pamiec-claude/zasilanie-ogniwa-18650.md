---
name: zasilanie-ogniwa-18650
description: "Decyzja 29.09.2026: EGRLab zasilany z ogniw 18650 (rekomendacja 4S), P01 i HOLD P02 zbędne, zamówienie PCB P01/P02 wstrzymane; przyjęte tańsze zamienniki (EAO, PBV, C&K/NKK, DEUTSCH na panelu); CAD jeszcze niezmieniony"
metadata:
  node_type: memory
  type: project
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-29T05:30:34.846Z
---

29.09.2026 użytkownik zdecydował o zasilaniu przyrządu z Li-ion 18650. Ogniwa ładuje poza autem i wkłada naładowane do koszyka na zewnątrz obudowy. Zaproponował 4S. Ja popieram 4S: 12,0–16,8 V obejmuje zakres auta (12,4–14,5 V), a pakiet ma ok. 50 Wh, czyli ok. 15 h przy 3 W.

Nie trzeba przetwornicy podwyższającej. 5 V i 3,3 V dalej dają posiadane TSR 2-2450/2-2433; VMOTOR idzie wprost z pakietu przez bezpiecznik.

Sprawdzone pod 16,8 V: TSR do 36 V, VNH5019 do 24 V, dzielniki P05 (VPROT_SENSE do ok. 61 V, kanały silnika do ok. 41 V). Nie pasuje: 1.5KE18A (VWM 15,3 V).

**Skutki decyzji:**
- **P01 i HOLD w P02:** stają się zbędne. Powstanie nowa płytka zasilania: bezpiecznik, BMS 4S, P-MOSFET (SUP53P06 z zakupów P01) z UVLO ok. 12,4 V i PG zamiast diody D2, TSR, rozdział LV, VMOTOR.
- **Złącze PG do P04:** zostaje bez zmian (PG_SEND, PG_LINK, SAFE_N, 3V3_IO), dzięki czemu P04 się nie zmienia.
- **Akumulator auta:** zostaje tylko jako przewód pomiarowy VBAT. Do decyzji: czy CH7 P05 (dziś VPROT_SENSE) ma mierzyć VBAT auta.
- **Chłodzenie:** radiatory i blachy są niepotrzebne (MOSFET ok. 0,3 W przy 3,5 A).
- **Uwaga do blach, gdyby wróciły:** blaszka TO-220 przyłożona do zewnętrznej blachy robi z niej przewodnik pod +pakiet. Masa przyrządu łączy się z karoserią przez odniesienie TAPS i CAN.

**Zamówienie PCB:** P01 i P02 wstrzymane (baner w `Plytki/Zamowienie-Satland/INSTRUKCJA-SATLAND.md`). P00 i P04 można zamawiać.

**Zamienniki przyjęte przez użytkownika („wszystkie”):**
- EAO → zwykłe przyciski, stacyjka i grzybek (ok. 1000 zł → ok. 100 zł),
- PBV → bocznik 2512 Kelvin 5 mΩ (zmiana PCB P06),
- C&K 7201 (P05 SW1, zmiana footprintu) i NKK S6A (BYPASS, na panelu; musi przenieść prąd silnika) → zwykłe przełączniki,
- DEUTSCH tylko przy adapterach w komorze silnika, na panelu tańsze złącze z kluczem,
- przewody i dystanse kupowane lokalnie.

Listę zakupową 2 trzeba przeliczyć.

29.09 (później): użytkownik zatwierdził CH7 = VBAT auta i kondensator 2200 µF; TSR zostają (moduły z Allegro odrzucone dla szyn pomiarowych — P05 bierze AVCC z 5V_SYS przez 1 Ω). Specyfikacja `Plytki/P02-R4-specyfikacja/`: UVLO 13,47/12,47 V (Rt 43,2k, Rb 10k, Rh 536k), VSW ≤ 220 µF, C_H przez 22 Ω + diodę (jak bank R3), po PFAIL_N ≥ 14 ms przy 6 W; J13 PG przeniesione z P01 (Q7/Q8 SAFE_N, zwora PG_SEND–PG_LINK); PFAIL_N wymaga nowego wejścia w P03. Czeka na D-01…D-07.

29.09 (przerwane przed schematem): **poprawka** — jeden P-MOSFET nie da ochrony polaryzacji i wyłączania; są dwa SUP53P06 przeciwsobnie (Q_REV, Q_SW) + tor sterowania P01 R3 1:1 (Q_OFF itd.), 3 × SUP53P06 (wszystkie kupione). UVLO przeliczone: 1k + przełącznik PWR + 41,2k / 10k, R_iso 10k, Rh 464k z OK 0/5 V (AUX5 z LM2936 zasilanego z SW_COM i VLOG) → 13,53 / 12,51 V. Stan i mapa części: `Plytki/P02-R4-specyfikacja/STAN-PRAC.md`.

**Why:** użytkownik optymalizuje gabaryty i koszt; termin 23.10 przestał być ograniczeniem.
**How to apply:** nie wracać do zasilania z auta ani do banku HOLD bez nowej decyzji. Nowa płytka zasilania zastępuje P01 i P02, a interfejsy do P03/P04/P05/P07 muszą zostać zgodne. Zob. [[kaseta-r1]], [[pcb-fab-satland]], [[egrlab-purchasing-state]], [[p02-r1-state]].
