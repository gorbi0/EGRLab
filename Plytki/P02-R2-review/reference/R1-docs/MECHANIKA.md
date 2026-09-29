# P02 R1 — mechanika, montaż, serwis

25.09.2026 · Claude. Wysokości części to wartości katalogowe lub szacunkowe — przy przymiarce 1:1 zmierzyć je na posiadanych egzemplarzach.

## Płytka i mocowanie

Format i otwory jak P01 (160 × 120 mm, M3 w narożnikach 5 mm od krawędzi), więc płytki mogą stać w jednym stosie lub obok siebie na tej samej siatce otworów. W promieniu 4,5 mm od środka otworu nie ma żadnego elementu (łeb śruby i podkładka).

## Wysokości nad płytką

| Element | Wysokość (orientacyjnie) | Uwaga |
|---|---|---|
| C1–C3 bank 22 mF / 35 V | 45 mm korpusu + zatrzaski | nad wieczkami (zawór) ≥ 3 mm wolnej przestrzeni; nic nie może ich dociskać |
| D1, D2 TO-220 pionowo | ok. 20 mm | bez radiatorów; tab = katoda (D1: VLOG_RES, D2: HOLD_FUSED) |
| F1–F4 oprawki PTF78 + wkładka 5 × 20 | ok. 10–12 mm | wkładki wymienialne od góry |
| U1, U2 TSR 2 | ok. 10–11 mm | |
| J3–J11 Mini-Fit Jr pionowe | ok. 10 mm, z wtykiem i przewodem ok. 25–30 mm | zatrzask od strony dolnej krawędzi |
| U5 na adapterze SO14 | ok. 8–11 mm | zależy od długości kołków goldpin |

Konsekwencja dla stosu: nad P02 potrzeba co najmniej ok. 50 mm (bank + zawór). Praktyczniej postawić P02 na górze stosu albo obok. To decyzja obudowy — poza zakresem R1.

## Wiązki i złącza

| Złącze | Kierunek wyjścia | Mocowanie |
|---|---|---|
| J1 SUPPLY (2 × 2,5 mm², od P01 J6) | w lewo, za lewą krawędź | lutowane, opaska w otworach Ø4,2 mm 12,5 mm od lutów |
| J2 VMOTOR (GMSTBA 2,5/3-G-7,62) | wtyk wsuwany od lewej krawędzi, czoło gniazda 0,6 mm od krawędzi | wtyk P07 musi być GMSTB 7,62 (odstępstwo od PC 4 w v6.1) |
| J13 R_CHARGE (2 × AWG20) | w górę, za górną krawędź | lutowane, opaska w otworach Ø3,2 mm 12,5 mm od lutów |
| J12 PSUOK (taśma 6 × AWG28) | w prawo, za prawą krawędź | lutowane, opaska 12,5 mm od lutów |
| J11 VSENSE, J3–J10 LV03–LV10 | pionowo w górę | wtyki z zatrzaskiem; nazwy LV pod złączami |

## R_CHARGE poza płytką

HSA2547RJ (47 Ω / 25 W) mocować do osobnej blachy aluminiowej zgodnie z warunkami TE, z dala od banku; nigdy nie zastępować rezystorem 0,5 W. Moc: ≤ 7,26 W przy 18 V, ≤ 22,94 W chwilowo przy 32 V i przy zwartym banku — temperaturę blachy sprawdzić w obu przypadkach. Przewody AWG20 do J13 (1 = VPROT, 2 = CHG), pinout nieistotny elektrycznie (rezystor), istotne jest tylko, żeby nie trafiły do innego złącza.

## Bank — bezpieczeństwo przy pracy

Energia banku przy 32 V i górnej tolerancji przekracza 40 J. Luty zacisków C1–C3 po stronie B.Cu trzeba osłonić (np. przekładka izolacyjna pod bankiem przy montażu na dystansach), puszki mają własne koszulki. Bleeder 4k7 rozładowuje bank do < 1 V w ok. 19 min; przed pracą zmierzyć napięcie na TP3. Do serwisowego rozładowania zewnętrzny rezystor 100 Ω / 10 W na izolowanych przewodach — nie zwierać zacisków. Te same ostrzeżenia są na nadruku: przy TP3 i pod puszką C3.

## Kolejność montażu (propozycja)

1. Elementy niskie: rezystory, 100 nF, podstawka DIP14 (U6), TO-92 (U3, U4, U8 — U8 ma układ wyprowadzeń TI LP: 1 = K, 2 = A, 3 = REF).
2. Adapter U5: najpierw SO14 na adapterze, potem kołki, na końcu adapter na płytkę (pin 1 = kółko na nadruku).
3. Kondensatory 5 mm (polaryzacja „+” na nadruku), LED1 (płaska strona = katoda).
4. Oprawki F1–F4, przetwornice U1/U2, D1/D2 (gruba linia nadruku = strona taba).
5. Złącza J2, J3–J11; przewody J1, J12, J13 z opaskami.
6. Na końcu bank C1–C3 („+” na dolnym padzie, pasek „−” w stronę górnej krawędzi). Pierwsze włączenie przez zasilacz z ograniczeniem prądu, zgodnie z odbiorem C1.
