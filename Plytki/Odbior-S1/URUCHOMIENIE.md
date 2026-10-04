# Uruchomienie i odbiór sprzętu S1 (LOGGER) — procedura stołowa

*Wersja 1, 4.10.2026 (sesja w chmurze, zadanie `Plytki/Format-S1/zadania/ZADANIE-ODBIOR-S1.md`). Płytki z zamówienia S1: P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2; firmware `Rewizje/EGRLab-v6.2-s1`. Wszystkie wyniki: **NIE ZBADANO** — dokument powstał z plików, nie ze sprzętu. Wartości wpisuj do `FORMULARZ-ODBIORU.md` (identyfikatory kroków są te same). Narzędzia i kolejność lutowania: `NARZEDZIA-I-CZESCI.md`.*

Dokument jest samowystarczalny przy stole. Szczegóły i uzasadnienia liczb są w formularzach ODBIOR wydań (`Plytki/P0x-Rx-review/docs/ODBIOR.md`) — tutaj jest kolejność, połączenia i kryteria. Gdzie kryterium jest moim szacunkiem, a nie liczbą z obliczeń wydania, jest oznaczone **(szac.)**.

## 0. Zasady

1. **Kolejność:** montaż i oględziny → zwarcia bez zasilania → P02 sama → P03 sama → P02 + P03 → P05 → P06 → P09 → P10 (każda najpierw sama z zasilacza, potem dołączana do stosu) → komplet LOGGER. Nie przechodź dalej po wyniku „źle” — najpierw przyczyna.
2. **Pierwsze zasilenie każdej płytki z zasilacza z ograniczeniem prądu**, z limitem z tabeli kroku. Limit wolno podnieść dopiero, gdy przy niskim nie ma zwarcia ani grzania.
3. **Żadnego wpinania pod napięciem.** Połączenia zmieniasz przy wyłączonym PWR i odłączonym USB. P05 i P06 mają 220 µF za 1 Ω: wpięcie do żywego 5V_SYS to impuls do 5 A, który przeciąża TSR 2-2450 (2 A, foldback) i resetuje P03.
4. **Nigdy prosta taśma między dwoma J_BP.** Pinouty płytek są różne (np. P03 J_BP2.17/19/20 = 5V_SYS, a P05 J_BP2.17/19/20 = GND — prosta taśma zwiera 5V_SYS z masą). Bez P12 tylko połączenia z tabeli 1.3.
5. **Kołki listew serwisowych J_SV** idą przez rezystor przy węźle (1 kΩ szyny i logika, 4,7 kΩ P02 węzły mocy i P05 VBAT_SENSE, 10 kΩ węzły analogowe, wyjścia OD i CAN_H/L). Multimetr 10 MΩ mierzy przez nie z błędem ≤ 0,1 %, sonda ×10 (15 pF) widzi zbocza 15 ns (1 kΩ) / 150 ns (10 kΩ). Przez kołki nie mierzysz prądu i nie podajesz zasilania. Pin 1 i ostatni każdej listwy to GND; na płytkach poziomów 2–4 pin 1 jest przy **większym** x — sprawdź z nadrukiem.
6. **Zwarcie widziane przez kołek:** omomierz między kołkiem a GND pokazuje rezystor szeregowy + rezystancję węzła. Odczyt równy samemu rezystorowi szeregowemu (np. 1,00 kΩ na kołku 1 kΩ) = węzeł zwarty do masy.
7. Masa sondy DHO804: kołek GND tej samej listwy, krótka sprężynka. Sondy ×10, ograniczenie pasma 20 MHz włączone przy pomiarach zasilania.
8. Termometr palcem: żaden element nie może parzyć po 1 min pracy na stole (wyjątek: P06 R21 PR02 — ciepły, ok. 0,7 W).

## 1. Przygotowanie

### 1.1 Firmware 6.2-s1 — który wariant kiedy

Obrazy gotowe w `Rewizje/EGRLab-v6.2-s1/firmware/prebuilt/<wariant>/`. Wgrywanie z katalogu wariantu, kabel USB w gnieździe modułu M1 (od krawędzi B):

```text
python -m esptool --chip esp32s3 -p PORT -b 460800 --before default_reset --after hard_reset write_flash "@flash_args"
python -m serial.tools.miniterm PORT 115200
```

| Etap | Wariant | Co robi | Oczekiwane w konsoli |
|---|---|---|---|
| 4 (P03, P02 + P03) | `core` | init, MCP23017, PSRAM, montaż SD, plik próbny; bez akwizycji | `PSRAM=16777216; hardware accepted=0; …`, potem `CORE: init, MCP, PSRAM and SD mount complete; acquisition disabled…` i `PFAIL_N (GPIO3) = 1, tryb stolowy = 0` |
| 5 (P05 w stosie) | `minimal` | LOGGER napięciowy: AD7606B, zapis SD, PFAIL; bez TEMP/CAN/prądu | jak wyżej (bez linii CORE); po `logger` — stan LOGGER w `status` |
| 6–9 (P06, P09, P10, komplet) | `logger` | DAQ + I-LOGGER + TEMP + CAN, TEST wyłączony | jak wyżej; w `events_NNN.ndjson` zdarzenia `config` z `current_chain`, `can_config`, `daq_stats` co 10 s |
| — | `test`, `wifi` | wymagają P04/P07 (TEST, DRIVE) | **nie używać** w LOGGER S1 |

Uwagi do firmware (z kodu `app_main.c`):
- Tryb stołowy (F-02) włącza się, gdy PFAIL_N = L przez ≥ 100 ms od startu, czyli **tylko gdy P02 jest podłączony, ale bez zasilania**, a CORE idzie z USB. Komunikat: `TRYB STOLOWY: PFAIL_N = L (P02 bez zasilania) - bez zapisu sesji i bez TEST`.
- Gdy J_BP2 P03 nie jest podłączone, R43 trzyma PFAIL_N = H i firmware pracuje normalnie (komunikat `zasilanie z P02`, choć P02 nie ma) — **montuje kartę SD i bez karty się zatrzymuje**. Karta FAT32 w gnieździe przy każdym starcie poza trybem stołowym.
- Polecenia konsoli: `status`, `profile`, `logger`, `stop`, `mark`, `zero`, `save`, kalibracja (`cal`, `iscal`, `currentcal`, `icalok`, `bank`, `bypass`) — opis w `Rewizje/EGRLab-v6.2-s1/docs/05-profile.md`.
- Logi z karty: `python tools/egrlog.py inspect|export|report <katalog sesji>` (z katalogu wydania 6.2-s1).

### 1.2 DHO804 — ustawienia bazowe

Sondy ×10 (w menu kanału ×10), sprzężenie DC, pasmo 20 MHz, wyzwalanie Single, pretrigger ok. 25 %, pamięć ≥ 1 Mpts. Pomiar prądu przez rezystor 1 Ω na P05 (R1) i P06 (R6): dwa kanały po obu stronach rezystora, Math A − B, 1 V na wyjściu = 1 A; przy 1 V/dz rozdzielczość różnicy ok. 2 mV, czyli ok. 2 mA.

### 1.3 Połączenia stołowe bez P12

Dopóki nie ma P12, każda płytka dostaje **pigtail**: gniazdo IDC zaciśnięte na ok. 20 cm taśmy, drugi koniec rozcięty na żyły z końcówkami dupont i opisany numerem pinu. Zasilanie rozprowadzają złączki Wago (szyny 5V_SYS, 3V3_IO, GND), sygnały łączysz żyła–żyła. Każdy sygnał zboczowy (zegary SPI, CS, CONVST, BUSY) prowadź skręcony z sąsiednią żyłą GND swojej taśmy, a GND wszystkich pigtaili połącz w jednej złączce. Na przewodach stołowych pracuj przy SPI 1 MHz; kwalifikacja 4 MHz / 10 kS/s dopiero z P12 (ODBIOR P05 krok 17).

Tabela połączeń (z `Plytki/P12-przygotowanie/wyniki/KONTRAKTY.md`, sieci w stanie OK oraz ADC_SCLK/ADC_DOUTA, które w LOGGER mają wszystkich odbiorców):

| Grupa | Sieć | P02 R4 J_BP | P03 R6 | P05 R3 | P06 R2 J_BP | P09 R2 J1 | P10 R2 J1 |
|---|---|---|---|---|---|---|---|
| W0 zasilanie | 5V_SYS | 2, 4, 6 | J_BP2.17, .19, .20 | J_BP1.2, .4 | 10, 12 | 2, 16 | 2, 10 |
| W0 | 3V3_IO | 8, 10 | J_BP3.5 | — (nie wchodzi) | 14 | 4 | 4 |
| W0 | GND | 1, 3, 5, 7, 9, 11, 13, 19 | J_BP1/2/3: nieparzyste poza wyjątkami (wyjątki: J_BP1.11/13/15/17/19, J_BP2.17/19, J_BP3.5/9/13/17) | J_BP1: 1, 3, 5, 7, 8, 9; J_BP2: nieparzyste, 16, 20 | nieparzyste, 16 | nieparzyste | nieparzyste |
| W1 P02–P03 | PFAIL_N | 14 | J_BP2.16 | — | — | — | — |
| W1 | VBAT_SENSE | 20 | — | J_BP1.10 | — | — | — |
| W2 DAQ | ADC_SCLK | — | J_BP2.2 | J_BP2.2 | 2 | — | — |
| W2 | ADC_DOUTA | — | J_BP2.4 | J_BP2.4 | 4 | — | — |
| W2 | ADC_SDI | — | J_BP2.6 | J_BP2.6 | — | — | — |
| W2 | ADC_CS | — | J_BP2.8 | J_BP2.8 | — | — | — |
| W2 | ADC_CONVST | — | J_BP2.10 | J_BP2.10 | — | — | — |
| W2 | ADC_BUSY | — | J_BP2.12 | J_BP2.12 | — | — | — |
| W2 | MEAS_EN | — | J_BP2.14 | J_BP2.14 | — | — | — |
| W2 | ADC_RESET | — | J_BP2.18 | J_BP2.18 | — | — | — |
| W3 ILOG | CS_ILOG_N | — | J_BP1.2 | — | 6 | — | — |
| W3 | LOGGER_CURRENT_OK | — | J_BP1.11 | — | 8 | — | — |
| W4 TEMP | SPI3_SCLK | — | J_BP3.2 | — | — | 6 | — |
| W4 | SPI3_MOSI | — | J_BP3.4 | — | — | 8 | — |
| W4 | SPI3_MISO | — | J_BP3.6 | — | — | 10 | — |
| W4 | TC1_CS | — | J_BP3.8 | — | — | 12 | — |
| W4 | TC2_CS | — | J_BP3.10 | — | — | 14 | — |
| W5 CAN | CAN_TX | — | J_BP1.6 | — | — | — | 6 |
| W5 | CAN_RX | — | J_BP1.8 | — | — | — | 8 |

Niepodłączone w LOGGER (zostają wolne): P02 J_BP.12 PSU_OK, .15 P04_3V3, .16 SAFE_N, .17/.18 PG_SEND/PG_LINK; P03 wejścia z P11 (MARK, TEST_KEY, LOGGER_CLEAR, TEST_PRESENT), P08 (SENSOR_HEALTHY) i P04 (INTERLOCK, HW_ARMED) — stany ustalają rezystory domyślne (`P03-R6-review/docs/STANY-DOMYSLNE.csv`); P05 J_BP1.6 DAQ_OK (odbiorca tylko w P04). 5V_SYS do P03 prowadź trzema żyłami, do pozostałych dwiema; każda płytka ma co najmniej dwie żyły GND do złączki.

## 2. Oględziny i zwarcia przed pierwszym zasileniem

Po montażu każdej płytki, przed zasileniem. Umyj topnik (IPA) — resztki pod U1 P05 i przy węzłach 10 kΩ fałszują pomiary. Rezystancję mierz omomierzem, oba kierunki; odczyt rosnący (ładowanie kondensatorów) jest poprawny.

| ID | Płytka | Gdzie mierzyć | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| Z-01 | wszystkie | oględziny pod lupą: mostki, polaryzacja elektrolitów i diod, pin 1 układów (rysunek montażowy F.Fab z PDF PCB), klucz IDC | brak uwag | poprawić przed zasileniem |
| Z-02 | P02 | J_BP.2–J_BP.1 (5V_SYS), J_BP.8–.7 (3V3_IO), J_BP.20–.19 (VBAT_SENSE) — piny J_BP to węzły bez rezystorów | > 100 Ω, rośnie **(szac.)**; zwarcie < 10 Ω | TSR (orientacja), C22/C24, U8/U7 |
| Z-03 | P02 | kołki J_SV2: 4 VMOTOR, 5 BAT_IN, 8 SW_COM, 9 VSW, 10 VLOG, 12 HOLD_C (4,7 kΩ); J_SV1.9 AUX5 (1 kΩ) | odczyt wyraźnie większy niż rezystor szeregowy; ≈ 4,70 kΩ / 1,00 kΩ = zwarcie węzła | D3, D1/D2 (wspólna katoda), C12, C3, transil |
| Z-04 | P03 | J_BP2.17–.15 (5V_SYS), J_BP3.5–.3 (3V3_IO); J_SV1.10 3V3_CORE i J_SV2.12 5V_M1 względem GND (1 kΩ) | jak Z-02 / Z-03 | U5/Q1, C13/C14, moduł M1 jeszcze nie włożony |
| Z-05 | P03 | J_SV1.9 (3V3_IO) – J_SV1.10 (3V3_CORE) | **wyraźnie > 2,0 kΩ**; ≈ 2,00 kΩ = szyny zwarte ze sobą (zakazane) | mostek przy listwie / U14 |
| Z-06 | P05 | J_BP1.2–J_BP1.1 (5V_SYS); J_SV1.6 3V3_DAQ – J_SV1.7 (1 kΩ); U1: piny 36/39 (REGCAP) nie zwarte, 44/45 zwarte | jak Z-02 / Z-03 | U12, C1, mostki U1 |
| Z-07 | P05 | każdy kołek J_SV1/J_SV2 do swojego węzła (`P05-R3-review/docs/SERWIS.csv`) | wartość rezystora ± 1 % | rezystor od spodu, luty |
| Z-08 | P06 | J_BP.10–.9 (5V_SYS), J_SV2.3 5VA_P06 i J_SV2.4 3V3_P06 (1 kΩ) do GND; J3/J4 tor ECU/EGR do GND | jak Z-02 / Z-03; tor mocy bez połączenia z GND | RSH1, C3, przelotki wylewek |
| Z-09 | P09 | J1.2–J1.1 (5V_SYS), J1.4–J1.3 (3V3_IO); J2 kołki 2–12 do węzłów | > 100 Ω; 1 kΩ ± 1 % | U1–U3, C5 |
| Z-10 | P10 | J1.2–J1.1, J1.4–J1.3; J2 kołki 2–6 (1 kΩ), 7–8 (10 kΩ); J3 H–L: brak 120 Ω | > 100 Ω; rezystory ± 1 %; H–L wysoka rezystancja | U1 TCAN1051V, D1 |

## 3. P02 R4 sama

Konfiguracja: przewody J1 do zasilacza (czerwony J1.1 BAT_IN, czarny J1.2 GND), J14 (PWR) — dwa przewody do przełącznika albo zwory, J15 (VBAT) wolny, J2 (VMOTOR) wolny. **Bezpieczniki F1, F2, F3 wyjęte.** Na pierwszy etap pakietu nie podłączaj.

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P02-01 | 10,0 V, limit 50 mA, PWR rozwarty | prąd zasilacza | < 15 mA **(szac.)**; nic się nie grzeje | zwarcie w sterowaniu: U1 LM2936, U3 TL431, D11/D12 |
| P02-02 | jw. | J_SV2.5 BAT_IN, J_SV2.8 SW_COM | BAT_IN = zasilacz; SW_COM = zasilacz − 0…0,7 V | Q9 (orientacja, bramka) |
| P02-03 | jw. | J_SV1.9 AUX5; J_SV1.11 REF | AUX5 4,85–5,15 V; REF 2,483–2,507 V (multimetr 10 MΩ przez 10 kΩ zaniża o ok. 2,5 mV) | U1, R1 47 Ω; U3 orientacja (1 = K, 2 = A, 3 = REF) |
| P02-04 | jw. | J_SV1.8 OK, J_SV1.2 ENABLE, J_SV2.9 VSW, J_SV1.10 PFAIL_N; LED1 | OK i ENABLE ≤ 0,4 V; VSW ≈ 0 V; PFAIL_N ≈ 0 V (3V3_IO brak, F3 wyjęty); LED zgaszona | U2 w podstawce (orientacja), U4 |
| P02-05 | 12,0 V, PWR zwarty, limit **1,0 A**; zasilacz powoli w górę do 14,5 V (ok. 0,05 V/s), potem w dół do 11,5 V | J_SV2.9 VSW (multimetr) albo LED; napięcie zasilacza na J_SV2.5 | załączenie **12,90–14,08 V** (nom. 13,50), wyłączenie **11,98–13,11 V** (nom. 12,55), histereza ≥ 0,84 V, bez migania LED na progu (O-02) | poza obwiednią: R5/R9/R10/R11, U3; miganie: C13, R11 |
| P02-06 | Załączenie przy 14,5 V z limitem 1,0 A | prąd zasilacza | krótkie wejście zasilacza w ograniczenie (do ok. 50 ms) jest oczekiwane: C12 2200 µF ładuje się przez R40 22 Ω (szczyt 0,76 A, τ 48 ms); jeśli LED miga cyklicznie (start–stop), podnieś limit do 2 A | trwałe ograniczenie > 0,2 s: zwarcie za Q1 |
| P02-07 | 14,5 V, włączone | J_SV2.2 GATE, J_SV2.10 VLOG, J_SV2.12 HOLD_C, J_SV1.8 OK, J_SV1.2 ENABLE | GATE co najmniej 8 V poniżej SW_COM **(szac.)**; VLOG = VSW − ok. 0,5 V; HOLD_C = VSW − ok. 0,3 V po ok. 0,3 s; OK 4,70–5,0 V; ENABLE H | D1/D2 odwrotnie; R40 (rezystor bezpiecznikowy); Q3–Q5 |
| P02-08 | Pakiet 3S i odwrócone ogniwo: PWR rozwarty, ustaw 12,6 V, zewrzyj PWR; potem 7,2 V | LED, VSW | brak startu w obu przypadkach (O-03) | próg UVLO |
| P02-09 | Szybkość narastania VSW: PWR zwierany przy 14,5 V | DHO804: CH1 J_SV2.9 VSW, 5 V/dz, 1 ms/dz, wyzwalanie narastające 7 V | narastanie VSW 5–15 V/ms (nom. 11,5 V/ms; O-04, Z-07) | C5/R21 |
| P02-10 | PWR rozwarty, włóż **F2** (TSR 5 V), PWR zwarty | J_BP.2–.1 (5V_SYS) | 4,90–5,10 V (TSR ± 2 %) | U5 orientacja, F2 |
| P02-11 | PWR rozwarty, włóż **F3** (TSR 3,3 V), PWR zwarty | J_BP.8–.7 (3V3_IO); J_SV1.3 SUP5_N; J_SV1.4 PSU_OK; J_SV1.10 PFAIL_N | 3V3_IO 3,23–3,37 V; SUP5_N, PSU_OK, PFAIL_N ≥ 3,0 V | U6, U7/U8 (MCP120), U9 od spodu, U10 w podstawce |
| P02-12 | jw. | prąd zasilacza przy 14,5 V bez obciążenia | zapisać (oczekiwane kilkadziesiąt mA **(szac.)**) | — |
| P02-13 | Makieta komplet LOGGER: PWR rozwarty, na pigtailu J_BP między 5V_SYS (2, 4, 6 razem) a GND kondensator 470 µF / 16 V i 4,7 Ω / 10 W; PWR zwarty przy 14,5 V | DHO804 jak w 9.1 (CH1 5V_SYS na J_SV2.11, CH2 PSU_OK J_SV1.4) | jak kryterium 9.1: narastanie monotoniczne, bez restartów (foldback), 5V_SYS po starcie 4,90–5,10 V pod 1 A | TSR w foldbacku: za duża pojemność albo obciążenie — nie łącz płytek, zgłoś |
| P02-14 | Podtrzymanie (O-05, wyłącznik): obciążenie 4,7 Ω (≈ 6 W z VLOG); zasilacz 14,5 V; rozewrzyj PWR | DHO804: CH1 J_SV1.10 PFAIL_N (wyzwalanie opadające 1,6 V, 5 ms/dz), CH2 5V_SYS (J_SV2.11), CH3 J_SV2.10 VLOG, CH4 J_SV1.2 ENABLE | od zbocza PFAIL_N do 5V_SYS < 4,75 V **≥ 10 ms** (Z-08 w najgorszym narożniku; nominalnie ok. 17 ms do VLOG = 7 V); PFAIL_N opada ≤ 100 µs po ENABLE (Z-09; oczekiwane ok. 5 µs) | C12, D1b, R40/D2; PFAIL_N późno: U2A |
| P02-15 | jw. z 10 Ω (≈ 3 W) | jw. | ≥ 20 ms **(szac. z 22,3 ms w najgorszym narożniku)**; nominalnie ok. 33 ms | jw. |
| P02-16 | VBAT (O-08): drugi kanał zasilacza albo ten sam przez przewód: 12,00 V i 15,00 V na J15 (wspólna masa z J1.2) | J_BP.20 VBAT_SENSE (bez P05), J_SV2.3 | VBAT_SENSE = J15 z dokładnością ≤ 20 mV **(szac.: upływ P6KE24CA µA na 10 kΩ)**; nie przekraczać 20 V | D13 odwrotnie (jest dwukierunkowy — wtedy uszkodzony), R38 |
| P02-17 | Odwrotna polaryzacja (O-01), opcjonalnie, przed łączeniem z innymi płytkami: F1–F3 wyjęte, −14 V na J1 (zamienione przewody), limit 100 mA, PWR zwarty, 10 s | prąd, temperatura Q9 | prąd ≤ 1 mA **(szac.: upływy)**, nic się nie grzeje; potem powtórzyć P02-02…P02-04 | Q9 (Q_REV) — nie przechodzić dalej |

### 3.1 Pakiet 4S

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P02-18 | Pakiet bez P02: napięcie i polaryzacja na XT60, BMS, bezpiecznik 7,5 A przy koszyku | multimetr na XT60 | 13,0–16,8 V (≥ 3,25 V/ogniwo, inaczej P02 może nie wystartować — próg do 14,08 V), plus na przewodzie do J1.1 | ładowanie ogniw, BMS |
| P02-19 | PWR rozwarty, XT60 do P02 (F2/F3 włożone, F1 wyjęty, makieta 470 µF + 4,7 Ω), PWR zwarty | LED, J_BP.2 5V_SYS, J_BP.8 3V3_IO, PSU_OK | start, wartości jak P02-10/P02-11; iskra przy wtyku bez znaczenia (wejście bez pojemności przed Q9) **(szac.)** | — |
| P02-20 | Podtrzymanie (O-05, wyjęcie pakietu): obciążenie 4,7 Ω, wyjęcie XT60 | jak P02-14 | ≥ 10 ms jak P02-14 | jak P02-14 |

F1 (VMOTOR, 5 A) zostaje wyjęty przez cały odbiór LOGGER; O-06 (zwarcie VMOTOR) i O-09 (4 A przez 30 min) należą do wariantu pełnego z P07. Pakietu nie zostawiaj w nagrzanym aucie (ok. 60 °C limit ogniw).

## 4. P03 R6

### 4.1 Bez modułu M1, z zasilacza

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P03-01 | Moduł M1 wyjęty. 5,00 V z zasilacza na J_BP2.17/.19/.20, GND na J_BP2.15, limit 50 mA | prąd | < 10 mA **(szac.: LTC4412 i podciągnięcia)** | Z-04, C13/C14, U5/Q1 |
| P03-02 | jw. | J_SV2.2 5V_SYS, J_SV2.12 5V_M1, J_SV1.10 3V3_CORE | 5V_SYS = 5,00 V; 5V_M1 = 4,95–5,00 V (Q1 włączony przez LTC4412) **(szac.)**; 3V3_CORE ≈ 0 V (LDO jest na module) | Q1 źródło/dren zamienione; U5 |

### 4.2 Moduł M1, tylko USB, firmware `core`

Wyłącz zasilacz i odłącz go. Na module zdejmij diodę RGB z GPIO38 (jeśli nie zdjęta). Włóż M1 (rzędy 22,86 mm, orientacja według nadruku), kartę microSD FAT32, kabel USB. Wgraj `core` (1.1).

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P03-03 | USB, J_BP niepodłączone | konsola | linie z tabeli 1.1 (`PSRAM=16777216`, `CORE: … SD mount complete`, `PFAIL_N (GPIO3) = 1, tryb stolowy = 0`); na karcie plik `core_probe.tmp` | brak SD → wariant staje na montowaniu karty; MCP23017: luty U1/U2 (DIP w podstawkach), I2C (J_SV1.8/.11 ≈ 3,3 V) |
| P03-04 | jw. | J_SV1.10 3V3_CORE; J_SV2.12 5V_M1; J_SV2.2 5V_SYS | 3V3_CORE 3,20–3,40 V; 5V_M1 = USB − D1 modułu (zapisać, ok. 4,6–4,9 V **(szac.)**); 5V_SYS < 0,1 V | 5V_SYS rośnie: Q1/U5 — USB zasila szynę (zakazane) |
| P03-05 | jw., amperomierz µA między J_BP2.20 a J_BP2.15 | prąd wsteczny USB → 5V_SYS | < 50 µA ustalonego prądu (impulsy zanotować osobno) | U5 (LTC4412) |
| P03-06 | jw. | J_SV2.3 PFAIL_N | ≥ 3,0 V (R43 100 kΩ, J_BP2 otwarte) | R43 |
| P03-07 | Przycisk RESET modułu przytrzymany (i osobno: tryb bootloadera — BOOT + RESET) | J_SV2: 4 ADC_RESET, 5 MEAS_EN, 7 ADC_CONVST = 0; 8 ADC_CS, 9 CURRENT_CS_N, 10 SD_CS = 1; J_SV1: 2/3 MOTOR_INB/INA = 0, 4 MEAS_BANK = 0, 5 CS_ILOG_N, 7 CS_ITEST_N = 1; J_SV3: 2 MCU_ARM = 0, 8 TC2_CS, 9 TC1_CS = 1 | „0” ≤ 0,4 V, „1” ≥ 2,9 V | rezystory domyślne, bufory U11–U14 / U21–U23 (Ioff) |
| P03-08 | RESET przytrzymany (przycisk modułu = EN = SUP_N) | J_SV3.12 SUP_N, J_SV2.11 SUP_RAW_N | SUP_N = L (≤ 0,6 V), SUP_RAW_N zostaje H (TPS3808 widzi poprawne 3V3_CORE); po puszczeniu SUP_N = H i ponowny start w konsoli (MCP odtworzony) | SUP_N > 0,6 V: R34/R35, U4 LVC1G37 (nie zamieniony z U6) |

### 4.3 P02 + P03

Wyłącz wszystko. Połącz W0 (5V_SYS trzy żyły, 3V3_IO, GND) i W1 (PFAIL_N, bez VBAT_SENSE). F1 wyjęty. Zasilanie P02 z zasilacza 14,5 V, limit 1,0 A (albo z pakietu).

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P03-09 | PWR zwarty, USB odłączony | P03 J_SV2.2 5V_SYS, J_SV2.12 5V_M1, J_SV1.10 3V3_CORE, J_SV1.9 3V3_IO | 5V_SYS ≥ 4,85 V; 3V3_CORE 3,20–3,40 V; 3V3_IO 3,23–3,37 V | spadek na przewodach: dołożyć żyły 5V_SYS/GND |
| P03-10 | Obciążenie ok. 0,5 A: 10 Ω / 5 W na złączce 5V_SYS przy P03 (razem z CORE ok. 0,6–0,8 A) | P03 J_SV2.2 5V_SYS względem P03 GND; ten sam pomiar na P02 J_SV2.11 | na P03 ≥ 4,85 V; zapisać spadek P02 → P03 (z P12 będzie mniejszy) | przewody, styki dupont |
| P03-11 | Tryb stołowy (F-02): PWR rozwarty (P02 bez zasilania), USB do P03 | konsola; J_SV2.3 PFAIL_N | komunikat `TRYB STOLOWY…`; PFAIL_N < 0,825 V (szac. 0,33 V); na karcie brak nowego katalogu sesji | PFAIL_N ≥ 0,825 V: R43 (musi być 100 kΩ), podciągnięcie na P02 |
| P03-12 | PWR: włącz i wyłącz kilka razy (USB podłączony, żeby CORE został przy życiu) | DHO804: CH1 P02 J_SV1.2 ENABLE, CH2 P03 J_SV2.3 PFAIL_N (wyzwalanie opadające) | opadanie PFAIL_N na P03 ≤ 100 µs od ENABLE; **L < 0,825 V** (szac. 0,43 V przy VOL 0,4 V); po włączeniu H ≥ 2,5 V. Zapisać L i temperaturę otoczenia | L za wysokie: VOL LM2903 (P02 U2), R42/R43 |

Przy podłączonych naraz USB i P02 CORE nie ma gwarantowanego priorytetu źródła (`ZASILANIE-RESET.md`) — pomiary napięć P03-09/P03-10 rób bez USB.

## 5. P05 R3

### 5.1 Sama, z zasilacza

Według `P05-R3-review/docs/ODBIOR.md`, kroki 0–7 i 10a–11. Zasilanie 5,00 V na J_BP1.2/.4 (GND J_BP1.1/.3), J_BP2 wolne (stany: CS = 1, reszta = 0 z rezystorów domyślnych). Najważniejsze punkty:

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P05-01 | 5,00 V, limit 100 mA, potem 250 mA; MEAS_EN = 0 | prąd; J_SV1.4 5V_SYS, J_SV1.5 5VA_P05, J_SV1.6 3V3_DAQ | 5VA = 5V_SYS − 12…20 mV (różnicowo J_SV1.4–.5); 3V3_DAQ 3,20–3,40 V | U12, R1 |
| P05-02 | Przed skręceniem stosu | REF_2V5 na C24 (multimetr) albo J_SV1.8 miernikiem ≥ 1 GΩ | 2,4988–2,5013 V | U2 REF5025 (klasa wysoka „ID”) |
| P05-03 | Okno DAQ_OK: zasilacz powoli 4,60 → 5,30 → 4,60 V (**nie więcej niż 5,3 V**) | J_SV2.10 DAQ_RAIL_N, J_SV2.9 DAQ_OK; zasilacz na J_SV1.4 | dolny próg **4,756–4,845 V** (nom. 4,800), górny **5,141–5,230 V** (nom. 5,186); DAQ_OK = 1 tylko w oknie | R3–R8 (1206 0,1 %, 10 ppm/K), U3 |
| P05-04 | 5,00 V; nadzorcy | J_SV2.11 P05_SUP3_N, J_SV2.12 P05_SUP5_N, J_SV2.9 DAQ_OK | wszystkie H przy 5,00 V; DAQ_OK = 0 przy braku któregokolwiek warunku (krok 6) | U6/U7 |
| P05-05 | Przekaźniki przed wlutowaniem (10a) | cewka z zasilacza, ok. 23 °C | zadziałanie ≤ 3,9 V każdej sztuki | sztukę wymienić |
| P05-06 | Pomiar 5V_SYS przy ok. 23 °C (krok 3) | J_SV1.4 | 4,93–5,07 V — to kryterium dla szyny z P02 w 9.2 | — |
| P05-07 | Kondensatory U1 przed skręceniem (krok 11) | TP2–TP5 (TP1 = GND) | Ceff C12/C13 ≥ 10 µF przy 2,5/4,4 V (karta DC-bias lub pomiar) | — |

### 5.2 W stosie (P02 + P03 + P05), firmware `minimal`

Wyłącz wszystko, dołącz W0 (5V_SYS dwie żyły, GND), W1 (VBAT_SENSE) i W2 do P05. Wgraj `minimal`. Karta SD w gnieździe. J4 TAPS i J6 AUX wolne.

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P05-08 | Start (PWR), konsola przez USB | konsola, `status` | start bez restartów; po `logger` stan LOGGER, `adc=1`, licznik `lost` = 0 | brak AD7606B: W2, U9/U10/U11 (Ioff) |
| P05-09 | Rozruch AD7606B (F-04): wyłącz/włącz PWR | DHO804: CH1 P05 J_SV2.6 ADC_RESET, CH2 J_SV2.7 MEAS_EN, CH3 J_SV2.2 ADC_CS, CH4 J_SV2.3 ADC_CONVST; 500 ms/dz, wyzwalanie narastające CH1 | RESET jeden impuls ok. 20 µs, nie wcześniej niż 10 ms po zasileniu; aktywność CS (konfiguracja) **≥ 2,1 s** po RESET; MEAS_EN dopiero po konfiguracji; CONVST startuje ok. 25 ms po MEAS_EN. Jeśli MEAS_EN rośnie dopiero po poleceniu `logger`, zmierz odcinek RESET → konfiguracja po starcie, a konfiguracja → MEAS_EN → CONVST po `logger` | firmware nie 6.2-s1; MEAS_EN przed konfiguracją = błąd F-04 |
| P05-10 | Takt próbkowania | CH4 ADC_CONVST, CH3 J_SV2.4 ADC_BUSY, 200 µs/dz | CONVST co 500 µs (2 kS/s); po każdym CONVST jeden impuls BUSY; zapisać szerokość BUSY | BUSY brak: U1 zasilanie/REGCAP |
| P05-11 | Wejście testowe CH7: 12,00 V z zasilacza na P02 J15 (VBAT_IN, wspólna masa) | zapis 30 s (`logger`, potem `stop`), `egrlog.py export` → kolumna kanału CH7 (indeks 6) | przed kalibracją kod ok. **6351** (±1 %) przy zakresie ±10 V (12,00 V / 6,1918 / 10 V × 32768; przez R38 10 kΩ na P02) | kod ok. 6457: VBAT podany wprost na P05 J_BP1.10 (mnożnik 6,0898); inny: zamiana kanałów, R31/R32 |
| P05-12 | jw. 15,00 V | jw. | kod ok. 7938 (±1 %); stosunek kodów 15/12 z dokładnością 0,2 % **(szac.)** | nieliniowość — U1, zakres |
| P05-13 | Kanały CH1–CH5 przez docelowe adaptery (krok 12 ODBIOR) | jw. | znaki i kanały zgodne; kalibracja dwupunktowa `cal 0 kanał gain offset`, sprawdzenie w trzecim punkcie | — |
| P05-14 | **Drgania DAQ_OK** (MINOR-4 recenzji): `logger` przy 2 kS/s, zapis SD, 30 min | DHO804: CH1 P05 J_SV2.9 DAQ_OK — wyzwalanie **opadające 1,6 V, tryb Normal**; CH2 J_SV1.5 5VA_P05 sprzężenie AC 20 mV/dz; CH3 J_SV2.10 DAQ_RAIL_N; CH4 J_SV2.8 MEAS_PERMIT | **zero wyzwoleń w 30 min**, przekaźniki nie klikają; tętnienia i szpilki 5VA (p-p, zapisać) mniejsze niż połowa zapasu (5VA DC − dolny próg zmierzony w P05-03) | szpilki od SD/CONVST: C35/C1, droga masy C15/C24 (przyjęte 21–23 mm); zapisać oscylogram |
| P05-15 | jw., pakiet częściowo rozładowany albo zasilacz 13,0 V | jw., 10 min | jak P05-14 | — |
| P05-16 | `daq_stats` w `events_NNN.ndjson` po 30 min | `convst`, `samples`, `adc_errors`, `lost_ticks` | `convst` = `samples`, `adc_errors` = 0, `lost_ticks` = 0 (F-05) | SD za wolna, przewody SPI (dopiero P12) |
| P05-17 | Zanik P05 w sesji: rozłącz żyły 5V_SYS P05 (bez ponownego wpinania pod napięciem) | konsola, log | FAULT / błąd ADC, MEAS_EN = 0; bez starych próbek jako nowych. Ponowny start całości → pełny RESET + 2,1 s | — |

## 6. P06 R2

### 6.1 Sama, z zasilacza

Według `P06-R2-review/docs/ODBIOR.md`, M01, E01–E09. Zasilanie 5,00 V na J_BP.10/.12 (GND .9/.11); 3V3_IO na J_BP.14 tylko dla E08. Bez P03 CS_ILOG_N = H (R8 100k), ADC_SCLK = L (R10 100k). Przełącznik BYPASS (DPDT ON-ON ≥ 10 A, na panelu) przylutowany do J4/J5 według `P06-R2-review/docs/WIAZKI.md`; numery oczek sprawdź omomierzem (E03).

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P06-01 | E01–E03 bez zasilania | J3/J4, RSH1, SW1 | tor przez bocznik zawsze zamknięty; BYPASS zwiera równolegle; brak połączenia z GND | luty RSH1, oczka SW1 |
| P06-02 | E04: 5,00 V, limit **30 mA**, BYPASS | J_SV2.2 5V_SYS, .3 5VA_P06, .4 3V3_P06, J_SV1.5 REF_BUF; REF25 na C5/U10.2 albo miernikiem ≥ 1 GΩ | VREF 2,475–2,525 V | U10 MCP1525, C5 |
| P06-03 | E05: MEASURE, limit 250 mA, 4,75 / 5,00 / 5,25 V | prąd; temperatura R21, R6 | < 180 mA; R21 ciepły (0,64–0,71 W) | — |
| P06-04 | E06–E07 | J_SV2.10 LOGGER_CURRENT_OK, J_SV2.9 SHUNT_ENABLED, J_SV2.7/.8 SUP3_N/SUP5_N | MEASURE: READY = H; BYPASS: SHUNT_ENABLED = L i READY = L; wymuszone SUP3_N / SUP5_RAW → READY = L | U6, R21/J5 |
| P06-05 | E09: start 5 V | CH1 J_SV2.2, CH2 J_SV2.3 (Math CH1 − CH2 = prąd R6 1 Ω), CH3 J_SV2.4, CH4 J_SV1.6 REF25 | **przy wpięciu do żywego 5 V** prąd przez R6 ≤ ok. 5 A, τ ≈ 0,22 ms; przy narastaniu zasilacza znacznie mniej | — |

### 6.2 W stosie, firmware `logger`

Wyłącz wszystko, dołącz W0 i W3 oraz ADC_SCLK / ADC_DOUTA (W2) do P06. Wgraj `logger`. P09 i P10 mogą jeszcze nie być podłączone — firmware zapisze wtedy błędy temperatur (NAN, fault) i brak ramek CAN; to oczekiwane. **Jeśli wariant `logger` nie przejdzie do stanu LOGGER bez P09/P10, zapisz to i odbierz P06 dopiero w komplecie (rozdz. 9)** — tego nie da się sprawdzić bez sprzętu.

Źródło prądu do kalibracji: zasilacz w trybie CC przez J3 → bocznik → J4, wzorzec w szeregu (`NARZEDZIA-I-CZESCI.md`). P02 zasila wtedy pakiet. Minus źródła połącz z GND stosu (napięcie wspólne ok. 0 V; E17 dla 12–15 V osobno).

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P06-06 | E10: prąd 0, MEASURE, `logger` | DHO804: J_SV2.11 CS_LOCAL_N, J_SV2.12 CLK_LOCAL; log `current_raw` | 16 taktów na CS, kod ok. 2048, stały; wspólna linia ADC_DOUTA bez konfliktu z P05 (brak zniekształconych bitów na CH obu ADC) | U5 (trójstanowy), W2 |
| P06-07 | E11: zero po 1 s | J_SV1.2 I_L_OUT, J_SV1.5 REF_BUF, J_SV1.3 ADC_AIN (multimetr) | I_L_OUT ≈ REF_BUF (ok. 2,5 V), ADC_AIN ≈ 1,25 V; szum kodu zapisać (cel po kalibracji: offset < 20 mA, RMS < 10 mA) | — |
| P06-08 | Kalibracja ADC lokalnego: w SAFE `bank 0`; dwa punkty prądu (np. 0 i +3 A), w każdym napięcie I_L_OUT multimetrem i `current_raw` z logu | — | `adc_gain = (V2 − V1)/(raw2 − raw1)` ≈ 0,00122 V/kod; `adc_offset = V1 − raw1·adc_gain` ≈ 0 | — |
| P06-09 | Skala V/A: ±0,5 / 1 / 3 A (potem ±6 A), odwracanie przewodów źródła przy wyłączonym źródle | I_L_OUT względem REF_BUF; wzorzec prądu | ok. 0,25 V/A (5 mΩ × 50) w obu kierunkach | znak odwrotny: Kelvin K_PLUS/K_MINUS |
| P06-10 | Wpisy: `iscal 0 adc_gain adc_offset V/A`, `currentcal 0 zero` (zmierzone I_L_OUT przy 0 A), `icalok 0 1`, `bypass 0`, `zero`, `save` | `profile` | wartości jak wpisane | — |
| P06-11 | E13: kontrola w punktach ±0,5 / 1 / 3 / 6 A przy 5V_SYS z P02; potem przy 4,75 i 5,25 V: żyły 5V_SYS P06 odłączone od szyny i podane z zasilacza (GND wspólne), zasilacz włączany po P02, wyłączany przed P02 | prąd z logu vs wzorzec | reszta ≤ max(30 mA, 1 % wskazania) | — |
| P06-12 | E14: BYPASS przy ustalonym prądzie 1 A | J_SV2.9, J_SV2.10; log | SHUNT_ENABLED = L, READY = L; w logu brak ważnych amperów (kolumna A pusta) | — |
| P06-13 | E15: bierny tor 10 A, 30 s, potem 10 min (35 µm miedzi!) | temperatura pól J3/J4/RSH1 (termopara P09 albo termowizja); spadek na torze | przyrost < 30 °C, stały spadek, brak odbarwień | przerwać przy zapachu/odbarwieniu |

## 7. P09 R2

### 7.1 Moduły i nośnik, z zasilacza

Moduły MAX31856 są lutowane wprost — **przed lutowaniem** kroki 1–4 `P09-R2-review/docs/MODUL-KWALIFIKACJA.md` (każdy moduł osobno: VIN 3,3 V, limit 50 mA, 3Vo 3,0–3,6 V). Nośnik bez modułów: 3,30 V na J1.4 i 5,00 V na J1.2/.16 (GND nieparzyste), limit 50 mA na szynę.

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P09-01 | Nośnik bez modułów | J2.2 3V3_IO, J2.3 5V_SYS, J2.8/.9 CS1_BUF/CS2_BUF, J2.10/.11 OE1_N/OE2_N | szyny bez zwarć, pobór kilka mA **(szac.)**; oba CS = H (≥ 2,9 V); OE1_N, OE2_N = H | U1–U3 |
| P09-02 | Kwalifikacja modułów 1–4, wybór VIN (JP1/JP2, jedna zwora na selektor, naklejka) | J2.4/.5 TC1/TC2_VIN, J2.6/.7 TC1/TC2_3VO | 3Vo 3,0–3,6 V przy wybranym VIN | wariant 5 V tylko po kroku 3 MODUL-KWALIFIKACJA |
| P09-03 | Po przylutowaniu modułów (pin 1 = VIN, nadruk „1”) | jw.; wyprowadzenia od spodu ≤ 1,5 mm | jak P09-02, brak zwarć kołków 4–7 do GND | — |

### 7.2 W stosie, firmware `logger`

Wyłącz wszystko, dołącz W0 (5V_SYS dwie żyły, 3V3_IO, GND) i W4. Termopary typu K w terminalach (polaryzacja według oznaczenia przewodu).

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P09-04 | Start (F-07) | log / konsola | konfiguracja CR0 = 91h, CR1 = 03h potwierdzona odczytem; pierwsza ważna próbka po 300 ms; brak błędu konfiguracji | W4, U1/U2, wybór VIN |
| P09-05 | MISO i CS | DHO804: J2.12 SPI3_MISO, J2.8/.9 CS1/CS2_BUF, J2.10/.11 OE1_N/OE2_N | przy nieaktywnych CS MISO w stanie Z; CS setup/hold 2 takty przy 1 MHz; przerwa obu CS = H ≥ 1 µs; podczas zapisu SD bez konfliktu (SD na tej samej SPI3) | U2 (Hi-Z), U3 dekoder |
| P09-06 | Temperatura otoczenia: obie termopary obok termometru odniesienia, 10 min stabilizacji, bez przeciągu | T1/T2 w logu (`status` pokazuje T1) | \|T − Tref\| ≤ 2 °C **(szac.: karta MAX31856 ok. ±0,7 °C zimne złącze + termopara klasy 1/2)**; T1 − T2 ≤ 1 °C | odwrotna polaryzacja termopary (spadek przy ogrzaniu) |
| P09-07 | Woda z lodem: kruszony lód + woda, mieszać, końcówka w środku naczynia, 3 min | T1, T2 | 0,0 ± 2,5 °C **(szac.: termopara klasy 2 ±2,5 °C)**; zapisać przesunięcie każdego kanału — to korekta do profilu | — |
| P09-08 | Ogrzanie końcówki (dłoń / ciepła woda) i powrót | T1/T2 | wzrost i powrót bez skoków | — |
| P09-09 | Termopara odłączona od terminala | log | fault, wartość NAN, poprawny status — nigdy 0 °C | — |
| P09-10 | Odłączona P09 (wyłącz, zdejmij W4, włącz) | log | błąd komunikacji, brak fikcyjnego 0 °C (moduł jest przylutowany, więc to zastępuje „moduł odłączony”) | — |

## 8. P10 R2

### 8.1 Sama, z zasilacza

5,00 V na J1.2/.10 i 3,30 V na J1.4, limit **20 mA na szynę** (bez drugiego kanału: 3V3_IO z P02 przez 47 Ω na pierwsze 10 s — spadek ok. 0,5 V przy 10 mA, tylko kontrola braku zwarcia).

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P10-01 | Pierwsze zasilanie | J2.2 5V_SYS, J2.3 3V3_IO; prądy | brak grzania; spoczynek w rezerwie 10 mA na szynę **(z formularza P10)** | U1 orientacja |
| P10-02 | Tryb stale silent | U1.8 (S) i U1.1 (TXD) = VIO; kołek J2.6 CAN_TX bez połączenia z U1 (omomierz) | jak obok | — |
| P10-03 | J3 wolne | J2.7 CAN_H, J2.8 CAN_L (multimetr) | poziomy recesywne ok. 2,5 V **(szac.)**; P10 nie wymusza stanu dominującego | D1, U1 |

### 8.2 W stosie, firmware `logger`, magistrala stołowa

Magistrala: dwa aktywne węzły CAN z ACK (np. dwa adaptery USB-CAN) na końcach skrętki, przy każdym 120 Ω; **500 kbit/s** (stałe w firmware). P10 jako odczep przez W3 (≤ 300 mm) do środka magistrali. **Masa:** połącz GND węzłów stołowych z GND stosu jednym przewodem przed podłączeniem W3 (stos z pakietu pływa względem komputera). Dołącz W0 i W5.

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| P10-04 | Znana sekwencja: ramki 11- i 29-bitowe, DLC 0–8, licznik w danych | log `can`, `can_stats`; DHO804 J2.4 RX_RAW → J2.5 CAN_RX | każda ramka w logu raz, `rx_missed` = 0; RX_RAW i CAN_RX zgodne | U2, R1, W5 |
| P10-05 | Brak TX: firmware/zewnętrznie CAN_TX (J_BP1.6 P03) L/H/PWM | CAN_H/L na J3 (sonda na złączu, nie na kołkach 10 kΩ) | P10 nigdy nie dominuje magistrali | — |
| P10-06 | Brak ACK: odłącz drugi węzeł | magistrala | brak ACK (P10 nie potwierdza), generator powtarza ramkę; po ponownym dołączeniu poprawne ramki | P10 potwierdza = S nie na VIO |
| P10-07 | Ruch ciągły 10 min z licznikiem | log vs licznik generatora | liczba ramek identyczna w zakwalifikowanym obciążeniu; `can_stats` bez strat; zapisać obciążenie magistrali | `log_dropped` > 0: obciążenie powyżej limitu — zapisać limit |
| P10-08 | RPM (F-08): z węzła `7E8#04410C1F40AAAAAA` co 100 ms | log | `rpm_obd` 2000 rpm, `ecu` 0x7E8 | — |
| P10-09 | Zatrzymaj nadawanie RPM | log | po 1 s `rpm_stale` (raz na przerwę); brak wartości 0 rpm | — |
| P10-10 | Zła długość: `7E8#07410C1F40` (DLC 5) | log | `rpm_rejected`, licznik `rpm_bad_length` rośnie | — |
| P10-11 | Wpływ kołków: powtórz P10-07 z sondą na J2.7/J2.8 | liczba błędów | bez dodatkowych błędów | — |

## 9. Komplet LOGGER (P02 + P03 + P05 + P06 + P09 + P10)

Wyłącz wszystko, połącz W0–W5. Firmware `logger`, karta SD, termopary, BYPASS w MEASURE, J4/J6 P05 wolne, F1 wyjęty.

### 9.1 Start 5V_SYS z całą pojemnością

Pojemność na 5 V z list części paczek: P02 22,1 µF, P03 11 µF, P05 232,7 µF (C1 220 µF, C35 10 µF, reszta ceramiczne), P06 220,5 µF, P09 4,7 µF, P10 4,8 µF — **razem ok. 496 µF**, limit TSR 2-2450 600 µF (karta TRACO: „Capacitive Load … 5 Vout: 600 µF max”, start 5 ms typ., przeciążenie: foldback). Elektrolity ±20 % mogą dać do ok. 580 µF, więc zapas w najgorszym razie jest mały i trzeba go zmierzyć. Budżet prądu 5V_SYS z dokumentów płytek: razem 1090 mA wobec 2 A.

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| LOG-01 | DHO804: CH1 P02 J_SV2.11 5V_SYS (1 V/dz), CH2 P02 J_SV1.4 PSU_OK (2 V/dz), CH3 P05 J_SV1.4, CH4 P05 J_SV1.5 (1 V/dz; Math CH3 − CH4 = prąd C1 przez R1 1 Ω); 2 ms/dz, Single, wyzwalanie CH1 narastające 2,5 V. Zasilacz 14,5 V / limit 2 A albo pakiet; PWR zwierany | przebiegi | 5V_SYS rośnie **monotonicznie** do ≥ 4,75 V, czas 10–90 % zapisać (oczekiwane rzędu 5 ms z karty TSR; **kryterium robocze ≤ 15 ms**); **brak restartów** (foldback = powtarzane narastania lub piła); po starcie brak spadku poniżej 4,75 V; PSU_OK = H po ustaleniu szyn | foldback: za duża pojemność albo obciążenie przy starcie — rozdzielić start (najpierw bez P06), zgłosić |
| LOG-02 | jw. | Math CH3 − CH4 | szczyt prądu ładowania C1 ≤ 0,5 A **(szac.: 220 µF × 5 V / 5 ms ≈ 0,22 A)** | prąd ok. 5 A = szyna rośnie skokiem, nie rampą — TSR / pomiar |
| LOG-03 | jw., zamiast P05 sondy na P06 J_SV2.2 / J_SV2.3 (prąd C3 przez R6) | Math | szczyt ≤ 0,5 A **(szac.)** | — |
| LOG-04 | Powtórz LOG-01 pięć razy; potem przy 13,6 V (blisko progu UVLO) i 16,8 V | jw. | każdy start jak LOG-01; przy 13,6 V brak cyklicznego załączania (UVLO + prąd startu) | miganie przy 13,6 V: spadek na przewodach pakietu/zasilacza w czasie startu |
| LOG-05 | P03 po starcie | konsola | jeden start, bez resetów brownout | zapad 5V_M1 / 3V3_CORE przy starcie |

### 9.2 Praca ciągła

| ID | Podłącz / zrób | Punkt pomiaru | Oczekiwane | Jeśli źle |
|---|---|---|---|---|
| LOG-06 | `logger`, sesja 30 min, zapis SD, ruch CAN z magistrali stołowej, termopary podłączone | prąd zasilacza przy 14,5 V | < 0,43 A (6 W z VLOG, Z-05) | pomiar poboru płytek osobno (budżety w `KONTRAKTY.md`) |
| LOG-07 | jw. | 5V_SYS: P02 J_SV2.11, P03 J_SV2.2, P05 J_SV1.4, P06 J_SV2.2, P09 J2.3, P10 J2.2 | P03 ≥ 4,85 V; P05 4,93–5,07 V przy ok. 23 °C (warunek okna DAQ_OK); pozostałe ≥ 4,85 V | przewody stołowe — z P12 spadek ma być mniejszy |
| LOG-08 | jw. | 3V3_CORE P03 J_SV1.10, 5V_M1 J_SV2.12 | 5V_M1 ≥ 4,60 V, 3V3_CORE stabilne (oscylogram podczas zapisu SD) | — |
| LOG-09 | jw. | log po 30 min | `daq_stats`: `convst` = `samples`, `adc_errors` = 0, `lost_ticks` = 0; `can_stats` bez strat w zakwalifikowanym ruchu; temperatury ważne; brak FAULT; P06 READY = 1 | — |
| LOG-10 | jw. | temperatura: P02 Q1/Q9, U5/U6 (TSR), D1; P03 M1 (LDO), Q1; P05 U1, R1; P06 R21, U1 | nic nie parzy po 30 min **(szac.)**; zapisać najcieplejszy element | — |
| LOG-11 | PFAIL z zapisem (F-01): w trakcie sesji rozewrzyj PWR (USB odłączony) | DHO804: CH1 P03 J_SV2.3 PFAIL_N (wyzwalanie opadające), CH2 P03 J_SV1.6 SCOPE_TRIG (GPIO41), CH3 P02 J_SV2.11 5V_SYS, 5 ms/dz | GPIO41 = H od zbocza PFAIL_N do zamknięcia plików, **≤ 10 ms**, i przed spadkiem 5V_SYS < 4,75 V; ostatnia linia `events_NNN.ndjson` to `power_fail` (reason UVLO); plik czytelny w `egrlog.py inspect` | dłużej niż 10 ms: zapisać czas; brak `power_fail`: GPIO3 / firmware |
| LOG-12 | jw., wyjęcie pakietu (XT60) zamiast PWR | jw. | jw. | — |
| LOG-13 | Zakłócenie krótkie: impuls L < 30 µs na PFAIL_N **(opcjonalnie, P00 lub generator przez 1 kΩ na J_BP2.16 P03)** | log | `pfail_glitch`, sesja trwa | — |

## 10. Odbiór firmware 6.2-s1 na sprzęcie (F-01…F-09)

| ID | Wymaganie | Gdzie sprawdzane | Kryterium |
|---|---|---|---|
| F-01 | PFAIL_N na GPIO3: napęd w dół, zamknięcie plików | LOG-11, LOG-12, LOG-13 | ≤ 10 ms od zbocza do zamknięcia (GPIO41), `power_fail` jako ostatnia linia; impuls < 30 µs = `pfail_glitch` |
| F-02 | Tryb stołowy | P03-11 | `TRYB STOLOWY`, brak katalogu sesji, licznik sesji w NVS nie rośnie (numer kolejnej sesji normalnej = poprzedni + 1), konsola działa |
| F-03 | CH7 = VBAT_SENSE, mnożnik 6,0898 (6,1918 przez R38 na P02) | P05-11, P05-12 | kod 6351 / 7938 ± 1 % przed kalibracją; w `meta.json` CH7 opisany jako akumulator auta |
| F-04 | Rozruch AD7606B: RESET 20 µs, 2100 ms, konfiguracja przed MEAS_EN, 25 ms na przekaźniki | P05-09, P05-17 | jak P05-09; po zaniku P05 pełny RESET + 2,1 s, bez samoczynnego TEST |
| F-05 | Próbkowanie i `daq_stats` | P05-10, P05-16, LOG-09 | 2 kS/s przy SPI 1 MHz: `convst` = `samples`, `lost_ticks` = 0. **10 kS/s / 4 MHz — poza tym odbiorem**: wymaga kompilacji z `EGR_SAMPLE_HZ=10000`, `EGR_ADC_SPI_HZ=4000000` i stosu z P12 |
| F-06 | Łańcuch prądu P06 R2, `current_chain` w `config` | P06-06…P06-12 | `config` zawiera `current_chain`; przy READY = 0 i w BYPASS prąd nieważny |
| F-07 | MAX31856: CS 2/2, 300 ms, odczyt CR0/CR1, błąd = NAN, fault 255 | P09-04, P09-09, P09-10 | jak w krokach |
| F-08 | CAN w osobnym zadaniu, `can_config`, `can_stats`, dekoder RPM | P10-04…P10-10 | jak w krokach; `can_config`: 500000, listen_only |
| F-09 | `profiles/hardware.json` = zmontowane rewizje | po montażu | P02 R4, P03 R6, P05 R3, P06 R2, P09 R2, P10 R2 zgodne z nadrukiem płytek; uzupełnić numery egzemplarzy w manifeście sesji |

Wszystkie obrazy mają `EGR_HARDWARE_ACCEPTED=0`. Ten odbiór tego nie zmienia: `qualify` i TEST dotyczą wariantu pełnego z P04/P07.

## 11. Poza zakresem tego dokumentu

- P04, P07, P08, P11 i P12 (nie ma ich w zamówieniu S1). Próby P03 związane z P04: zbocze SUP_N_OUT na U9.5 P04, CORE_LINK ≥ 2,7 V, prąd SUP_N_OUT przez R41 — przy odbiorze P04/P12.
- Wariant `test` / `wifi` (TEST, Wi-Fi), próba „SD + Wi-Fi 30 min” z ODBIOR P03 — Wi-Fi tylko w `wifi`, który wymaga P07.
- Kwalifikacja 4 MHz / 10 kS/s (F-05) i spadek 5V_SYS na docelowej drodze — z P12.
- Auto: P06 E20, P10 „Samochód/postój” i RPM z ECU, P05 kroki z adapterami TAPS na złączu EGR — dopiero po odbiorze stołowym i zgodnie z kolejnością w `docs/01-overview.md` (najpierw procedura v3 ze skopem, pinout CUD87 multimetrem przed wpięciem).
- O-06, O-09, O-10 P02 (VMOTOR, pakiet 5S).
