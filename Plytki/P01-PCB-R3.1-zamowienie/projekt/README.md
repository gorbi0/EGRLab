# EGRLab P01 - PCB-R3 / schemat R3 / montaż A1 - wydanie R3.1

**R3.1 (25.09.2026):** PCB-R3 z poprawkami po recenzji `Plytki/P01-PCB-R3-recenzja/`:
kolejność montażu C6/Q1, wiersz U4 i uwagi montażowe w BOM A1, kontrole. Płytka (miedź, nadruk, wiercenia)
identyczna z R3. Szczegóły na górze `docs/ZMIANY-R3.md`.

Nowa rewizja PCB na bazie P01-PCB-R2 Opusa. **160 x 120 mm, dwie warstwy,
FR4 1,6 mm, miedź 70 um na stronę.** Zachowane interfejsy i funkcjonalne bloki R2.
Oryginalne pakiety PCB-R1, PCB-R2 i schematu R3 nie są zmieniane.

Najpierw otwórz:

- `eda/P01.kicad_pro` - edytowalny projekt KiCad 10 i właściwa PCB.
- `output/pdf/P01-PCB-R3.1-dokumentacja.pdf` - montaż 1:1, spód, miedź i przymiarka.
- `docs/ZMIANY-R3.md` - co zmieniono oraz dlaczego.
- `docs/BOM-MONTAZOWY-A1.csv` - części do rzeczywistego montażu, z rozróżnieniem od BOM nominalnego R3.
- `docs/MECHANIKA.md` - czynności przy stole; wyniki pozostają NIE ZBADANO.
- `verification/QA.md` - zakres kontroli oraz jedno polecenie do powtórzenia odbioru.

## Najważniejsze zmiany

D4 znajduje się bezpośrednio między Q1 i C6. Droga K-S ma 5,25 mm, A-G 6,78 mm.
C6 przesunięto o 2,1 mm ku środkowi PCB. Szyna VS na B.Cu omija jego pad GATE.
TP1/TP2 są dostępne od spodu, z opisami S/G i ostrzeżeniem, że SOURCE nie jest GND.
Ścieżki od Q1 do pól pomiarowych mają po około 4,62 mm.

Dodano lokalne modele gabarytowe (w tym radiatory, Q1/D2, D4 i C6), opisy rezystorów
na spodzie oraz pola AssemblyMPN/AssemblyValue na PCB. Nominalne wartości schematu
R3 pozostają zachowane; wariant A1 jest opisany osobno, szczególnie R8 = 221 kΩ.

Odbiór zawsze uruchamia nowy natywny DRC. Raport jest związany z hashem PCB,
schematu, reguł, bibliotek, modeli, materiału odniesienia i skryptów. Pięć prób
usterek obejmuje rzeczywistą przerwę oraz zwarcie przy pozostawionym starym raporcie.

## Stan i następny krok

Aktualny wynik cyfrowy jest w `verification/release-status.json` i
`verification/pcb-checks.json`. Przymiarka części i pomiary elektryczne są
**NIE ZBADANE**, a nie domyślnie zaliczone. Modele są gabarytowe; nie zastępują
sprawdzenia rzeczywistych radiatorów, tulejek, śrub, wtyku i lutowania.

Wydrukuj stronę montażową w 100%, sprawdź belkę 100 mm i uzupełnij MECHANIKA.md.
Eksport Gerber/Excellon jest etapem po przymiarce, zgodnie z przyjętym planem;
ten pakiet dostarcza kompletny layout do jej wykonania i przeglądu.
Uruchamianie: `reference/R3-docs/ODBIOR.md` i `METROLOGIA.md`, uzupełnione
przez `docs/ODBIOR-R3-DODATEK.md`. P07 nadal HOLD dla wariantu BTS7960.

`reference/R2-layout` i `reference/R3-*` są materiałem historycznym. Ich tytuły
oraz dawne wymiary/stany nie opisują bieżącej PCB. `mechanical/placement.kicad_pcb`
jest widokiem rozmieszczenia bez tras, a `output/plot-source.kicad_pcb` kopią
do ilustracji. **Jedyny właściwy plik PCB: `eda/P01.kicad_pcb`.**

Nie używać plików z `verification/negative-controls` do wykonania płytki:
zawierają celowo wprowadzone usterki.
