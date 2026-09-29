# P06 I-LOGGER - R1 do recenzji

27.09.2026. Pomiar prądu silnika EGR w trybie LOGGER, dla EGRLab v6.1 / P03-R2. **Projekt do recenzji i przymiarki; sprzęt NIE ZBADANY.** Poprzednie płytki pozostają bez zmian. P07 nadal HOLD.

PCB 120 × 100 mm, FR4 1,6 mm, dwie warstwy miedzi po 70 µm. P06 zawiera stale włączony bocznik PBV 5 mΩ, INA240A2, lokalny MCP3201 i mechaniczne obejście. Zasilanie elektroniki 5 V z P02; prąd silnika przepływa wyłącznie między ECU_P1 a EGR_P1. To tor prądowy, bez sterowania EGR i bez izolacji galwanicznej pomiaru.

| Plik | Zawartość |
|---|---|
| `eda/P06.kicad_pro` | Edytowalny projekt KiCad 10, 6 arkuszy schematu, PCB, lokalne biblioteki |
| `output/pdf/P06-R1-schemat.pdf` | Natywny schemat, 6 × A3 |
| `output/pdf/P06-R1-PCB.pdf` | Omówienie, montaż 1:1, F.Cu i B.Cu 1:1 |
| `docs/PROJEKT.md` | Obliczenia, zakres, zasilanie, ograniczenia pomiaru |
| `docs/BOM.csv`, `docs/ZAKUPY.md` | Elementy i materiały do złożenia jednej płytki |
| `docs/interfejsy.csv`, `docs/WIAZKI.md` | Oba końce przewodów, długości, pinout, kotwy |
| `docs/MECHANIKA.md` | Obudowy, otwory, montaż przewlekany i SOIC/0805 |
| `docs/ZMIANY.md`, `docs/FIRMWARE.md` | Odstępstwa od v6.1 i współpraca z firmware |
| `verification/QA.md`, `verification/ODBIOR.md` | Kontrole plików oraz osobny, niewypełniony odbiór sprzętu |
| `src/`, `routing/` | Generatory, zapis routingu, testy i kontrole negatywne |
| `reference/` | Zamrożone wejścia, dokumentacja producentów i adresy źródeł |

Kolejność pracy: recenzja R1 → przymiarka 1:1 rzeczywistych części → zatwierdzenie mechaniki → eksport Gerberów → montaż i odbiór. Pakiet nie zawiera Gerberów przeznaczonych do zamówienia przed przymiarką.

Odtwarzanie: `python src/run_release.py --rebuild` Pythonem KiCad 10 z `pcbnew`; dokumenty wymagają dodatkowo Pillow, ReportLab i Popplera. Domyślnie używany jest zapisany SES, bez uruchamiania routera od nowa. Zmiana geometrii wymaga ponownego DRC i oględzin PDF. Instrukcje i zmienne środowiskowe: `docs/ODTWARZANIE.md`.
