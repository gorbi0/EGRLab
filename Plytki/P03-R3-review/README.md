# EGRLab P03-R3 — CORE (rewizja zamykająca)

27.09.2026 · R3 na podstawie R2 Astry i końcowej recenzji `Plytki/P03-R2-recenzja/RECENZJA-P03-R2.md`. Pakiety R1 i R2 pozostają bez zmian. **Status: pliki gotowe do zamknięcia projektu; miedź i rozmieszczenie identyczne z R2. Przekrój B2B P03–P05, przymiarka i odbiór sprzętu NIE ZBADANE; Gerbery po zatwierdzeniu przekroju B2B.**

Start: `docs/ZMIANY-R3.md` (co i dlaczego), `docs/ZASILANIE-RESET.md` (reset i blokada USB), `docs/ODBIOR.md` (pomiary przed integracją).

## Co zmienia R3

1. **R14 (CORE_LINK) 0 Ω → 1 kΩ.** Zwarcie żyły 13 z sąsiednią masą w taśmie nie zwiera już 3V3_CORE. P04 dalej widzi ≥ 2,85 V.
2. **Kontrole:** żadne złącze nie wyprowadza szyny zasilania bez ograniczenia. Złącza pin w pin z zamrożonymi P02-R3/P04-R2.1/P05-R1. Próby ujemne mają próbę zerową i czysty DRC kopii; w R2 jedna z nich była pozorna.
3. **Dokumenty:** wolne zbocze SUP_N na złączu do P04 (skutki i pomiar), wymagania dla P09/P10, poprawione liczby resetu, lokalna karta LTC4412.

## Zawartość

- CAD: `eda/P03.kicad_pro`, pięć arkuszy A3, `eda/P03.kicad_pcb`.
- PDF: `output/pdf/P03-R3-schemat.pdf` (5 × A3), `output/pdf/P03-R3-PCB.pdf` (przegląd, montaż, obie warstwy 1:1).
- Zakupy: `docs/BOM.csv`, `docs/zakupy.csv`, `docs/wiazki-BOM.csv`.
- Połączenia: `docs/netlist-pinowa.csv`, `docs/interfejsy.csv`, `docs/STANY-DOMYSLNE.csv`.
- Sprawdzenia: `verification/QA.md` i raporty JSON; `src/verify_function.py`, `src/verify_pcb.py`, `src/check_revision.py`, próby ujemne.
- Odtwarzanie: `docs/ODTWARZANIE.md`.
- `reference/`: R2 zamrożone (PCB, części, manifest), recenzje R1 i R2, karty katalogowe, `interfaces-R3.json`.

W `output/pdf` zostały dwa PDF R2 skopiowane razem z katalogiem (`P03-R2-*.pdf`). Nie należą do wydania R3 i nie trafiają do archiwum; można je usunąć ręcznie.

## Pozycje otwarte

- Przekrój mechaniczny pary B2B (MPN, wysokości rzędów, szczelina), przed zamówieniem P03 i P05.
- Antena i Wi-Fi: pomiar na gotowym zestawie.
- Temperatura LDO modułu.
- Zbocza SPI i SUP_N: pomiar według `ODBIOR.md`.
- P07 nadal HOLD. Problemy firmware P05 (start AD7606B, czas ramki SPI) poza zakresem.
