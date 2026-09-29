# EGRLab P01 - PCB R1, do przeglądu

Wykonany layout **dwuwarstwowy 160 × 120 mm**, na podstawie zamrożonego schematu
P01-R3. To pierwsza PCB P01: geometria, ścieżki, pola miedzi, opisy i wiercenia.
Status: **LAYOUT SPRAWDZONY; PRZYMIARKA I SPRZĘT NIE ZBADANE**.

## Otwieranie

- `eda/P01.kicad_pro` - projekt KiCad 10; schemat i PCB z lokalnymi bibliotekami.
- `output/pdf/P01-PCB-R1-dokumentacja.pdf` - montaż 1:1, warstwy miedzi i kontrola przymiarki.
- `docs/LAYOUT.md` - decyzje, zmiana wymiarów i ograniczenia toru mocy.
- `docs/MECHANIKA.md` - przymiarka części, wiązki, montaż radiatorów.
- `docs/BOM.csv`, `docs/BOM-MECHANIKA.csv` - elementy R3 i aktualna mechanika PCB.
- `verification/QA.md` - wyniki kontroli; `drc.json` i `pcb-checks.json` są raportami maszynowymi.

Schemat, wartości i pinouty R3 nie zostały zmienione. Przybyły cztery otwory
montażowe; HS1/HS2 są osobnymi footprintami mechanicznymi. **Wysokość PCB wzrosła
ze wstępnych 100 do 120 mm** dla większych rezystorów THT, radiatorów i odciążenia
wiązek. Dolne otwory M3 są teraz na Y=115 mm. To istotne przy wyborze obudowy.

## Następny krok przy stole

Wydrukuj stronę montażową PDF w skali **100%, bez dopasowania**, zmierz belkę
100 mm i przyłóż rzeczywiste radiatory, Q1/D2, C6, J6 oraz przewody z opaskami.
Zapisz wynik w `docs/MECHANIKA.md`. Po przymiarce i przeglądzie PCB można wykonać
eksport produkcyjny z tej konkretnej, zamrożonej płytki. **W tym pakiecie nie ma
Gerberów do zamawiania**, zgodnie z bramką przymiarki przed Gerberami w R3.
Nie zamówiono żadnych części ani PCB.

Potem montaż i niezależny odbiór P01 według `reference/R3-docs/ODBIOR.md` oraz
`METROLOGIA.md`; dopiero następnie integracja P02-HOLD. Czysty DRC nie potwierdza
SOA, termiki, dynamiki zabezpieczenia ani odporności na impulsy samochodowe.

## Granice pakietu

Historyczne pliki w `reference/` dokumentują R3; ich stare 160 × 100 mm i status
"layout niewykonany" nie opisują niniejszej PCB. Dokumentacja bieżąca jest w
`docs/`. P01-R3, wcześniejsze rewizje i firmware systemu pozostają bez zmian.
**P07 nadal HOLD do sprawdzenia fizycznego modułu BTS7960.**

Końcowym źródłem PCB jest `eda/P01.kicad_pcb`. Skrypty tworzenia/rozmieszczania
w `src/` zapisują przebieg pracy i nie są poleceniem do bezwarunkowego nadpisania
gotowej płytki. Powtarzalny odbiór i wykrywanie błędów: `src/verify_pcb.py`,
`src/negative_controls.py` oraz komendy w `verification/QA.md`.
