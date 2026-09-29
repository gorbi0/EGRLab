# P02-R3 — progi i ograniczenia HOLD

*R3 (Claude, 26.09.2026): progi, rezystory i filtry bez zmian względem R2 (obwiednie odtworzone niezależnie w recenzji). Dopisano: pracę przy zgaszonym silniku, wykrywanie przerwanego F1, dobór wkładek F2–F4 i prąd LED.*

Stan: obliczenia i kontrola netlisty, **sprzęt NIE ZBADANO**. Temperaturą projektu jest 0…50°C wewnątrz obudowy.

## Znaczenie kontrolki

HOLD_READY = BANK_OK AND VPROT_OK AND PSU_OK. Jest to **lokalna informacja napięciowa**. J12.3 nadal kończy się NC po stronie P04. Nie zmieniono firmware ani ARM. CORE nie odmierza 15 s w tej rewizji.

Kontrolka nie sprawdza pojemności, ESR ani wydajności przetwornic. Przerwany F1 wykrywa z opóźnieniem: odcięty od ładowania bank rozładowują R1 ∥ (R6 + R7), τ ≈ 280–330 s. LED gaśnie więc po ok. 1–2 min — 55–85 s przy nominalnym C, najdłużej ok. 115 s przy C +20 %, najniższym progu wyłączenia i starcie z 13,5 V (`check_electrical.py`, kontrola „Open F1”). Po montażu trzeba wykonać test podtrzymania. Podczas pracy operator kwalifikuje rezerwę dopiero po 15 s stabilnego zasilania i świecenia LED. Po zgaśnięciu lub zaniku zasilania kwalifikację powtarza od początku. Na stole przyjąć VPROT=13,5 V. Przy słabym akumulatorze LED może nie zapalić się mimo działających przetwornic; urządzenie wtedy nie ma zakwalifikowanej rezerwy HOLD.

**Zgaszony silnik (R3).** Próg załączenia VPROT_OK wynosi nominalnie 12,25 V (obwiednia 11,81–12,62 V). Akumulator w spoczynku daje ok. 12,2–12,7 V, a P01 odejmuje ok. 0,05–0,1 V. W trybie TEST/HOT-SOAK przy zgaszonym silniku kontrakt HOLD (VPROT ≥ 11,5 V, bank ≥ 9,5 V) bywa spełniony, a kontrolka zależnie od egzemplarza nie świeci. Progów celowo nie obniżono, bo gwarantują zasadę „LED świeci ⇒ kontrakt spełniony”. Kwalifikacja ręczna przy zgaszonym silniku: przez 15 s TP1 ≥ 11,6 V i TP3 ≥ 9,7 V, mierzone multimetrem 10 MΩ (TP3 przez R20 1 kΩ: błąd ok. 0,01 %). Pomiar banku jest wprost warunkiem kontraktu C1.

## Tor analogowy

```
HOLD_STORE/VPROT -- Rt -- X -- Rs -- Y --> LM2903 (+)
                         |          |
                       Rb || C      Rf
                         |          |
                        GND        OUT -- Rp -- 3V3_IO
LM2903 (-) <-- TL431BILP, K=REF, 2,495 V
```

| Tor | Rt | Rb | Rs | Rf | Rp | C |
|---|---|---|---|---|---|---|
| Bank | R6 30,1 kΩ 0,1% | R7 10 kΩ 0,1% | R18 10 kΩ 1% | R8 1 MΩ 1% | R12 10 kΩ 1% | C14 10 nF |
| VPROT | R9 38,3 kΩ 0,1% | R10 10 kΩ 0,1% | R19 10 kΩ 1% | R11 1 MΩ 1% | R13 10 kΩ 1% | C15 10 nF |

C14/C15 są na X, a dodatnie sprzężenie na Y. R18/R19 rozdzielają te węzły. R6/R9 pozostają przy źródłach, tak aby długa ścieżka była już ograniczona rezystancją. R5=330 Ω zapewnia około 7,6 mA TL431. C16=100 nF jest dodatkowym kondensatorem na adapterze U5, bez nowego footprintu na P02.

## Obliczenia, odtwarzane z wartości eksportowanej netlisty

Dla A=1+Rt/Rb, S=A·Rs+Rt, Vt=Vref+Vos i prądu Ib skierowanego **do** wejścia:

`Vin = A·Vt + S·(Vt−Vout)/Rf + S·Ib`

Stan wysoki uwzględnia obciążenie rezystora podciągającego:

`VoutH = (VIO/Rp + Vt/Rf − Ileak)/(1/Rp + 1/Rf)`.

Skrypt `src/check_electrical.py` sprawdza 1024 kombinacje graniczne na tor: dzielniki 0,1% + 25 ppm/K × 25 K; pozostałe 1% + przyjęte 100 ppm/K × 25 K; VIO 3,135…3,465 V; VOL 0…0,7 V; prąd wejścia −500…0 nA; upływ wyjścia 0…1 µA. TL431BI: początkowo 2,483…2,507 V, konserwatywnie ±34 mV dryftu całego zakresu przemysłowego, dodatkowo ±4 mV na zmianę prądu katody. Vos LM2903: ±15 mV z pełnego zakresu temperatur. To szersza obwiednia niż nominalne warunki 0…50°C; starzenia wieloletniego nie obejmuje.

| Tor | Nominalnie rosnący / opadający | Obwiednia rosnącego | Obwiednia opadającego |
|---|---|---|---|
| Bank | 10,170 / 9,949 V | 9,805…10,474 V | 9,612…10,252 V |
| VPROT | 12,254 / 11,982 V | 11,810…12,623 V | 11,573…12,349 V |

Wartości są progami DC, nie gwarantowanym czasem reakcji. Nominalny VOL przy obliczeniu środka: 0,15 V. Obwiednie obu progów mogą się przecinać między różnymi egzemplarzami; histereza pojedynczego egzemplarza jest dodatnia (bank min. 166 mV, VPROT min. 205 mV).

Szybki skok dodatniego sprzężenia na Y ma co najmniej ok. 23 mV w tym modelu. Dla pojemności filtra do 13 nF stałe czasowe są około 97/102 µs (wartości rezystorów nominalne; do odbioru przyjmujemy 110 µs). Brak kondensatora na Y usuwa problem ładowania C14/C15 przez dodatnie sprzężenie. Pojemności pasożytnicze, odpowiedź samego LM2903 i zakłócenia od silnika wymagają pomiaru oscyloskopem; nie zastępujemy go obliczeniem RC. Nagły zanik VPROT gasi status z opóźnieniem układu — status nie jest wyjściem awaryjnego odcięcia mostka.

## Kontrolka LED (R3)

R16 = 470 Ω: przy VOH U6C 3,0–3,3 V i Vf 1,8–2,2 V prąd LED1 wynosi ok. 1,7–3,2 mA. W R2 było 1 kΩ, ok. 1,1 mA, słabo widoczne w kabinie. Wyjście U6C obciąża łącznie ok. 3,5 mA: LED, R15 i nieobciążony J12.3.

## Bezpieczniki (R3)

Schurter SPT 5 × 20 (ceramiczne, zwłoczne, 250 VAC / 300 VDC, UL 1500 A przy 300 VDC): F1 T2A (0001.2507), F2/F3 T1A (0001.2504), F4 T0,5A (0001.2501). Uzasadnienie i otwarte pozycje zakupowe: `ZAKUPY-P02.md`.

## Rezerwa energii i budżet

Cel pozostaje: co najmniej 50 ms przy łącznej mocy **6 W pobieranej z VLOG_RES**, a nie 6 W sumy wyjść przetwornic. Wliczyć straty obu TSR. P07/VMOTOR nie jest podtrzymywany.

Model graniczny: Ceff≥52,8 mF, bank przed zdarzeniem≥9,5 V, VLOG_RES≥7 V, strata toru bank→VLOG_RES≤1,2 V. Z dodatkowym 0,15 W rezerwy na upływy i nadzór:

`t = 0,0528 · ((9,5−1,2)²−7²) / (2·6,15) = 85,4 ms`.

To zapas w modelu; limit 1,2 V trzeba zmierzyć (D1, F1, styki i ESR). F2/F3 i napięcia na VIN TSR sprawdzić osobno. Kontrolka nie dowodzi spełnienia tych założeń. Przy 13,5 V, D2≤1 V, R17+5%, C+20% i obciążeniu upływami ≤0,15 W bank powinien przekroczyć górny próg w 15 s; potwierdzić realnym pomiarem, zwłaszcza na zimno.

## TP3 i rozładowanie

R20=1 kΩ / 2 W / 5% jest bezpośrednio przy odgałęzieniu banku; TP3 znajduje się dopiero za nim. Przy 32 V i tolerancji z TCR zwarcie TP3 daje ≤33,91 mA i ≤1,086 W. DMM 10 MΩ zaniża wynik o około 0,01%; wejście 1 MΩ o 0,1%. Do pomiarów szybkich uwzględnić RC sondy z R20; TP3 nie służy do wyznaczania bardzo szybkich skoków ESR bez korekcji pasma.

TP3 nie jest wyjściem mocy ani punktem rozładowywania. Bank ma 33,79 J nominalnie i 40,55 J przy C+20%, 32 V. R1 rozładowuje do 1 V w maks. około 21,7 min (R+1%, C+20%). Przed montażem/serwisem zmierzyć napięcie. Dostępny tor serwisowy: przez zamontowany F1 i zewnętrzny izolowany rezystor 100 Ω / ≥10 W o dopuszczalnym impulsie ≥41 J; nie traktować samego napisu „10 W” jako gwarancji impulsowej.

## Źródła granic

- [TI TL431, tabela 6.12 i wyprowadzenia LP](https://www.ti.com/lit/ds/symlink/tl431.pdf).
- [TI LM2903, tabela parametrów klasycznego LM2903](https://www.ti.com/lit/ds/symlink/lm2903.pdf).
- [Vishay MBB precision, tolerancje, TCR i kod zamówienia](https://www.vishay.com/doc?28767=).
- [Vishay PR02, moc i TCR R20](https://www.vishay.com/docs/28729/pr010203.pdf).
- [TRACO TSR2](https://www.tracopower.com/products/tsr2.pdf), kopia tekstowa w `reference/TRACO_TSR2.txt`.

Ostateczną ocenę stabilności i reakcji na zaniki wykonuje się na sprzęcie według `verification/ODBIOR.md`.
