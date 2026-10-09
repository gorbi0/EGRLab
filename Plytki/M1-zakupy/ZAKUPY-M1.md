# M1-R1 — co już jest, co dokupić

*9.10.2026. Porównanie BOM M1-R1 (`Plytki/M1-R1-review/docs/BOM.csv`, `zakupy.csv`) z rejestrem `Zamowione/` (TME, Mouser, Kamami 24.09) i modułami posiadanymi przez użytkownika. Ilości na **jedną zmontowaną płytkę**; dostępności w sklepach nie sprawdzano.*

Założenie: M1 zastępuje stos S1. Jeśli S1 też będzie składany, kolidują: TSR 2-2450 / 2-2433 (po 1 szt., kupione dla P02), AD7606B, ESP32-S3, MAX31856 ×2.

## 1. Już masz — idzie na M1

| Część | Masz | M1 | Pozycje | Źródło |
|---|---:|---:|---|---|
| TRACO TSR 2-2450 | 1 | 1 | U1 | Mouser 24.09 (było dla P02) |
| TRACO TSR 2-2433 | 1 | 1 | U2 | Mouser 24.09 (było dla P02) |
| 74LVC125AD,118 | 25 | 1 | U5 | Mouser 24.09 |
| INA240A2EDRQ1 | 2 | 1 | U4 | Mouser 24.09 (druga sztuka zapasem) |
| AD7606BBSTZ (LQFP-64) | 1 | 1 | U3 | posiadany, goły układ (potwierdzone 9.10) |
| Waveshare ESP32-S3-DEV-KIT-N32R16V | 1 | 1 | M1 | posiadany; **wylutować D1** (M1-01) |
| MAX31856 XU | 2 | 2 | TC1, TC2 | posiadane (Allegro), pomiar 8.10 zgodny |
| IBT-2 (2× BTS7960B) | 1 | 1 | poza płytką | posiadany |
| Adafruit 4682 (microSD) | 1 | 1 | SD1 | posiadany (potwierdzone 9.10; poza rejestrem `Zamowione/`) |
| goldpin 1×40 | 9 | 2 | listwy 2×1×22 pod ESP32 | Kamami 24.09 (jeśli moduł nie ma własnych) |
| dystans M3×10 poliamid, śruby, nakrętki, podkładki M3 | 10 / 100 | 4 kpl. | otwory montażowe | TME 24.09 |
| tulejki WAGO 216-206 (2,5 mm²) | 6 | wg potrzeb | przewody 2,0 mm² na X1 | TME 24.09 |
| opaski 2,5×100 | 100 | kilka | otwory na opaski przy polach | TME 24.09 |

Z rejestru nic więcej nie pasuje: pasywne z 24.09 są przewlekane (THT), a M1 ma wyłącznie SMD 1206 / 1210 / 2512.

## 2. Do kupienia — części na płytkę

**Uwaga:** w `M1-R1-review/docs/zakupy.csv` pozycje U6, D1, U8 mają źródło „rejestr”, ale **nie były zamówione** (były tylko na liście 2). Kupić.

### Układy i części mocy

| MPN | Szt. | Pozycje | Uwagi |
|---|---:|---|---|
| TCAN1051VDRQ1 (TI) | 1 | U6 | |
| PESD2CAN,215 (Nexperia) | 1 | D1 | |
| TPS2553DBVR (TI) | 1 | U8 | SOT-23-6 |
| 74AHCT125D,118 (Nexperia) | 1 | U7 | wejścia TTL, nie zamieniać na LVC/HC |
| WSK25125L000FEA (Vishay) | 1 | RSH1 | 5 mΩ 1 %, 2512 Kelvin — tylko ten footprint |
| C3225X7R1E226M250AB (TDK) | 2 | C14, C15 | 22 µF / 25 V X7R 1210 |
| Littelfuse 0297007.WXNV | 1 + zapas | F1 | MINI 7,5 A / 32 V |
| Keystone 3568 | 1 | F1 | oprawka MINI lutowana |

### Rezystory 1206, 1 % (Yageo RC1206FR-07…)

| Wartość | MPN | Szt. | Pozycje |
|---|---|---:|---|
| 0 Ω | RC1206FR-070RL | 2 | R24, R26 |
| 1 Ω | RC1206FR-071RL | 1 | R7 |
| 33 Ω | RC1206FR-0733RL | 1 | R8 |
| 100 Ω | RC1206FR-07100RL | 1 | R30 |
| 1 k | RC1206FR-071KL | 1 | R21 |
| 4,7 k | RC1206FR-074K7L | 1 | R2 (pull-down GPIO39 — nie 100 k) |
| 10 k | RC1206FR-0710KL | 6 | R1, R6, R9, R28, R29, R32 |
| 47 k | RC1206FR-0747KL | 1 | R10 |
| 100 k | RC1206FR-07100KL | 3 | R3, R4, R5 |
| 232 k | RC1206FR-07232KL | 1 | R31 (limit TPS2553) |

R25, R27 — DNP, nie kupować.

### Rezystory 1206, 0,1 % cienkowarstwowe (Yageo RT1206BRD07…)

| Wartość | MPN | Szt. | Pozycje |
|---|---|---:|---|
| 10 Ω | RT1206BRD0710RL | 2 | R22, R23 |
| 100 k | RT1206BRD07100KL | 7 | R12, R14–R17, R19, R20 |
| 300 k | RT1206BRD07300KL | 2 | R11, R13 |
| 499 k | RT1206BRD07499KL | 1 | R18 |

### Kondensatory 1206

| Wartość | Typ | Szt. | Pozycje |
|---|---|---:|---|
| 100 nF | X7R 50 V 10 % | 13 | C4, C6–C10, C13, C24–C29 |
| 1 µF | X7R 50 V 10 % | 3 | C11, C12, C30 |
| 4,7 µF | X7R 50 V 10 % | 1 | C1 (wejście pakietu) |
| 10 µF | X7R 16 V 10 % | 3 | C2, C3, C5 |
| 220 pF | C0G 50 V 5 % | 7 | C16–C22 (filtry AD7606B) |
| 1 nF | C0G 50 V 5 % | 1 | C23 |

Pasywne kupuje się w paczkach (minimum sklepu) — zapas na drugą płytkę wychodzi sam.

## 3. Do kupienia — poza płytką

| Co | Uwagi |
|---|---|
| X1: listwa śrubowa 16 torów, ≥ 10 A | do wyboru razem z obudową: złączki na szynę DIN (np. Phoenix UT 2,5 + pokrywa końcowa + odcinek szyny) albo listwa barierowa 16-torowa na panel. Mostki: X1.4 ↔ X1.2 stały, X1.13 ↔ X1.3 w trybie TEST (zacisk nie sąsiedni — kawałek przewodu) |
| wyłącznik pakietu na obudowie | w torze X1.1 (BAT+ za BMS); ≥ 10 A DC przy 16,8 V |
| przycisk START / STOP | chwilowy NO, **styki złocone** (obwód suchy, 3,3 V / 10 k) |
| bezpieczniki MINI 7,5 A zapasowe | 2–3 szt. (razem z F1) |
| dławnice | liczba i rozmiar wg obudowy: pakiet, wiązka EGR strona ECU, wiązka EGR strona zaworu, akumulator / masa auta + CAN, 2× termopara (osobna dławnica, D-M1-8) |
| przewód 2,0 mm² | czerwony, czarny + 2 inne kolory (P1 ECU / P1 EGR, IBT-2 M+ / M−) |
| przewód 0,25 mm² w kilku kolorach | X1.7–X1.10, X1.13, X1.16 (6 żył), J3 przycisk (2), J4 IBT-2 logika (6) |
| przewód 0,5 mm² | X1.11 SENS_5V, X1.12 GND |
| skrętka do CAN | X1.14 / X1.15 (+ X1.16 GND 0,25 mm²) |
| tulejki 0,25 / 0,5 mm² | do X1; dla 2,0 mm² są WAGO 2,5 mm² z TME |
| pakiet 4S + BMS 40 A | jeśli jeszcze nie masz |
| obudowa | po przymiarce do PCB |

## 4. Uwagi montażowe związane z zakupami

- D1 na module Waveshare wylutować przed pierwszym zasileniem (najpierw potwierdzić oznaczenie diody na posiadanym egzemplarzu).
- R2 = 4,7 k (nie 100 k) — GPIO39 ma po resecie wewnętrzne podciąganie ok. 45 k.
- AD7606BBSTZ jest jeden, w LQFP 0,5 mm — ewentualna druga sztuka na wypadek uszkodzenia przy lutowaniu to decyzja użytkownika.

## 5. Lista do Mousera — `MOUSER-M1.csv`

28 pozycji, 121 szt.: wszystkie części z punktu 2 z zapasem (układy ×2, drobne pasywne zaokrąglone). Kontrola z `zakupy.csv`: 27/27 pozycji BOM pokrytych, ilości ≥ potrzeby. Mouser, bo TME (lista 2, 28.09) nie miało w detalu 232 k 1 %, C3225X7R1E226M250AB sprzedawało tylko po 1000 szt., a TPS2553DBVR miało 5 szt. **Stanów i cen nie sprawdzano** (Mouser blokuje zapytania automatyczne).

Wczytanie: mouser.pl → Narzędzie BOM (BOM Tool) → wgraj CSV, kolumna „Mfr Part Number” jako numer producenta, „Quantity” jako ilość, „Customer Part Number” jako numer klienta (oznaczenia z płytki trafią na etykiety woreczków). Pozycje bez dopasowania albo bez stanu — zamienniki:

| Pozycja | Zamiennik |
|---|---|
| RC1206FR-07232KL | Vishay CRCW1206232KFKEA albo Panasonic ERJ-8ENF2323V |
| RT1206BRD07… (0,1 %) | Panasonic ERA-8AEB…V (np. ERA-8AEB104V = 100 k), Vishay TNPW1206…BE |
| C3225X7R1E226M250AB | Samsung CL32B226KAJNNNE, Murata GRM32ER71E226KE15L |
| kondensatory 1206 | dowolne tej samej wartości, napięcia i dielektryka (X7R / C0G) |
| WSK25125L000FEA | bez zamiennika — footprint Kelvin WSK2512 |

Nie ma na liście (poza płytką, punkt 3): listwa X1, wyłącznik pakietu, przycisk, dławnice, przewody, tulejki — do wyboru z obudową.
