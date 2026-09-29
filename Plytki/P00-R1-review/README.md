# P00 FIXTURE — schemat i PCB R1 do recenzji

25.09.2026 · Claude (schemat i layout). Recenzja: Astra. Stan: **pliki do recenzji; sprzęt, przymiarka 1:1 i odbiór NIE ZBADANE.**

P00 to przyrząd stanowiskowy z v6.1-rc1: osiem przełączanych źródeł 3,3 V/GND przez 1 kΩ i heartbeat ok. 102 Hz z TLC555, używany przy odbiorze pojedynczych płytek (przede wszystkim P04 SAFE i watchdoga). Nie wchodzi do zestawu w aucie. Decyzje użytkownika z 25.09: wyjścia na listwach 2,54 mm, zasilanie 5–15 V z własnym LM2937 3,3 V, LED stanu przy każdym kanale.

## Wynik kontroli

| Kontrola | Wynik |
|---|---|
| ERC / netlista pin po pinie | 0 / 141 z 141 zgodnych |
| DRC: naruszenia / niepołączone / zgodność ze schematem | 0 / 0 / 0 |
| Kontrole gotowej PCB | 22/22 |
| Próby ujemne | 8/8 wykryte |

Szczegóły: `verification/QA.md`.

## Co przejrzeć najpierw

1. **Przełącznik Würth WS-SLTV**: wspólny styk na środkowym pinie i „opposite side connection” — przenumerowany symbol i orientacja (`docs/ZALOZENIA-P00-R1.md`).
2. **Zasilanie**: D1 + LM2937 przy 5–15 V, kondensator wyjściowy względem wymagań karty TI.
3. **Dodatek spoza v6.1**: SW9 RUN/STOP heartbeatu (STOP = wyjście trwale L).
4. Nadruk: w kolumnach tylko numery kanałów zamiast oznaczeń każdej części.

## Pliki

| Ścieżka | Zawartość |
|---|---|
| `eda/` | projekt KiCad 10: `P00.kicad_sch`, `P00.kicad_pcb`, biblioteki lokalne |
| `output/pdf/P00-R1-schemat.pdf`, `output/pdf/P00-R1-PCB.pdf` | schemat A3; podsumowanie, montaż 1:1 (z oznaczeniami Fab), F.Cu i B.Cu 1:1 |
| `docs/ZALOZENIA-P00-R1.md`, `docs/LAYOUT.md`, `docs/ZAKUPY-P00.md` | karta założeń i decyzji; layout z mechaniką; stan części |
| `docs/BOM.csv`, `docs/parts.json` | BOM z uwagami; lista części ze źródłem w BOM v6.1 lub oznaczeniem dodatku R1 |
| `reference/` | import pinowy, BOM i próby P00 z v6.1, źródła kart katalogowych |
| `routing/`, `src/`, `verification/` | wejście i wynik routera; skrypty (`run_release.py` odtwarza całość); kontrole |

## Odtworzenie

```
python src/run_release.py
```

Pythonem z KiCada 10, z katalogu pakietu. Importuje zapisany wynik routera; `--new-route` uruchamia Freerouting od nowa.
