# Zasilanie i wspólny reset

Aktualizacja R5: U4 Schmitt/open-drain; reset do P04 przez U6. Współpraca z P04-R2.2 R17=10 kΩ.

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

## Reset wspólny i wyjście do P04

```text
TPS3808 -> SUP_RAW_N (R13=10k do 3V3_CORE) -> U4 LVC1G37 (Schmitt, OD)
 -> R34=220R -> SUP_N -> EN M1 + RESET MCP23017 + wejście U6 LVC1G17
U6 push-pull -> R41=220R -> SUP_N_OUT -> J4.15 -> P04 J2.15/U9.5
                                                R17=10k do GND
```

U4 ma NC1, A2, GND3, Y_OD4, VCC5. U6 ma taki sam układ numerów, ale inne wyjście: **nie zamieniać tych układów miejscami**. U4 musi pozostać open-drain, aby przycisk i DTR/RTS mogły również wymusić reset. R35=10 kΩ jest równoległy do fabrycznego EN 10 kΩ; fabryczny C_EN=1 µF pozostaje.

### Wejście supervisora i U4

R13=10 kΩ pozostaje zgodnie z zaleceniem TPS3808 (pull-up nie mniejszy niż 10 kΩ). Poprzedni LVC1G07 wymagał szybkiego wejścia. Nowy LVC1G37 ma histerezę i dopuszcza szybkość przejścia do 100 ms/V. Nie ma potrzeby przyspieszać tego węzła kosztem supervisora. U4 przejmuje prąd rozładowania C_EN przez R34: 3,465 V / (220 Ω × 0,99) = 15,91 mA, poniżej zalecanego prądu wyjścia 32 mA przy 3 V. [TI TPS3808](https://www.ti.com/lit/gpn/TPS3808), [TI LVC1G37](https://www.ti.com/lit/gpn/SN74LVC1G37), lokalna karta `reference/datasheets/SN74LVC1G37.pdf`.

### Poziom LOW wspólnego resetu

Do obliczeń przyjmujemy VOL U4 = 0,4 V (karta: 16 mA, VCC=3 V), zamiast przenosić specyfikację dla 100 µA na większy prąd. Przy nominalnych 10 kΩ || 10 kΩ i R34=220 Ω:

`SUP_N = (VOL × Rpull + VDD × R34)/(Rpull + R34)`

Wynik wynosi 0,522 V przy 3,3 V albo 0,510 V przy 3,0 V. Budżet tolerancji w `verify_reset.py` przyjmuje R34/R35 ±1%, fabryczne EN 10 kΩ ±5% (do potwierdzenia na posiadanym module). Najgorsze obliczone LOW przy 3,0 V pozostaje poniżej progu MCP23017 0,2 VDD = 0,6 V, a także VT− U6. Wynik dotyczy ustalonego zasilania ≥3 V; zachowanie przy zapadzie i rozruchu mierzymy. Sprzęt NIE ZBADANO.

### P04 z wyłączonym CORE

U6 ma Ioff o module do 10 µA; wejście Nexperia 74LVC125A do 5 µA w zakresie do 85°C lub 20 µA do 125°C. Konserwatywny budżet sumy modułów wynosi odpowiednio 15/30 µA. Z R17=10 kΩ ±1% daje 0,152/0,303 V < VIL=0,8 V. To graniczny budżet, nie pomiar kierunku upływu. Nie narzuca temperatury pracy całego urządzenia 125°C. [TI LVC1G17](https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf), [Nexperia 74LVC125A](https://assets.nexperia.com/documents/data-sheet/74LVC125A.pdf).

Przy aktywnym CORE R17 obciąża U6 około 0,33 mA. Konserwatywne VOH U6=2,4 V, R41, R17 i 20 µA upływu odbiornika nadal dają na U9.5 ponad VIH=2,0 V. Nie łączyć 3V3_CORE z 3V3_IO. Po zaniku/resetowaniu CORE P04 ma się rozbroić; powrót zasilania nie odtwarza ARM.

### Zbocze na końcu taśmy

R41=220 Ω pozostaje jako wartość początkowa ograniczenia zwarcia i tłumienia. Idealne RC dla założonych 20 pF daje τ=4,4 ns i 10–90% około 9,7 ns. Ten model nie obejmuje impedancji i szybkości wyjścia U6, rzeczywistej taśmy, niezerowego VOL oraz sondy. **36 pF nie jest gwarantowaną granicą.** Czas 10–90% sam nie dowodzi spełnienia limitu 10 ns/V w całym obszarze przełączania.

Na docelowej taśmie H_SAFE 150 mm mierzyć oba zbocza bezpośrednio na P04 U9.5: pojedyncze monotoniczne przejście przez 0,8–2,0 V, szybkość zgodna z ≤10 ns/V, brak dodatkowych impulsów na U9.6/SUP_OK. Podać model/pasmo przyrządu, pojemność sondy i długość połączenia masy; sonda jest częścią obciążenia. Kryterium obowiązuje również po każdej zmianie R41 lub długości taśmy. Nie utożsamiać tej próby z pomiarem milisekundowego EN.

SUP_N narasta nominalnie z τ≈5 ms. Próg U6 daje nominalne opóźnienie około 2,6–4,0 ms po zwolnieniu U4; przy narzuceniu resetu około 0,2–0,3 ms. To szacunki dla nominalnych RC, nie gwarantowane przedziały wszystkich egzemplarzy. Dochodzi opóźnienie TPS3808. Przyciski/DTR/RTS resetują ESP i MCP wspólnie; po starcie pełne board_init(), inicjalizacja ekspandera i nowa sesja, bez automatycznego ARM. Reset programowy bez zmiany EN nadal wymaga pełnej inicjalizacji.

Nagły zanik zasilania może uniemożliwić zapis zdarzenia. Zachować dane do ostatniego poprawnego bloku i potraktować restart jako nową sesję. Nie przypisywać przyczyny przycisk/zapad wyłącznie na podstawie EN.
