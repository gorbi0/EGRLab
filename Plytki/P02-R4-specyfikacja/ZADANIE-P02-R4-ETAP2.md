# P02 R4, etap 2 — PCB w formacie S1 (pilot); zadanie dla sesji w chmurze

*Wersja 2.1, 29.09.2026: dopuszczony montaż SMD od spodu (format S1-2).*

*Wersja 2, 29.09.2026. Zmiany względem wersji 1:*
- *format S1 zamiast obrysu 115 × 85 mm;*
- *złącze płytki połączeń zamiast ośmiu złączy LV i wiązek sygnałowych;*
- *listwy serwisowe na krawędzi B;*
- *posiadane rezystory THT montowane na stojąco.*

*Wersja 1 jest nieaktualna.*

**Źródła (obowiązujące):**
- `Plytki/Format-S1/SPECYFIKACJA-FORMATU-S1.md` i `Plytki/Format-S1/format-s1.json`;
- pakiet `Plytki/P02-R4-review` (etap 1, scalony w PR #2);
- recenzja `Plytki/P02-R4-recenzja/RECENZJA-P02-R4-ETAP1.md`;
- `SPECYFIKACJA-P02-R4.md`: Z-01…Z-14 i plan odbioru O-01…O-09 (sekcja 10); wymiary z Z-15 zastępuje format S1;
- łańcuch PCB z `Plytki/P02-R3-review/src`.

**Pamięć:** `kicad-pipeline-quirks.md`, `p02-r1-state.md`, `p01-pcb-r1-review.md`, `format-s1.md`.

**Ustawienia sesji:** Opus 5.5, wysiłek high. Gałąź `p02-r4-pcb`. Pakiet `Plytki/P02-R4-review` pozostaje otwarty.

## Praca równoległa

Może równolegle działać inna sesja. **Nie zmieniać plików wspólnych:**
- `EGRLab-AKTYWNE.md`;
- `docs/01-overview.md`;
- `docs/CHMURA.md`;
- `docs/pamiec-claude/`;
- `scripts/`;
- `Plytki/Format-S1/`;
- `.gitignore`.

Wolno zmieniać `Plytki/P02-R4-review/` i `Plytki/P02-R4-specyfikacja/STAN-PRAC.md`. Środowisko: `bash scripts/setup-chmura.sh`.

## 1. Schemat (osobny commit)

**Decyzje po recenzji etapu 1:**
- D3: 5KP18A → 5KP24A.
- J15: w opisie BOM bezpiecznik 1 A przy klemie.
- T14: dodać kontrolę Z-01 (VBR min transila ≥ 25 V) z próbą ujemną 5KP18A.
- QA „Zgodność ze specyfikacją”: według nowego brzmienia Z-02 i Z-08.

**Zmiany wynikające z formatu S1:**
- **Nowe złącze płytki połączeń:** usunąć J3–J10 (LV), J11, J12, J13 i J16, a w ich miejsce dodać J_BP. To kątowe, obudowane złącze IDC 2×10 z pinoutem z tabeli w §8 specyfikacji formatu. Zwora PG_SEND–PG_LINK zostaje na płytce.
- **Połączenia przewodami:** J1 BAT, J2 VMOTOR, J14 PWR i J15 VBAT_IN zostają jako przewody.
- **Listwy serwisowe J_SV1 (slot S2) i J_SV2 (slot S3):**
  - kątowe kołki goldpin, najwyżej 13 pinów w każdej, GND na pierwszym i ostatnim pinie;
  - punkty z planu odbioru O-01…O-09, co najmniej: BAT_IN, VSW, VLOG, HOLD_C, GATE, UV_DIV, REF, AUX5, OK/ENABLE, PFAIL_N, SAFE_N, PSU_OK, 5V_SYS, 3V3_IO, VBAT_SENSE;
  - każdy kołek poza GND przez rezystor szeregowy według §6 specyfikacji formatu (1 kΩ / 4,7 kΩ / 10 kΩ).

  Dotychczasowe pola testowe TP1–TP17 można usunąć, jeśli ich punkt jest na listwie.
- **Rezystory:** jeśli wartość i typ są w `Zamowione/zamowione.csv` (zakupy P01), stosujemy THT na stojąco (np. P5.08 pionowo). Pozostałe rezystory to SMD 1206, a rezystory mocy (PR02) leżą. Kondensatory THT z zakupów zostają, nowe ceramiczne to SMD.
- **Wysokości:** poziom 1 jest wysoki, więc każdy element może mieć ≤ 21,5 mm. TO-220 może stać z nóżkami skróconymi do 4 mm. C_H (16 × 25 mm) leży i potrzebuje własnego footprintu z obrysem korpusu na płytce. Wysokości wpisać do `parts.py` i sprawdzić kontrolą.
- **Kontrole elektryczne:** poprawić kontrole odwołujące się do usuniętych złączy (np. T02, T13, T07, T08). Powtórzyć ERC, netlistę, `check_electrical` i próby ujemne.

## 2. PCB

- **Klasa i położenie:** 2/3, sloty S2–S3 poziomu 1. Obrys 106,5 × 100,0 mm, osiem otworów M3 według `format-s1.json` (x = 4, 49, 57,5, 102,5; y = 14, 86).
- **Jeśli się nie zmieści:** gdy płytka nie mieści się w klasie 2/3 z zachowaniem reguł, przejść na klasę L (160 × 100) i opisać powód w PR.
- **J_BP:** na krawędzi A, środek w x = 80,0 mm (slot S3 płytki), pin 1 od strony mniejszego x.
- **J_SV1 i J_SV2:** na krawędzi B, w x = 10–43 mm każdego slotu; kołki wystają ok. 6 mm za krawędź.
- **Złącza zewnętrzne:** J1 BAT, J2 VMOTOR i J15 VBAT_IN przy krótkiej krawędzi x = 106,5 (ściana wejść). J14 PWR w dowolnym dogodnym miejscu.
- **Tory 5 A:** J1 → Q9 → SW_COM → Q1 → VSW → F1 → J2 oraz powrót GND. Szerokie ścieżki albo wylewki, ≤ 20 K przyrostu przy 5 A według IPC-2152 dla 35 µm.
- **TO-220:** blaszka tylko na miedzi swojej sieci.
- **Odsprzęganie przy pinach**, jak w wersji 1 zadania:
  - C2/C4 przy Q1/Q2, C8/C10 przy U1, C11 przy U2, C13 przy R12/U2;
  - C25–C29 przy U7–U10, C21–C24 przy TSR;
  - C_H, D2 i D1 blisko siebie.
- **Strefy dystansów:** Ø 7 mm bez elementów i bez miedzi innych sieci. Wyprowadzenia THT przycinane do ≤ 1,5 mm.
- **Montaż od spodu (S1-2):** wolno SMD ≤ 1,5 mm, a SOIC na poziomie 1 (P02 R4) też. Od spodu mogą trafić: nowe rezystory i kondensatory SMD, rezystory szeregowe kołków serwisowych (pod listwą) i U9 74LVC125A w SOIC bez adaptera. Część ta sama co w zakupach: 74LVC125AD, obudowa SO14. Odległość ≥ 1 mm od pól THT; nadruk od spodu.
- **Reguły produkcyjne** jak P02-R3 (pierścień ≥ 0,25 mm). Na nadruku `P02 R4 S1-2/3 S2–S3`, znaczniki krawędzi A i B oraz opisy kołków.

## 3. Kontrole

- DRC 0/0/0.
- `verify_pcb.py` sprawdza:
  - obrys i otwory względem `format-s1.json`;
  - położenie i pinout J_BP;
  - listwy serwisowe (położenie, GND na końcach, rezystor szeregowy przy każdym węźle);
  - wysokości ≤ 21,5 mm;
  - tory 5 A, odsprzęganie, blaszki TO-220 i strefy dystansów.
- Próby ujemne z próbą zerową, np.:
  - otwór przesunięty o 0,5 mm;
  - J_BP przesunięte;
  - listwa bez GND na końcu;
  - kołek bez rezystora;
  - element za wysoki;
  - przewężenie toru 5 A;
  - odsunięty kondensator;
  - blaszka Q1 na obcej miedzi.
- PDF: warstwy, montaż i wydruk 1:1 do przymiarki.

## 4. Poza zakresem

Paczka produkcyjna i zamówienie; zrobi je sesja lokalna po recenzji.

## Wynik

PR po polsku, w nim:
- klasa (2/3 czy L) i wymiary;
- tabela zmian schematu;
- wyniki kontroli z liczbami;
- podgląd płytki;
- lista otwartych punktów.

Pytania wpisać do opisu PR. Nie włączać śledzenia PR.
