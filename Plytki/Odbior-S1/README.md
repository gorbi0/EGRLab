# Odbior-S1 — uruchomienie i odbiór sprzętu LOGGER w formacie S1

*4.10.2026, sesja w chmurze, zadanie `Plytki/Format-S1/zadania/ZADANIE-ODBIOR-S1.md`. Tylko dokumenty; pakiety płytek i firmware bez zmian. Sprzęt: **NIE ZBADANO**.*

| Plik | Do czego |
|---|---|
| `URUCHOMIENIE.md` | Procedura przy stole: zwarcia → P02 R4 → P03 R6 → P05 R3 → P06 R2 → P09 R2 → P10 R2 → komplet LOGGER; połączenia stołowe bez P12 (tabela 1.3), start 5V_SYS z pełną pojemnością (9.1), odbiór firmware F-01…F-09 (rozdz. 10) |
| `FORMULARZ-ODBIORU.md` | Formularz do wydruku, osobno dla każdej płytki; ID kroków jak w procedurze |
| `NARZEDZIA-I-CZESCI.md` | Przyrządy, pola z pełnym połączeniem GND, części od spodu, kolejność montażu |

Źródła: README i `docs/` wydań (`ODBIOR.md`, `SERWIS.csv`, `J_BP.csv`, `parts.json`), `routing/solid-pads.json` i pliki PCB paczek `…-zamowienie`, `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md`, `Plytki/P02-R4-specyfikacja/SPECYFIKACJA-P02-R4.md` (O-01…O-10), `Rewizje/EGRLab-v6.2-s1` (README, `docs/`, `app_main.c`, `obd.c`, `Kconfig.projbuild`).

**Sporne decyzje w procedurze (jednym zdaniem):**
- Kolejność dołączania płytek jest narastająca (P05 przed P06), bo P06 dzieli z P05 linie ADC_SCLK/ADC_DOUTA i odbiór wspólnej magistrali wymaga obu.
- Bez P12 płytki łączą pigtaile IDC rozcięte na żyły, nie taśmy płytka–płytka, bo pinouty J_BP są różne (prosta taśma P03–P05 zwiera 5V_SYS z GND).
- P02 przy pierwszym załączeniu ma limit 1 A zamiast typowych 100 mA, bo przy niższym limicie ładowanie C12 przez R40 (0,76 A) zbija napięcie pod próg UVLO i płytka cyklicznie startuje.
- SW1 P05 (AUX HI/LO) jest na panelu, nie na płytce (decyzja 4.10): 5 przewodów do otworów SW1, ciągłość w P05-18.
- Bez P11 firmware odrzuca `zero` (LOGGER_CLEAR = L to „adapter LOGGER obecny”), więc zero prądu P06 wpisuje się `currentcal` z pomiaru multimetrem; `zero` tylko z tymczasowym podciągnięciem (URUCHOMIENIE 1.1).
- Kryteria oznaczone „(szac.)” to moje szacunki, nie liczby z obliczeń wydań — po pierwszym egzemplarzu zastąpić zmierzonymi.
