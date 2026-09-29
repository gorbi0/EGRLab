# P06-R1 względem v6.1

1. Konkretne obudowy, numeracja i lokalne biblioteki; INA240 **SOIC D** ma inny pinout od TSSOP PW. SW1 NKK ma styki wspólne 2 i 5. U10 MCP1525 TO92 ma VIN na 3, GND na 1.
2. Bocznik PBV 5 mΩ / 0,5% / 3 W bez radiatora, zamiast niezdefiniowanej części 5 mΩ. Projekt biernego toru na 10 A, przewody 2,5 mm², miedź 6 mm / 70 µm, bez przelotek mocy.
3. Lokalny ADC MCP3201 i wzmacniacze bez zmiany funkcji zewnętrznych pinów. SOIC8/SO14 lutowane bezpośrednio, 1,27 mm. DIP/TO92/THT dla pozostałych układów; małe odsprzęganie 0805.
4. R3/R4 z 2 kΩ na 5,1 kΩ, aby obciążenie INA240 wynosiło co najmniej 10 kΩ. C1 z 4,7 nF na 470 nF PET: filtr około 133 Hz do rejestracji trendu przy 2 kS/s, zamiast przepuszczania PWM do wolnego ADC. Skala DC 1:2 bez zmiany.
5. Osobny tor położenia SW1 z obciążeniem 39 Ω / 2 W dla srebrnego styku. READY LOW w BYPASS. Wzrost budżetu zasilania opisany w PROJEKT.md.
6. U6 wykorzystany także do translacji styku i buforowania READY z Ioff. Dodane pull-downy po buforach oraz rezystory szeregowe DOUT 47 Ω i READY 100 Ω. Nieaktywne OE związane z lokalnym 3,3 V.
7. R8 na zewnętrznym CS = 100 kΩ zamiast 10 kΩ, R24 bleed = 1 kΩ. Ograniczenie zasilania wyłączonej domeny przez rezystor, którego sam Ioff nie blokuje.
8. Większy C3 470 µF, D1/D2 dla rozładowania szyn; osobne lokalne odsprzęganie VREF przy ADC. Wymagane próby startu/zaniku, nie deklaracja odporności na nieprzebadane zwarcia.
9. Zamiast rezerwacji obrysu 80 × 65 mm: rzeczywista PCB **120 × 100 mm** z miejscem na lutowanie przewodów, duży bocznik i odstęp od gorącego R21. P06 jest samodzielnie mocowana, nie w stosie CORE-DAQ. Obudowę urządzenia dobrać do tej wersji; dawny obrys był założeniem, nie zgodnym mechanicznie zamiennikiem.
10. Wszystkie pięć wiązek lutowane w PTH po stronie P06, z kotwą 12 mm. Zewnętrzne kontrakty ILOG, LV06, ISERIES bez zmiany numeracji. Własne SW1-A i SW1-B nie są nowymi magistralami między modułami.

Zmiany nie podwyższają limitów aktywnego testowania EGR. Nie zmieniono P02/P03/P04/P05 ani firmware bazowego. P07 pozostaje HOLD. Ten pakiet nie jest nową rewizją całego EGRLab.
