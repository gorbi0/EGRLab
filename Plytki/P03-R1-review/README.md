# P03 CORE — schemat i PCB R1 do recenzji

25.09.2026 · Claude (schemat i layout). Recenzja: Astra. Stan: **pliki do recenzji; sprzęt, przymiarka 1:1 i odbiór NIE ZBADANE.**

P03 to rdzeń EGRLaba z v6.1-rc1: ESP32-S3 (Waveshare ESP32-S3-DEV-KIT-N32R16V na gniazdach), microSD (Adafruit 4682), MCP23017, dekoder CS 74HC139, nadzór TPS3808 i siedem buforów 74LVC125A (Nexperia) między CORE a złączami. Decyzje użytkownika z 25.09: listwy modułu co 22,86 mm, P03 i P05 obok siebie ze złączem kątowym, moduł Adafruit 4682, format 160 × 120 jak P01/P02, PA0085 w dwóch rzędach po 3, CAN jako IDC 2 × 3 z kluczem na pinie 4.

## Wynik kontroli

| Kontrola | Wynik |
|---|---|
| ERC / netlista pin po pinie | 0 / 347 z 347 zgodnych |
| Zgodność z importem v6.1 | 310 pinów, 0 różnic; dodane tylko pozycje 5–6 złącza CAN i pola TP |
| DRC: naruszenia / niepołączone / zgodność ze schematem | 0 / 0 / 0 |
| Kontrole gotowej PCB | 26/26 |
| Próby ujemne | 14/14 wykryte |

Szczegóły: `verification/QA.md`.

## Co przejrzeć najpierw

1. **Położenie M1**: USB-C na krawędzi, antena w głąb płytki nad strefą bez miedzi — świadomy kompromis kosztem zasięgu Wi-Fi (`docs/ZALOZENIA-P03-R1.md`, wiersz „sporne”).
2. **J1 DAQ kątowe do P05**: czoło przy prawej krawędzi, H5 jako drugi punkt mocowania przy złączu; wysokość rzędów styków zależy od wybranych części (`docs/MECHANIKA.md`).
3. **Klasy ścieżek 0,30/0,25 mm** (P00/P02: 0,5/0,3) i zszycie wylewek GND 48 przelotkami.
4. **Nadruk przy LV03**: pola TP pod padami wiązki z tą samą siecią; 23 pady GND z pełnym połączeniem do wylewki (lutowanie).
5. Zmiana względem v6.1 wynikająca z decyzji: wiązka CAN do P10 ma 6 pozycji.

## Pliki

| Ścieżka | Zawartość |
|---|---|
| `eda/` | projekt KiCad 10: `P03.kicad_sch` + `IO.kicad_sch`, `P03.kicad_pcb`, biblioteki lokalne |
| `output/pdf/P03-R1-schemat.pdf`, `output/pdf/P03-R1-PCB.pdf` | schemat (2 × A3); podsumowanie, montaż 1:1, F.Cu i B.Cu 1:1 |
| `docs/ZALOZENIA-P03-R1.md` | decyzje użytkownika, zgodność z v6.1, decyzje R1 i sporne, sprawy na R2 |
| `docs/LAYOUT.md`, `docs/MECHANIKA.md` | layout, miedź, oczyszczanie, nadruk; współrzędne złączy, modułów i otworów, lista przymiarki |
| `docs/ZAKUPY-P03.md` | co już zamówione, co dokupić (w tym para złączy J1/P05) |
| `docs/BOM.csv`, `docs/parts.json` | BOM z uwagami; lista części ze źródłem w BOM v6.1 |
| `reference/` | import pinowy, BOM i interfejsy CORE z v6.1, pinout DevKitC-1, rysunki Adafruit 4682 |
| `routing/`, `src/`, `verification/` | wejście i wynik routera; skrypty (`run_release.py` odtwarza całość); kontrole |

## Odtworzenie

```
python src/run_release.py
```

Pythonem z KiCada 10, z katalogu pakietu. Importuje zapisany wynik routera; `--new-route` uruchamia Freerouting od nowa (z ponawianiem, jeśli wylewka nie obejmie któregoś padu GND).
