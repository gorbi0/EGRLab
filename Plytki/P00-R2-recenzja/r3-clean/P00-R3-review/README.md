# P00 FIXTURE — rewizja R3 (zamykająca)

27.09.2026. R3 powstała na podstawie R2 Astry i mojej recenzji `Plytki/P00-R2-recenzja/RECENZJA-P00-R2.md`. Pakiety R1 i R2 pozostają bez zmian. **Status: pliki gotowe do zamknięcia projektu; miedź, rozmieszczenie, wartości i MPN są identyczne z R2. Przymiarka 1:1, zakup i odbiór sprzętu NIE ZBADANE.**

P00 daje osiem przełączanych poziomów H/L przez 1 kΩ i heartbeat ok. 102 Hz (TLC555) z przełącznikiem RUN/STOP. Zasilanie 6–15 V na J10, zalecane 9–12 V, przez D1 i LM2937 3,3 V. Służy do odbioru pojedynczych modułów, przede wszystkim P04. Nie wchodzi do zestawu w samochodzie.

## Co zmienia R3

1. **Wiązka do P04 napisana dla zamkniętego P04-R2.1** (R2 opisywało P04 v6.1: J13–J20, H_* z J16.1). Piny J1–J8 P04, TP1 P04 jako źródło pięciu gałęzi 1 kΩ, wybierak HB, styki STOP/ARM/SAFE_N, lista „tylko pomiar” i przypisanie do prób E03–E21. Mapę sprawdza `src/check_harness.py` względem zamrożonej netlisty P04-R2.1.
2. **Nadruk:** „+VIN 6-15V” pod J10; pole TP3 opisane „ZA D1”. TP3 leży za diodą i nie jest wejściem zasilania.
3. **Kontrole:** budżet cieplny powiązany z maksimum z netlisty (57,1 mA wobec 65 mA), poziom H heartbeat na wejściu P04, próby ujemne z próbą zerową i czystym DRC kopii, zagłodzone termiki po UUID.
4. **Dokumenty:** plan B dla temperatury to 12 V (radiator koliduje z C5/C7), pomiar HB na J9 przed P04 ze środkiem zaradczym, wyposażenie wiązki w `ZAKUPY-P00.md`.

Mapa zmian: `docs/ZMIANY-R3.md`. Historia R1 → R2: `docs/ZAMKNIECIE-RECENZJI.md`.

## Co otworzyć

| Plik | Przeznaczenie |
|---|---|
| `eda/P00.kicad_pro` | Projekt KiCad 10, schemat i PCB |
| `output/pdf/P00-R3-schemat.pdf` | Schemat A3 |
| `output/pdf/P00-R3-PCB.pdf` | Przegląd, montaż i obie warstwy miedzi 1:1, belka 100 mm |
| `output/fabrication/` | Gerbery i osobne wiercenia PTH/NPTH, do zamówienia po przymiarce |
| `docs/ZAKUPY-P00.md`, `docs/BOM.csv` | Zestawienie zakupowe, wyposażenie wiązki, BOM według oznaczeń |
| `docs/ODBIOR-P00-R2.md` | Uruchomienie i odbiór (nazwa z R2, treść R3) |
| `docs/ZALOZENIA-P00-R2.md` | Warunki pracy, poziomy, bilans cieplny (nazwa z R2, treść R3) |
| `docs/P00-P04-WIAZKA.md` | Wiązka do P04-R2.1 i przypisanie do prób P04 |
| `docs/LAYOUT.md`, `docs/ODTWARZANIE.md` | Geometria i nadruk; odtwarzanie pakietu |
| `docs/ZMIANY-R3.md` | Zmiany R3 i punkty sporne |
| `verification/QA.md` | Wyniki kontroli i ich ograniczenia |
| `reference/` | Zamrożone R2 (PCB, części, manifest), P04-R2.1 (części, pinout, P00-P04, ODBIOR), recenzje R1 i R2, źródła |

## Wyniki kontroli plików

Pełne wyniki: `verification/QA.md`. Obliczenia i DRC nie zastępują pomiaru stabilności LM2937, poziomu heartbeat, temperatury ani przymiarki rzeczywistych części.

## Pozycje otwarte

Przymiarka 1:1, zakup (części P00 nie są zamówione), odbiór według `ODBIOR-P00-R2.md`, potem odbiór P04 według jego formularza. W katalogu `output/pdf` zostały dwa PDF R2 skopiowane razem z pakietem (`P00-R2-*.pdf`). Nie należą do wydania R3 i nie trafiają do archiwum; można je usunąć ręcznie.
