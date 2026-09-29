# Zasilanie i wspólny reset

*R3 (27.09.2026): poprawiony poziom LOW wspólnego resetu, dopisane zbocze SUP_N na złączu do P04 i potwierdzenie LTC4412 z lokalnej karty. Układ bez zmian.*

## Dwa źródła 5 V

```text
P02 / J10.1 / 5V_SYS ---- D Q1 AO3401A S ---- 5V_M1 ---- M1.J1-21
                         |           |           |
                   U5 VIN/GATE     U5 SENSE      C14
USB ---- fabryczna D1 Waveshare ------------------+
```

Q1 ma diodę pasożytniczą od drenu (SYS) do źródła (M1). LTC4412 porównuje oba napięcia i zamyka MOSFET przy wstecznym przepływie. Karta (Linear 4412f, s. 5–6, kopia w `reference/datasheets/LTC4412.pdf`) potwierdza, że układ zasilają **oba** piny, VIN i SENSE, a bramka jest klampowana 7 V poniżej wyższego z nich. Bez P02 (VIN = 0) i z USB na SENSE kontroler działa więc dalej, jest w trybie wyłączenia wstecznego i trzyma Q1 zamknięty. STAT pozostaje NC, CTL=GND. Piny: U5 1=VIN, 2=GND, 3=CTL, 4=STAT, 5=GATE, 6=SENSE; Q1 1=G, 2=S, 3=D. Źródło nie może zostać zamienione z drenem. [LTC4412](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4412.pdf), [AO3401A](https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf).

| P02 / 5V_SYS | USB | Stan oczekiwany |
|---|---|---|
| ON | OFF | Q1 przewodzi SYS → M1; fabryczna D1 blokuje powrót do VBUS |
| OFF | ON | M1 działa z USB; Q1 blokuje zasilanie SYS z M1 |
| ON | ON | Zasilanie M1 zależy od napięć i spadków obu torów; brak gwarantowanego priorytetu USB/P02 |
| OFF | OFF | CORE gaśnie; nie powinien być podtrzymywany przez linie sygnałowe |

U5/Q1 blokują zasilanie **szyny 5 V** z USB. Nie jest to izolator sygnałów, odłącznik masy ani ogranicznik prądu. Krótkie prądy przejściowe podczas przełączania są możliwe. Zasilanie częściowe przez inne połączenia trzeba sprawdzić z faktycznie zmontowanymi P04/P05/P09/P10, nawet gdy zastosowano bufory Ioff. Nie łączyć 3V3_CORE z 3V3_IO.

Projektowy punkt odbioru: do 0,5 A średnio i 0,8 A w impulsie dla całego CORE, napięcie na J10.1 co najmniej 4,85 V pod obciążeniem. To limit roboczy do potwierdzenia, nie zmierzony pobór ani gwarancja Waveshare. Dla oszacowania przyjęto 2 × 85 mΩ MOSFET-u (konserwatywny mnożnik temperaturowy, nie gwarantowana granica producenta) i do 50 mΩ miedzi toru głównego. Przy 0,8 A spadek wynosi ok. 176 mV, zatem 5V_M1 ≈4,67 V. Nominalny spadek przy małym prądzie wynika z regulacji kontrolera. Rezystancję miedzi i obciążenie weryfikuje się pomiarem; nie porównuje się wartości typowej z granicą maksymalną bez zapasu.

Przy konserwatywnym budżecie spadku LDO 1,3 V pozostaje ok. 70 mV ponad 3,3 V. Wymagany pomiar: 5V_M1 ≥4,60 V i stabilne 3V3_CORE podczas zapisu SD / używanego trybu radiowego, również po rozgrzaniu. Identyfikować regulator na faktycznej płytce, zamiast zakładać, że każdy moduł rodziny ma identyczny LDO. Jeśli zapas jest za mały, poprawić zasilanie/przewód lub osobno zrewidować zasilanie CORE — nie obniżać progu resetu, aby ukryć zapady.

W USB-only spadek fabrycznej D1 i kabla jest niezależny od U5; tanie kable mogą nie przejść powyższego odbioru. USB-only służy najpierw do programowania CORE. Przed spięciem z komputerem potwierdzić ciągłość VBUS → D1 → pin 5 V i wartości sieci EN na konkretnym N32R16V. [Schemat Waveshare rodziny](https://files.waveshare.com/wiki/ESP32-S3-DEV-KIT-N8R8/ESP32-S3-DEV-KIT-N8R8-schematic.pdf).

## Reset bez rozjazdu stanu MCP i ESP32

```text
3V3_CORE -> TPS3808G33 -> SUP_RAW_N -> U4 (nieodwracający OD) -> R34 220R -> SUP_N
                                                                        +-> EN M1
                                                                        +-> RESET MCP23017
                                                                        +-> J4.15 / P04
```

R13 10K podciąga SUP_RAW_N; R35 10K podciąga SUP_N. Na module pozostają EN 10K/1uF i układ DTR/RTS. U4 przejmuje rozładowanie pojemności EN, dlatego wyjście TPS3808 nie dostaje jej bezpośrednio. Wyłącznie SN74LVC1G07DBVR (wyjście OD); nie zastępować zwykłym buforem push-pull. [TPS3808](https://www.ti.com/lit/ds/symlink/tps3808.pdf), [SN74LVC1G07](https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf).

Oszacowanie: 3,465 V / (220 Ω × 0,99) <16 mA chwilowego prądu rozładowania, poniżej projektowego 24 mA dla zasilania U4 około 3 V. Dwa rezystory 10K równolegle dają ok. 5K; przy niskim resecie prąd statyczny jest mniejszy od 0,7 mA. W stanie ustalonym U4 ma VOL ≤ 0,1 V (IOL 100 µA–0,7 mA), a spadek na R34 wynosi ok. 0,15 V, więc LOW ≈ 0,25 V. To poniżej progu RESET MCP23017 (wejście Schmitta, VIL = 0,2 VDD ≈ 0,66 V), progu EN ESP32 i 0,8 V wejścia LVC w P04. (R2 podawało „poniżej 0,7 V” z VOL przy 24 mA — to nie dowodziło progu MCP.) R17=100K do GND na P04 daje w HIGH ok. 95% napięcia CORE. Fabryczne 1uF i 5K dają ok. 5 ms narastania po zwolnieniu U4; dochodzi opóźnienie TPS3808 (CT otwarte). Rzeczywiste zbocza i progi trzeba zmierzyć.

Zapad poniżej progu supervisora zatrzymuje jednocześnie MCU i MCP, a P04 dostaje LOW. Reset przyciskiem lub DTR/RTS M1 również resetuje MCP i P04. Po starcie aplikacja wykonuje pełne `board_init()`, inicjalizuje IODIR/OLAT oraz rozpoczyna nową sesję pomiarową; nie wolno automatycznie odtwarzać ARM. Wymuszenie RESET samego ekspandera przez SUP_N jest teraz resetem obu układów. Reset programowy MCU bez zmiany EN nadal wymaga pełnej inicjalizacji aplikacji.

R2 nie dodaje do firmware rejestracji zdarzenia przed nagłym zanikiem zasilania: taki zapis może być niemożliwy. Należy zachować log do ostatniego poprawnego bloku i rozpoznać nowy start jako nową sesję. Nie można bez dodatkowego źródła informacji rozróżnić przycisku od zapadu wyłącznie na podstawie wspólnego EN.

## Zbocze SUP_N na złączu do P04 (R3)

SUP_N jest tym samym węzłem co EN modułu z fabrycznym 10K/1 µF. Narasta z τ ≈ (R35 ∥ 10K modułu) × 1 µF ≈ 5 ms, co przy progu daje ok. 2,8 ms/V. Opada przez R34 z τ ≈ 0,22 ms. P04 odbiera SUP_N na 74LVC125A (U9.5), który wymaga Δt/ΔV ≤ 10 ns/V (Nexperia Rev. 12, tab. 5). To odstępstwo od karty. Przy przejściu przez próg możliwe są serie impulsów na SUP_N_P04 i SUP_OK. RESET MCP23017 ma wejście Schmitta, a EN ESP32 jest projektowany na zbocze RC, więc sam P03 tego problemu nie ma.

Skutki w P04-R2.1:
- Zatrzask ARM (74HC74) nie może się ustawić, bo jego zegar pochodzi wyłącznie z przycisku ARM przez 74HC14, a PRE = H.
- Przy zwolnieniu resetu HEARTBEAT = L (MCU jeszcze w resecie), więc HC123 nie wyzwala.
- Przy narzucaniu resetu (zapad) MCU może jeszcze pracować. W czasie trwania serii możliwe są krótkie wznowienia WD_Q i SENSOR_PERMIT, bez HW_ARMED i bez zgody na silnik.

Stan końcowy jest zawsze rozbrojony. Pomiar: próba „Zbocze SUP_N na P04” w `ODBIOR.md` (razem z E16 P04).

Czyste rozwiązanie to bufor Schmitta SN74LVC1G17 (DBV, jak U4) z rezystorem szeregowym przed J4.15. Wymaga to nowego trasowania i ponownej recenzji layoutu, dlatego R3 go nie wprowadza. Decyzję zostawiono użytkownikowi (`docs/ZMIANY-R3.md`).

