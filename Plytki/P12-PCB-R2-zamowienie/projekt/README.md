# P12 R2 — płytka połączeń krawędzi A (wariant PEŁNY), schemat i PCB

*5.10.2026, komputer 24/7 (KiCad 10.0.6 + Freerouting 2.1.0 w Dockerze). Łańcuch skryptów P12 R1 (`Plytki/P12-R1-review/src`), rozszerzony o poziomy 5 i 6. Wejście: kontrakty `Plytki/P12-przygotowanie` po dopisaniu P04 R3, P07 S1 i P08 R2 (**0 błędów, 56 sieci OK, 0 czeka**).*

**Status: PCB gotowa do zamówienia** (paczka `Plytki/P12-PCB-R2-zamowienie`). Sprzętu nie zbudowano, przymiarki taśm NIE ZBADANO. P12 R1 zostaje dla wariantu LOGGER. R2 jest płytką wariantu pełnego.

## Co to jest

Płytka 160 × 136 mm z 16 prostymi obudowanymi gniazdami IDC i 4 polami pomiarowymi. Nie ma na niej elementów aktywnych ani biernych. Każde złącze krawędzi A płytek stosu pełnego (poziomy 1–6) ma na P12 swoje gniazdo w tym samym x i na wysokości osi kątowego IDC płytki. J1–J10 mają te same oznaczenia i położenia co w R1.

| Ref | Płytka i złącze | Typ | x stosu [mm] | z osi [mm] |
|---|---|---|---:|---:|
| J1 | P02 R4 J_BP (poziom 1, S3) | IDC 2×10 | 133,5 | 14,05 |
| J2 / J3 / J4 | P03 R6 J_BP1 / J_BP2 / J_BP3 (poziom 2, S1 / S2 / S3) | IDC 2×10 | 26,5 / 80,0 / 133,5 | 40,65 |
| J5 / J6 / J7 | P05 R3 J_BP1 (S1, 2×5), P05 R3 J_BP2 (S2, 2×10), P09 R2 J1 (S3, 2×8) — poziom 3 | — | 26,5 / 80,0 / 133,5 | 62,25 |
| J8 / J9 | P06 R2 J_BP (S2, 2×8), P10 R2 J1 (S3, 2×5) — poziom 4 | — | 80,0 / 133,5 | 83,85 |
| J10 | P11 R2 J_P12 (panel, taśma z P11) | IDC 2×10 | 26,5 | 14,05 |
| **J11** | **P08 R2 J_BP (poziom 5, S1)** | IDC 2×8 | 26,5 | 105,45 |
| **J12 / J13** | **P07 S1 J_BP1 (poziom 5, S2) / J_BP2 (poziom 5, S3)** | IDC 2×8 | 80,0 / 133,5 | 105,45 |
| **J14 / J15 / J16** | **P04 R3 J_BP1 (S1, 2×8) / J_BP2 (S2, 2×10) / J_BP3 (S3, 2×10) — poziom 6** | — | 26,5 / 80,0 / 133,5 | 127,05 |
| TP1–TP4 | pola pomiarowe GND / 5V_SYS / 3V3_IO / GND | THT Ø2,0 | 94 / 100 / 106 / 112 | 14,05 |

Tabela dla programów jest w `docs/GEOMETRIA.csv`, pinout pin po pinie w `docs/kontrakt-P12.json`.

## Geometria (do potwierdzenia przy przymiarce)

- **Ustawienie jak w R1:** P12 stoi pionowo, ok. 18–20 mm przed krawędzią A (y ≈ −18), stroną F (gniazda) do stosu. KiCad: X = x stosu, Y = 140 − z.
- **Obrys:** x 0…160, z 4…140, narożniki R1, FR4 1,6 mm, 2 × 35 µm. Najwyższa oś złącza (P04, poziom 6) to z = 127,05. Korpus gniazda sięga ok. z 131,5, a jego opis ok. 133,5. P04 ma górę elementów na 121,0 + 1,6 + 16,5 = 139,1 mm. Wnętrze obudowy pełnej ma ok. 143 mm, więc nad P12 zostają ok. 3 mm. **Do potwierdzenia w obudowie (pytanie 1).**
- **Wysokość złącza:** z = spód płytki (8,0 / 34,6 / 56,2 / 77,8 / 99,4 / 121,0; format S1, dystanse 25 / 20 / 20 / 20 / 20 mm) + 1,6 + 4,45 mm (oś kątowego IDC, jak R1).
- **Otwory M3 (NPTH 3,2, strefy Ø7 bez miedzi), 8 sztuk:**
  - narożniki (4,5; 8,5), (4,5; 135,5), (155,5; 8,5), (155,5; 135,5);
  - między slotami, w połowie między osiami poziomów 2/3: (53,25; 51,45) i (106,75; 51,45), jak w R1;
  - między slotami, w połowie między osiami poziomów 4/5: (53,25; 94,65) i (106,75; 94,65), nowe.

  W przerwach między slotami nie ma złączy ani taśm. Obrysy gniazd są co najmniej 1 mm poza strefą.
- **Taśmy:** jak R1. Gniazda bez odciążki, taśma prosta (bez skrętu), wychodzi w górę lub w dół i zawija się między krawędzią A a P12. Sąsiednie poziomy są 21,6 mm od siebie.
  - P07 ma dwa gniazda tego samego typu (J12 = J_BP1 w S2, J13 = J_BP2 w S3) z różnymi sieciami. Nie wolno zamienić taśm, więc przy montażu trzeba sprawdzić opis „P07 J_BP1 (poziom 5, S2)” na nadruku.
  - Taśma P11 (J10) jak w R1: w górę, potem w stronę x < 0.
- **Orientacja rzędów** jak w R1: pin 1 od mniejszego x, rząd nieparzysty niżej, pin 2 nad pinem 1 (PDF, strona 5; kontrola „Orientation”, próby `conn_turned` / `rows_swapped`).
- **P07 bez PCB:** środki J_BP1/J_BP2 P07 przyjęto ze slotów (x płytki 26,5 / 80,0; wymagania layoutu w README P07). P04 R3 i P08 R2 zmierzono w ich raportach PCB (26,5 / 80,0 / 133,5 i 26,5).

## Elektryka

- **Łączenie wyłącznie po nazwie sieci, nigdy pin w pin**, z pinoutów płytek (`src/kontrakt.py`). Pliki P04 / P07 / P08 są czytane z gałęzi płytek (`git show`) i porównywane z blobami w `kontrakty.json`.
- **57 sieci (56 + GND), każda z co najmniej dwoma końcami.** Pinów bez połączenia jest 0, a `docs/NIEPODLACZONE.csv` jest pusta. Wszystkie 24 piny, które w R1 zostały wolne, mają teraz drugi koniec.
- **Sieci, które w R2 zyskały końce lub są nowe** (przykłady):
  - SAFE_N: P02 J1.16 → P04 J15.16 i P07 J13.16 (węzeł OC, nadajnik P02);
  - PG_SEND: P02 J1.17 → P04 J15.20;
  - PG_LINK: P02 J1.18 → P04 J15.18 (zwora R34 na P02, P12 jej nie powtarza; kontrola K8);
  - P04_3V3: J1.15 → J15.14;
  - PANEL_3V3 / MECH_OK / STOP_NC_OUT / ARM_CONTACT: P11 J10 → P04 J14;
  - TEST_KEY: P03 J2.14, P11 J10.14 i P04 J14.14;
  - ADC_SCLK / ADC_DOUTA: P03, P05, P06 i P07 J12;
  - SENSOR_PERMIT / SENSOR_OK: P04 J14 → P08 J11;
  - MOTOR_PERMIT / PWM_OUT / ARM_CLK / DRIVE_OK: P04 J15 → P07 J13.
- **5V_SYS:** P02 J1.2/4/6 zasila 16 pinów odbiorników, w tym P08 J11.2/16, P07 J13.10/12 i P04 J16.8 (bez odbiorcy na P04), oraz TP2. Ścieżki mają 1,0 mm.
- **3V3_IO:** P02 J1.8/10 zasila 9 odbiorników, w tym P04 J15.10 / J16.10, P07 J13.14, P08 J11.4, oraz TP3. Ścieżki mają 0,5 mm.
- **Sygnały i GND:** sygnały mają 0,3 mm, odstęp 0,25 mm. GND to wylewka na F.Cu (75,0 %) i B.Cu (83,9 %) oraz 105 przelotek GND.
- **Budżet 5V_SYS stosu pełnego (dokumenty płytek): 1400 mA.** Wobec 1,8 A (90 % TSR 2-2450, 2 A) **nie ma ryzyka.** Przez 3 styki źródła płynie ok. 0,47 A na styk. Najwęższa ścieżka 5V_SYS (1,0 mm) przenosi ok. 2,4 A według IPC-2221 (zewnętrzna, 10 K).

  | Płytka | mA |
  |---|---:|
  | P03 R6 | 500 |
  | P05 R3 | 140 |
  | P09 R2 | 200 |
  | P06 R2 | 180 |
  | P10 R2 | 70 |
  | P08 R2 (TPS2553, cewka, sensor) | 200 |
  | P07 S1 (ok. 30 + cewka KPWR ok. 80) | 110 |
  | P04 R3 (5V_SYS bez odbiorcy) | 0 |

  3V3_IO podają tylko P04 (30 mA), P08 (15) i P07 (≤ 5). Pojemność na szynach 5 V wynosi razem 519,7 µF wobec 600 µF (`P12-przygotowanie`).

## Wyniki (szczegóły: `verification/QA.md`, `verification/QA-PCB.md`)

| Kontrola | Wynik |
|---|---|
| Kontrakty (`P12-przygotowanie`) | 0 błędów, 0 uwag; 56 sieci OK, 0 czeka; próby ujemne 11/11 z zerową (nowe: ryzyko budżetu, brak P07) |
| Kontrakt P12 (`src/kontrakt.py`) | 16 złączy, 276 pinów, 10/10 źródeł z blobami jak w `kontrakty.json`, 0 błędów |
| ERC | 0 naruszeń (1 arkusz) |
| Netlista pin po pinie wobec `parts.py` | 20 części, 280 pinów, 0 błędów |
| Netlista wobec kontraktów (`src/verify_kontrakt.py`, K1–K10) | 10/10. Próby ujemne 22/22 z zerową: zamienione piny (P03, P09, P04, P08), brak sieci (ADC_BUSY, DRIVE_OK), brak końca (CAN_RX, SAFE_N P07), zwarcie 5V_SYS–GND (całe i pin P08), pin w pin P03/P05 J_BP2 (2) i P07/P04 J_BP2.10, zły typ (4), P04_3V3→3V3_IO, mostek PG, TP, dodatkowa część |
| DRC (świeży, wszystkie poziomy, parity) | 0 / 0 / 0 |
| Kontrole PCB (`src/verify_pcb.py`) | 22/22, w tym położenia ±0,5 mm (zmierzone 0,00 mm dla 16 złączy), orientacja, M3 i strefy, szerokości, rozdział zasilań i P03/P05 J_BP2 16/17/19/20, dojście zasilań do źródła, budżet 5V_SYS (nowa), GND, nadruk ≥ 1,0/0,15 z opisem „Jn Pxx J_BPn (poziom k, Sx)” przy każdym złączu |
| Próby ujemne PCB | 25/25 z zerową (nowe w R2: przesunięty P04 J_BP3, podniesiony P07 J_BP1, zła sieć pinu P07, przesunięty nowy otwór H7, zwężona 5V_SYS przy P08) |
| Trasowanie | Freerouting 2.1.0, 1. próba (30 przebiegów). Domknięcie GND J8.3 i pola bez termików zrobiono planerem `complete_routes.py` na tym samym SES (`routing/attempts.json`) |

PDF przeglądowy `output/pdf/P12-R2-PCB.pdf` ma 5 stron: przegląd, montaż 1:1, F.Cu, B.Cu i geometrię z opisem orientacji taśm. Obejrzany 5.10. Schemat: `output/pdf/P12-R2-schemat.pdf`.

## Różnice wobec R1

1. Obrys 160 × 92 → **160 × 136 mm** (z 4…96 → 4…140), 6 → **8 otworów M3**.
2. Nowe gniazda J11–J16 (P08, P07 ×2, P04 ×3); J1–J10 i TP1–TP4 bez zmian położenia.
3. Brak pinów NC: 24 piny R1 bez połączenia mają drugi koniec. Kontrola K8 sprawdza teraz brak pinów jednokońcowych i rozdział PG_SEND / PG_LINK.
4. Budżet 5V_SYS 1,09 → 1,40 A (nowa kontrola PCB), tytuł nadruku „P12 R2 S1 PELNY”.
5. `kontrakt.py` czyta pinouty P04 / P07 / P08 z gałęzi płytek. W kontenerze trzeba zamontować katalog `.git` repozytorium (`EGRLAB_EXTRA_MOUNTS=<repo>/.git`, gdy pracuje się w worktree).
6. W `P12-przygotowanie/zrodla.json` cele SAFE_N płytki P02 (tabela ręczna) uzupełniono o P07, bo P07 czyta i ściąga węzeł OC. To jedyna rozbieżność kontraktów i była oczywista. P02 się nie zmienia.

## Pytania do użytkownika

1. **Wysokość:** P12 R2 sięga z = 140 przy wnętrzu ok. 143 mm. Czy obudowa pełna ma tyle miejsca nad P12 (mocowanie pokrywy, kanał przewodów)? Jeśli nie, górne narożne otwory można zejść do z ≈ 133, a obrys do ok. 137 mm (gniazdo J15/J16 kończy się ok. 131,5).
2. **P07 bez PCB:** J12 / J13 stoją w x 80,0 / 133,5 według slotów. Po layoucie P07 trzeba potwierdzić środki (`pcb_checks` w `zrodla.json`) i puścić kontrole. Przesunięcie o więcej niż 0,5 mm wymaga R3.
3. **Pozostałe pytania R1 nadal otwarte:** odstęp P12 od krawędzi A (18–20 mm) i długość taśmy P11 (zalecana 100 mm do skrócenia).
4. **Po scaleniu** gałęzi p04-r3-pcb / p07-s1-pcb / p08-r2-pcb trzeba zmienić `ref` w `zrodla.json` na `origin/main` i odświeżyć kontrakty (bloby muszą się zgadzać).

## Uruchomienie

Z katalogu pakietu, w worktree z `EGRLAB_EXTRA_MOUNTS=/home/tgorbacz/AI/Claude/EGRLab/.git`:

- schemat: `../../scripts/egrlab-docker python3 src/run_schematic.py` (ok. 10 s);
- całość: `../../scripts/egrlab-docker python3 src/run_release.py`. Odtwarza `routing/P12.ses` i `routing/completion-routes.json`; `--new-route` uruchamia Freerouting od nowa.

## Zawartość

Pliki jak w R1 (`src/`, `eda/`, `docs/`, `routing/`, `output/`, `verification/` z `manifest.json`). Gniazda: Amphenol FCI T821 1xx A1S100CEU lub odpowiednik, 8 × 2×10, 6 × 2×8 i 2 × 2×5. Taśmy: 16 (w tym taśma P11 ok. 100 mm).
