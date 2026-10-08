# P08 R2 — SENSOR w formacie S1, schemat (zadanie dla sesji w chmurze, 5.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Baza: `origin/pelny-s1`. Gałąź zadania: `p08-r2-schemat`, wynik jako PR do `pelny-s1`.

**Zakres:** tylko schemat, kontrole i dokumenty, **bez PCB** (`docs/CHMURA.md`, zasada 6).

## Decyzje
- 5.10.2026: wariant pełny przygotowujemy przed zamówieniem (jedno wspólne zamówienie). **P08 na 5. poziomie, slot S1, klasa 1/3 (53 × 100 mm)**; sloty S2–S3 tego poziomu zajmie P07 (`format-s1.json`). Jeśli obwód R1 nie zmieści się realnie w 1/3 (ocena powierzchni jak `powierzchnia.py` w P10 R2), zapisz to z liczbami jako pytanie w PR — nie zmieniaj klasy sam.
- Obwód P08 R1 zostaje (zamknięty pakiet `Plytki/P08-R1-review` — nie zmieniać; wejście): TPS2553, przekaźnik G6K-2P-Y rozłączający plus i powrót, TBD62083, MCP120, 74LVC125. Zmieniają się złącza (wszystko przez krawędź A i P12 zamiast wiązek LV08 / SENSOR / SFAULT), punkty serwisowe (krawędź B), typy części (S1: posiadane THT na stojąco, nowe SMD 1206), wymiar.
- J4 TSENSOR (czujnik położenia EGR, Mini-Fit 2p w R1): w S1 przewody do portu TEST na panelu — pole przewodów z kotwą przy krawędzi x = 0 (strona panelu), jak J4 / J6 w P05 R3.

## Źródła
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-3; §4, §5, §6, §8) i `format-s1.json`.
- `Plytki/P08-R1-review` (docs/interfejsy.csv, WIAZKI.md, PROJEKT.md, parts.json, src/ — generator do skopiowania).
- Kontrakty P12: `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md` / `kontrakty.json` — po stronie P03 R6 ustalone i zamówione: SENSOR_HEALTHY (P03 J_BP1.12, wejście P03); SENSOR_ENABLE (P03 J_BP3.9) idzie do P04. Zasilanie z P02 R4 J_BP (5V_SYS, 3V3_IO).
- Połączenia P08 ↔ P04 (SENSOR) i P08 ↔ P03 (SFAULT): nazwy sieci **dokładnie** jak w `P08-R1-review/docs/interfejsy.csv` i `P04-R2.2-review/docs/interfejsy.csv` (P12 łączy po nazwie; równolegle sesja robi P04 R3 S1 z tymi samymi nazwami).
- Pamięć: `docs/pamiec-claude/MEMORY.md`, `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`.

## Zasady
`docs/CHMURA.md` 1–9. Nie zmieniać: `EGRLab-AKTYWNE.md`, `docs/`, `scripts/`, `Plytki/Format-S1/`, zamkniętych pakietów, `.gitattributes`.

## Do zrobienia — pakiet `Plytki/P08-R2-review`
1. Kopia łańcucha schematu z R1; kontrola zgodności obwodu z R1 na netliście (poza złączami i punktami serwisowymi).
2. J_BP na krawędzi A (IDC 2×5 lub 2×8 kątowe obudowane, środek x = 26,5, pin 1 od mniejszego x, GND na nieparzystych) — `docs/J_BP.csv` w formacie innych płytek; SENSOR_HEALTHY na pinie zgodnym z kierunkiem.
3. Listwa serwisowa na krawędzi B (S1 §6) z punktami ODBIOR R1.
4. Kontrole: ERC 0, zgodność z R1, kontrakty i nazwy sieci wobec P04 R2.2 / P03 R6, ocena powierzchni dla klasy 1/3, próby ujemne z zerową, PDF, BOM S1.
5. README: decyzje, zmiany R1 → R2, otwarte pytania (w opisie PR).

Po PR zakończyć pracę (zasada 5).
