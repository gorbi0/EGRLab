# P02 R4 — specyfikacja zasilania z pakietu Li-ion 4S

29.09.2026. **Etap: specyfikacja przyjęta 29.09.2026** (D-01 ze zmianą: VBAT z klemy akumulatora w komorze). Nie ma jeszcze schematu, PCB ani zakupów. P02 R4 zastępuje P01 PROTECT i część HOLD płytki P02 R3; zamówienie PCB P01 i P02 R3 jest wstrzymane.

| Plik | Zawartość |
|---|---|
| `SPECYFIKACJA-P02-R4.md` | decyzje, architektura, wymagania, obliczenia, złącza, pakiet, części, wpływ na inne płytki, plan odbioru, decyzje do potwierdzenia |
| `interfejsy.csv` | złącza P02 R4 pin po pinie, z drugą stroną i zmianą względem R3/P01 |
| `src/obliczenia.py`, `obliczenia.json` | UVLO, podtrzymanie 2200 µF, ładowanie C_H, straty Q1/D1, CH7, czas pracy pakietu |

Odtworzenie liczb: `python src/obliczenia.py` (sama biblioteka standardowa Pythona).
