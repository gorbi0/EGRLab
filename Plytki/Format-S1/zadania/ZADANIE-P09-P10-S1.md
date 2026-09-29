# P09 R2 i P10 R2 — schematy w formacie S1 (zadanie dla sesji w chmurze, 29.09.2026)

**Ustawienia sesji:** Sonnet 5.5, wysiłek high. Gałąź `p09-p10-s1`.

**Zakres:** tylko schematy i kontrole, **bez PCB**. Layout robi sesja lokalna.

**Źródła:**
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` (S1-2) i `format-s1.json` — obowiązują;
- zamknięte pakiety `Plytki/P09-R1-review` i `Plytki/P10-R1-review` — nie zmieniać;
- rejestr zakupów `Zamowione/zamowione.csv`.

**Pamięć:** `format-s1.md`, `chmura-limity.md`, `kicad-pipeline-quirks.md`.

## Zasady pracy

Obowiązują zasady 6–9 z `docs/CHMURA.md`:
- commit i push po każdej płytce;
- bez własnych narzędzi trasowania;
- bez procesów dłuższych niż 15 min;
- po dwóch nieudanych próbach zapis stanu i PR.

**Nie zmieniać plików wspólnych:** `EGRLab-AKTYWNE.md`, `docs/01-overview.md`, `docs/CHMURA.md`, `docs/pamiec-claude/`, `scripts/`, `Plytki/Format-S1/`, `.gitignore`.

## Dla każdej płytki: nowy pakiet `Plytki/P09-R2-review` i `Plytki/P10-R2-review`

Każdy pakiet powstaje na kopii łańcucha z R1.

1. **Złącze płytki połączeń J_BP:**
   - kątowe, obudowane IDC 2×5 (2×8, jeśli nie wystarczy), na krawędzi A, środek slotu;
   - zastępuje złącza wiązek do innych płytek:
     - P09: J1 LV09 i J2 TEMP;
     - P10: J1 LV10 i J2 CAN_CORE;
   - **pinout:** piny nieparzyste to GND, a sygnały i zasilanie idą na parzyste. Zasilanie bierzemy tylko takie, jakiego płytka używa (5V_SYS i/lub 3V3_IO z dawnego LVxx).
2. **Połączenia zewnętrzne zostają:**
   - P09: gniazda modułów MAX31856 i wejścia termopar;
   - P10: J3 OBD (skrętka do gniazda OBD).
3. **Listwa serwisowa na krawędzi B:** kątowy goldpin 1×N, N ≤ 13, GND na pierwszym i ostatnim pinie.
   - Treść: punkty z `docs/ODBIOR.md` R1, co najmniej zasilania płytki i sygnały do P03.
   - Każdy kołek poza GND przez rezystor szeregowy przy węźle: 1 kΩ dla szyn do 5 V i logiki, 10 kΩ dla węzłów wysokoimpedancyjnych.
4. **Części:**
   - rezystory i kondensatory, których wartość i typ są w `Zamowione/zamowione.csv`: THT, rezystory na stojąco;
   - pozostałe: SMD 1206 (od spodu wolno SMD ≤ 1,5 mm);
   - klasa płytki: 1/3 (53 × 100 mm), P09 w slocie S3 poziomu 3, P10 w slocie S1 poziomu 1.
5. **Kontrole:**
   - ERC 0;
   - netlista pin po pinie z `parts.py`;
   - kontrole elektryczne z R1 poprawione pod nowe złącza;
   - nowe kontrole z próbami ujemnymi:
     - każdy pin nieparzysty J_BP to GND;
     - każdy kołek serwisowy poza GND ma rezystor przy węźle;
     - na końcach listwy jest GND;
   - próba zerowa.
6. **Pliki dla płytki połączeń P12:**
   - `docs/J_BP.csv`: kolumny `pin;siec;kierunek;plytka_docelowa;uwagi`;
   - `docs/SERWIS.csv`: kolumny `pin;siec;rezystor;cel_pomiaru`.
7. **README pakietu:** tabela zmian R1 → R2, liczby z kontroli, lista otwartych punktów.

## Wynik

PR po polsku z obiema płytkami. Pytania wpisać do opisu PR. Nie włączać śledzenia PR, a po otwarciu PR zakończyć pracę.
