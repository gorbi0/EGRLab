# P00 FIXTURE — karta założeń schematu i PCB (R1)

25.09.2026 · Claude. Karta spisana po decyzjach użytkownika, razem ze schematem. Źródła: import pinowy P00 z v6.1-rc1 (`reference/v6.1-P00-import.xml`), BOM v6.1 (`reference/v6.1-P00-BOM.csv`), `docs/03-uruchomienie.md` §0 i `verification/ODBIOR.csv` z v6.1 (`reference/v6.1-P00-ODBIOR.csv`). Do recenzji: Astra.

## Rola płytki

P00 to wyposażenie stołu, nie część zestawu w aucie. Zastępuje źródła sygnałów przy odbiorze pojedynczej płytki, głównie P04 SAFE: „wszystkie kombinacje wymaganych sygnałów dodatnich, oba gniazda LOGGER, klucz, pętla TEST, STOP, odłączenie heartbeat” (v6.1, §4). Daje osiem przełączanych poziomów 3,3 V/GND przez 1 kΩ i heartbeat ok. 102 Hz z TLC555 dla próby watchdoga.

## Decyzje użytkownika (25.09.2026)

1. **P00 jako następna płytka** (kolejność v6.1: P01/P02/P00 → CORE i DAQ…).
2. **Wyjścia na listwach 2,54 mm 1 × 2** — przewody Dupont nasadzane wprost na piny złączy badanej płytki.
3. **Zasilanie 5–15 V z własnym stabilizatorem 3,3 V** zamiast samego 3,3 V ze stołu (v6.1).
4. **Dioda LED stanu przy każdym kanale.**

## Funkcja i sieci

| Blok | Połączenia |
|---|---|
| Zasilanie | J10 (MKDS 2p): 1 = +VIN 5…15 V, 2 = GND → D1 1N5819 (odwrotna polaryzacja) → C4 10 µF + C5 100 nF → U2 LM2937ET-3.3 → C6 22 µF + C7 100 nF → P00_V33; LED10 czerwona przez 1 k |
| Kanały 1–8 | SWn: COM → RSn 1 k → Jn pin 1; Jn pin 2 = GND; LEDn zielona przez RLn 1 k z węzła przełącznika (nie z wyjścia) |
| Heartbeat | U1 TLC555CP (DIP8 w podstawce): R1 4k7, R2 68k, C1 100 nF → f = 1,44/((R1 + 2·R2)·C1) = 102 Hz; C2 10 nF (CTRL), C3 100 nF; wyjście przez R3 1 k na J9; LED9 żółta przez RL9 z wyjścia 555; SW9 RUN/STOP na RESET z R4 100k do 3V3 |
| Pomiar | TP1 3V3, TP2 GND, TP3 VIN za D1 |

## Wymagania przeniesione z v6.1

- Każde wyjście przez 1 kΩ: przy zwarciu do masy lub pomyłkowym wpięciu w wyjście innej płytki prąd ≤ 3,3 mA.
- GND przyrządu łączyć z GND badanej płytki (drugi pin każdej listwy).
- Przełączniki SPDT ON-ON; heartbeat 3,3 V, ok. 102 Hz, zmierzyć częstotliwość (ODBIOR P00).
- P00 odpinany przed integracją; zworki udające gotowość nie mogą zostać w kompletnym TESTER-ze.

## Decyzje projektowe R1 (do recenzji)

| Decyzja | Uzasadnienie |
|---|---|
| **Przełącznik Würth WS-SLTV 450301014042**; symbol SPDT przenumerowany (wspólny = pin 1) | Footprint zweryfikowany w bibliotece KiCad, raster 2,54 mm. Karta Würth: COM to środkowy pin 1, styki 2 i 3; „opposite side connection” — suwak łączy COM ze stykiem po przeciwnej stronie. Ogólny symbol KiCad ma COM na pinie 2 i bez przenumerowania spiąłby styk z COM |
| Pin 2 = 3V3, pin 3 = GND, pin 3 u góry | Przy tej semantyce suwak w górę = H, co jest na nadruku; kontrola w `verify_pcb.py` na wszystkich 9. **Potwierdzić omomierzem na pierwszym egzemplarzu** — LED i tak pokazuje prawdziwy stan |
| LM2937ET-3.3 + D1 1N5819 | Karta TI (SNVS100F): wejście do 26 V ciągle, 60 V impulsowo, VIN ≥ VOUT + 1 V, Cout ≥ 10 µF przy ESR < 3 Ω, θJA TO-220 77,9 °C/W. Przy 15 V i najgorszym przypadku (wszystkie wyjścia zwarte, ok. 45 mA) strata ok. 0,5 W → +40 K. D1 odcina odwrotną polaryzację przed C4 (LM2937 sam ją znosi, elektrolit nie) |
| **SW9 RUN/STOP heartbeatu** (dodatek, nie z v6.1) | Pozycja STOP trzyma RESET 555 w stanie niskim, więc wyjście stoi w L: zablokowany heartbeat bez rozpinania przewodu. R4 100k utrzymuje RESET wysoko w chwili przełączania |
| LED kanału z węzła przełącznika, przed 1 kΩ | Stan jest widoczny także przy zwartym wyjściu; LED nie obciąża wyjścia |
| Płytka 115 × 70 mm, 2 × 35 µm, M3 5 mm od narożników | Przyrząd stołowy, poza stosem modułów; prądy < 50 mA, 35 µm wystarcza |
| Kolumny kanałów prowadzone ręcznie i zablokowane | Freerouting w tym gęstym wzorze zostawił dwa połączenia 3V3 niepoprowadzone; ręczny wzór jest powtarzalny i czytelny |

## Poza zakresem R1

Przewody Dupont i ich oznaczenia do konkretnych złączy P04, obudowa lub nóżki, odbiór sprzętu (ODBIOR P00). Sprzęt: NIE ZBADANO.
