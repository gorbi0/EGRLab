# Uruchomienie i odbiór sprzętu S1 — procedura (zadanie dla sesji w chmurze, 4.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Baza: `origin/zamowienie-s1`. Gałąź zadania: `odbior-s1`, wynik jako PR do `zamowienie-s1`.

**Cel:** po przyjściu płytek z JLCPCB (P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2) użytkownik ma je zmontować i uruchamiać krok po kroku z jednym dokumentem przy stole. Dotąd każde wydanie ma „odbiór sprzętu: NIE ZBADANO”, a firmware 6.2-s1 też nie był sprawdzony na sprzęcie.

**Źródła:** README i `docs/` wydań `Plytki/P0x-Rx-review` (BOM, obliczenia, listwy serwisowe J_SV, ODBIOR tam, gdzie jest), `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md` (budżety 5V_SYS: razem 1090 mA z TSR 2-2450 2 A), firmware `Rewizje/EGRLab-v6.2-s1` (warianty, tryb testowy, F-01…F-09), `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md`. Pamięć: `MEMORY.md`, `format-s1.md`, `p02-r4-state.md`, `zasilanie-ogniwa-18650.md`, `user-pcb-background.md`.

**Sprzęt użytkownika:** oscyloskop DHO804, multimetr, zasilacz laboratoryjny (zakres sprawdzić w `docs/`), stanowisko P00, pakiet 4S 18650.

## Zasady

`docs/CHMURA.md` 1–9. Niczego nie zmieniać w pakietach płytek ani w firmware; tylko nowy katalog dokumentów. Kompilacja firmware niepotrzebna.

## Do zrobienia — `Plytki/Odbior-S1/`

1. `URUCHOMIENIE.md` — kolejność: oględziny i pomiar zwarć szyn przed zasileniem → P02 sama (zasilacz z ograniczeniem prądu, potem pakiet 4S) → P03 → P05 / P09 / P06 / P10 pojedynczo przez P12 (lub przewody, jeśli P12 jeszcze nie ma). Na każdym kroku: co podłączyć, limit prądu zasilacza, punkty pomiarowe (pin listwy J_SV / pole), wartość oczekiwana z tolerancją, wynik zły → co sprawdzić.
2. Pomiar startu 5V_SYS z całą pojemnością (~490–500 µF wobec 600 µF dopuszczalnych dla TSR 2-2450): przebieg na DHO804, czas narastania, prąd rozruchu; kryterium zaliczenia.
3. P05: kontrola drgań DAQ_OK (okno i próg z README P05 R3) i AD7606 (testowe wejście); P06: kalibracja zera i wzmocnienia INA240 przy znanym prądzie, przełącznik BYPASS; P09: termopara w temperaturze otoczenia i w wodzie z lodem; P10: pętla CAN / OBD na stole.
4. Firmware 6.2-s1: który wariant wgrać na którym etapie, polecenia testowe, oczekiwane logi; tabela odbioru F-01…F-09 na sprzęcie.
5. `FORMULARZ-ODBIORU.md` (do wydruku): tabele z polami na zmierzone wartości, podpis i datę, dla każdej płytki osobno.
6. `NARZEDZIA-I-CZESCI.md`: co mieć przed montażem (lutownica mocniejsza do pól z pełnym połączeniem GND — listy `routing/solid-pads.json` wydań, topnik, kolejność montażu SMD od spodu).

Po PR zakończyć pracę.
