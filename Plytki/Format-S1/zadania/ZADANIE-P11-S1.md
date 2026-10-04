# P11 R2 — schemat panelu w formacie S1 (zadanie dla sesji w chmurze, 4.10.2026)

**Ustawienia sesji:** Opus 5.5, wysiłek high. Baza: `origin/zamowienie-s1`, bo lokalny main nie jest jeszcze wypchnięty. Gałąź zadania: `p11-r2-schemat`, wynik jako PR do `zamowienie-s1`.

**Zakres:** tylko schemat, kontrole i dokumenty, **bez PCB**. Layout robi sesja lokalna (`docs/CHMURA.md`, zasada 6).

**Źródła:**
- `Plytki/P11-S1-przygotowanie/README.md` — fakty, zmiany wokół P11 i **decyzje 4.10** (obowiązują);
- zamknięty pakiet `Plytki/P11-R1-review` — wejście (logika styków R1, kontrola 64 kombinacji); nie zmieniać;
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` §7, §8, §10;
- kontrakty P12: `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md` — sieci czekające na P11: MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT (P03 R6 J_BP1.13–16), N_J_SCOPE_HOT (J_BP1.10);
- wzór łańcucha S1 (parts.py, build_schematic.py, verify_s1.py, negative controls): `Plytki/P06-R2-review/src`.

**Pamięć:** `docs/pamiec-claude/MEMORY.md` (indeks), `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`.

## Zasady pracy

Obowiązują zasady 1–9 z `docs/CHMURA.md`:
- commit i push po każdym etapie;
- bez procesów dłuższych niż 15 min;
- po dwóch nieudanych próbach zapis stanu i PR.

**Nie zmieniać:** `EGRLab-AKTYWNE.md`, `docs/`, `scripts/`, `Plytki/Format-S1/`, zamkniętych pakietów (`…-review` innych płytek, `…-zamowienie`), `.gitattributes`.

## Decyzje użytkownika (4.10.2026)

| Nr | Decyzja |
|---|---|
| P11-1 | P11 **odchudzona**: logika styków (kluczyk, STOP, ARM, MARK, pętle NC L1/L2, TEST_PRESENT, MECH_OK) i złącze IDC 2×10 do P12 (S1 §8: PANELCORE + PANELSAFE). Porty łączone przewodami wprost. |
| P11-2 | Porty L1 / L2 / TEST na panelu: **Amphenol AT04-12** (klon DT), klucze A / B / C, styki 13 A. Złącza nie leżą na P11; na P11 tylko pola przewodów dla pinów sygnałowych portów (pętle, TEST_PRESENT, MECH_OK, LOOP_OUT). |
| P11-3 | Zasilanie styków w LOGGER: **3V3_IO z P12** (pin J_BP.14 P06 R2) przez **100 Ω na P11**, montowany tylko bez P04; przy P04 nieobsadzony (DNP, notatka w BOM i na schemacie). Przy P04 PANEL_3V3 jak w R1 (R40 na P04). |
| P11-4 | Prąd silnika (ECU_P1, EGR_P1, T_EGR_P1 / P3) **przewodami z portów wprost do P06 / P07**; P11 bez prądu silnika. |
| P11-5 | TAPS (P05 J4) i ISERIES (P06 J3) **lutowane przewody**; bez J7 Mini-Fit i J1 MSTB na P11. |
| P11-6 | Układ panelu: rysunek makiety 1:1 robi sesja lokalna. P11 ma się zmieścić za panelem obok SW1 P05, BYPASS P06, PWR P02 z LED, 3 × AT04, 2 × BNC, kluczyka, STOP, ARM, MARK — proponuj jak najmniejszą płytkę. |
| P11-7 | **Zwykłe przyciski ze stykami złoconymi** (do małych prądów, ok. 27 µA / 3 V); bez zmian rezystorów na P03 R6. |

## Do zrobienia — pakiet `Plytki/P11-R2-review`

1. Obwód z R1 bez torów silnika, J1 / J7 i wiązek W3 / W4 / W5–W7 (porty: tylko piny sygnałowe na polach przewodów). Lista sieci R1 → R2 w README z uzasadnieniem każdej zmiany.
2. Złącze do P12: IDC 2×10 (S1 §8). Pinout zgodny z P03 R6 J_BP1 (MARK 13, TEST_KEY 14, LOGGER_CLEAR 15, TEST_PRESENT 16, N_J_SCOPE_HOT 10) i z PANELSAFE dla P04 (PANEL_3V3, MECH_OK, STOP_NC_OUT, ARM_CONTACT); GND co drugi pin, gdzie się da. Plik `docs/J_P12.csv` w formacie `J_BP.csv` innych płytek.
3. R 100 Ω z 3V3_IO (P11-3) z pozycją DNP w wariancie z P04 i kontrolą, że przy obsadzonym R nie ma drugiego źródła na PANEL_3V3.
4. Kontrole: ERC 0, symulacja kombinacji styków jak w R1 (wszystkie kombinacje, oba warianty: z P04 i LOGGER bez P04), zgodność J_P12 z kontraktami P12, próby ujemne (np. zamieniony pin, brak R, R obsadzony przy P04), PDF schematu.
5. BOM: przyciski z wymaganiem styków złoconych (bez MPN, kody wybiera osobne zadanie zakupowe), pola przewodów z przekrojami.
6. README pakietu: co zrobione, otwarte pytania (dla użytkownika w opisie PR).

Po PR zakończyć pracę (zasada 5).
