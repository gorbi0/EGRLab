# EGRLab P09 TEMP — R1

Kompletna płytka nośna dwóch kupionych modułów MAX31856 XU z oferty Allegro 18805671895. Status: **CAD do recenzji; sprzęt NIE ZBADANO; dopasowanie realnych modułów do sprawdzenia przed zamówieniem PCB**. Nie zmieniono wcześniejszych płytek ani zamrożonej v6.1. P07 nadal HOLD dla wariantu BTS7960.

- `eda/P09.kicad_pro`: projekt KiCad, cztery arkusze schematu i PCB 100×100 mm, dwuwarstwowe.
- `output/pdf/P09-R1-schemat.pdf`: schemat; `output/pdf/P09-R1-PCB.pdf`: opis i montaż/miedź 1:1.
- `docs/PROJEKT.md`, `docs/MODUL-KWALIFIKACJA.md`, `docs/WIAZKI.md`: działanie, przymiarka i uruchomienie.
- `docs/ZAKUPY.md`, `docs/BOM.csv`, `docs/interfejsy.csv`: zakupy i połączenia.
- `firmware/P09-temperature.diff`: poprawka rzeczywistego błędu odczytu MAX31856 w bazowym firmware, z testami. Pełny plik `firmware/board.c` jest kopią v6.1 z tą poprawką, nie scalonym firmware wszystkich nowych PCB.
- `verification/QA.md` i `verification/ODBIOR.md`: wyniki kontroli plików i niewypełniony formularz pomiarów.

**Najpierw przymiarka 1:1 i kwalifikacja zasilania modułu.** Zdjęcia oferty pokazują kolejność 9 pinów oraz napis „VIN/Logic: 3.3–5V”; nie udostępniają schematu ani wymiarowanego rysunku. Nie uznajemy tej płytki za elektrycznie lub mechanicznie identyczną z Adafruit. Gerbery nie są częścią pakietu do recenzji.
