# P04 R3 — SAFE w formacie S1, schemat (zadanie dla sesji w chmurze, 5.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Baza: `origin/pelny-s1`. Gałąź zadania: `p04-r3-schemat`, wynik jako PR do `pelny-s1`.

**Zakres:** tylko schemat, kontrole i dokumenty, **bez PCB** (`docs/CHMURA.md`, zasada 6).

## Decyzje użytkownika
- 5.10.2026: wariant pełny, **P04 na 6. poziomie, klasa L** (160 × 100 mm, sloty S1–S3, dystans 20 mm pod spodem — `format-s1.json`, S1 §7). Zamówienie płytek LOGGER czeka na pełny wariant (jedno wspólne zamówienie).
- Obwód P04 R2.2 zostaje (zamknięty pakiet `Plytki/P04-R2.2-review` — nie zmieniać; to wejście). Zmieniają się złącza do innych płytek (wszystko przez krawędź A i P12), punkty serwisowe (krawędź B), typy części (S1: posiadane THT na stojąco, nowe SMD 1206), wymiar.
- P11 R2 (panel) jest już zrobiona: PANELSAFE (PANEL_3V3, MECH_OK, STOP_NC_OUT, ARM_CONTACT, TEST_KEY) przychodzi z P11 przez P12 — pinout `Plytki/P11-R2-review/docs/J_P12.csv`; przy obsadzonej P04 rezystor R1 na P11 jest DNP, PANEL_3V3 daje P04 (R40 100 Ω).

## Źródła
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3; §4 części od spodu, §5 krawędź A, §6 krawędź B, §8 złącza) i `format-s1.json`.
- `Plytki/P04-R2.2-review` (docs/interfejsy.csv, pinout.csv, PROJEKT.md, KONTRAKT-RESET.md, parts.json, src/ — generator schematu do skopiowania).
- Kontrakty P12: `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md` i `kontrakty.json` — sieci, które czekają na P04 (piny po stronie innych płytek są już ustalone i zamówione — **nie wolno ich zmieniać**):
  - z P03 R6: CORE_LINK (J_BP3.13), HEARTBEAT (J_BP3.16), HW_ARMED (J_BP3.17, wejście P03), MCU_ARM (J_BP3.18), INTERLOCK (J_BP3.20, wejście P03), PWM (J_BP3.14), SENSOR_ENABLE (J_BP3.9), SUP_N_OUT (J_BP3.12), TEST_KEY (J_BP1.14);
  - z P02 R4 J_BP: PSU_OK (12), SAFE_N (16), P04_3V3 (15), PG_SEND (17), PG_LINK (18);
  - z P05 R3: DAQ_OK (J_BP1.6);
  - z P11 R2 J_P12: PANEL_3V3 (2), MECH_OK (4), STOP_NC_OUT (6), ARM_CONTACT (8), TEST_KEY (14).
- Połączenia P04 ↔ P07 (DRIVE) i P04 ↔ P08 (SENSOR): nazwy sieci **dokładnie** jak w `P04-R2.2-review/docs/interfejsy.csv` i `P08-R1-review/docs/interfejsy.csv` (P12 łączy po nazwie; równolegle sesja robi P08 R2 z tymi samymi nazwami). P07 jeszcze nie istnieje (czeka na pomiary modułu BTS7960, `Plytki/P07-modul-BTS7960/POMIARY-MODULU.md`) — sieci do P07 wyprowadź na J_BP z nazwami z R2.2 i oznacz „czeka na P07”.
- Pamięć: `docs/pamiec-claude/MEMORY.md`, `format-s1.md`, `p04-r2-state.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`.

## Zasady
`docs/CHMURA.md` 1–9 (commit i push po etapie, bez procesów > 15 min, po dwóch nieudanych próbach stan i PR). Nie zmieniać: `EGRLab-AKTYWNE.md`, `docs/`, `scripts/`, `Plytki/Format-S1/`, zamkniętych pakietów, `.gitattributes`.

## Do zrobienia — pakiet `Plytki/P04-R3-review`
1. Kopia łańcucha schematu z R2.2; obwód bez zmian funkcjonalnych (kontrola na netliście: poza złączami i punktami serwisowymi każdy pin ma tę samą sieć co w R2.2, jak `verify_s1.py` w P05/P06 R2/R3).
2. Złącza J_BP na krawędzi A (IDC kątowe obudowane, S1 §5; środki x = 26,5 / 80,0 / 133,5 w slotach; pin 1 od mniejszego x; GND na nieparzystych gdzie się da; zasilanie z P02 przez 5V_SYS/3V3_IO lub P04_3V3 jak w R2.2) — tabela `docs/J_BP.csv` w formacie innych płytek (zlacze;pin;siec;kierunek;plytka_docelowa;uwagi). Każda sieć z listy wyżej musi się pojawić z właściwym kierunkiem.
3. Listwy serwisowe na krawędzi B (S1 §6, rezystory szeregowe) z punktami ODBIOR R2.2.
4. Kontrole: ERC 0, zgodność obwodu z R2.2, kontrakty (każda sieć „czeka na P04” ma koniec; zgodność nazw z P08 R1 / P04 R2.2 interfejsy), próby ujemne z zerową, PDF schematu, BOM S1 (nowe części SMD 1206, posiadane THT).
5. README: decyzje, tabela zmian R2.2 → R3, otwarte pytania (w opisie PR).

Po PR zakończyć pracę (zasada 5).
