# EGRLab P03-R4 — CORE (bufor Schmitta w resecie do P04)

27.09.2026 · R4 na podstawie zamykającego R3, po decyzji użytkownika w sprawie uwagi P3-01 z końcowej recenzji R2. Pakiety R1–R3 pozostają bez zmian. **Status: pliki gotowe do recenzji layoutu przy J4. Poza obszarem zmiany miedź identyczna z R3. Przekrój B2B P03–P05, przymiarka i odbiór sprzętu NIE ZBADANE; Gerbery po recenzji i zatwierdzeniu przekroju B2B.**

Start: `docs/ZMIANY-R4.md` (co i dlaczego), `docs/ZASILANIE-RESET.md` (reset, sekcja R4), `docs/DLA-RECENZENTA.md` (kolejność recenzji), `docs/ODBIOR.md` (pomiary przed integracją).

## Co zmienia R4

1. **U6 SN74LVC1G17 + R41 220 Ω między SUP_N a J4.15 (SUP_N_OUT), C15 100 nF przy U6.** P04 dostaje reset z wyjścia Schmitta: jedno zbocze ok. 10 ns zamiast narastania EN modułu (τ ≈ 5 ms), które łamało wymaganie 74LVC125A w P04 (≤ 10 ns/V).
2. **PCB:** zmiana położona ręcznie przy J4. Resztę miedzi przeniesiono z wyniku routera R3. Usunięte 3 odcinki R3, dodane 25 elementów w obszarze 6–31 × 58–84 mm, HW_ARMED_CORE obchodzi U6 po B.Cu. Bilans sprawdza `src/check_revision.py`.
3. **Kontrole:** tor U6 → R41 → J4.15 i odsprzęganie C15 w netliście i na PCB, nowe mutacje i próby ujemne, porównanie R3 → R4.

## Zawartość

- CAD: `eda/P03.kicad_pro`, pięć arkuszy A3, `eda/P03.kicad_pcb`.
- PDF: `output/pdf/P03-R4-schemat.pdf` (5 × A3), `output/pdf/P03-R4-PCB.pdf` (przegląd, montaż, obie warstwy 1:1).
- Zakupy: `docs/BOM.csv`, `docs/zakupy.csv`, `docs/wiazki-BOM.csv`.
- Połączenia: `docs/netlist-pinowa.csv`, `docs/interfejsy.csv`, `docs/STANY-DOMYSLNE.csv`.
- Sprawdzenia: `verification/QA.md` i raporty JSON; `src/verify_function.py`, `src/verify_pcb.py`, `src/check_revision.py`, próby ujemne.
- Odtwarzanie: `docs/ODTWARZANIE.md`. Wynik routera R3 (`routing/P03-R3.ses`) jest wejściem R4.
- `reference/`: R3 i R2 zamrożone (PCB, części, manifest), recenzje R1 i R2, karty katalogowe (w tym SN74LVC1G17), `interfaces-R3.json`.

## Pozycje otwarte

- Recenzja layoutu przy J4 (U6/C15/R41, przelotki HW_ARMED_CORE, dostęp lutownicy przy J4 i adapterze U12).
- Przekrój mechaniczny pary B2B (MPN, wysokości rzędów, szczelina), przed zamówieniem P03 i P05.
- Antena i Wi-Fi: pomiar na gotowym zestawie. Temperatura LDO modułu.
- Zbocza SPI i SUP_N_OUT, prąd zwarcia J4.15: pomiar według `ODBIOR.md`.
- P07 nadal HOLD. Problemy firmware P05 (start AD7606B, czas ramki SPI) poza zakresem.
