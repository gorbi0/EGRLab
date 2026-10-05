# Kontrakt wydania P08-R1

P08 jest modułem zasilania czujnika w TEST. W LOGGER źródłem zasilania czujnika pozostaje ECU. P08 nie ustala polaryzacji pinów zaworu, nie steruje silnikiem i nie zastępuje zabezpieczeń P04. P07 nadal HOLD.

## Granice modułu

- LV08 do P02-R3/J8: 1=5V_SYS, 2=GND, 3=3V3_IO, 4=GND.
- SENSOR do P04-R2.1/J4: 1=PERMIT, 2=KEY/NC, 3=OK, 4=GND, 5/6=NC.
- SFAULT do P03-R2/J6: 1=HEALTHY, 2=GND, 3=KEY/NC, 4/5/6=NC.
- TSENSOR do przyszłej P11: 1=5V_SENSOR, 2=AGND_SENSOR; mapowanie na zawór poza P08.
- J1–J3 lutowane do PTH na P08, kotwy 12 mm od pierwszego rzędu lutów. J4 jest gniazdem na PCB; wiązka W4 należy do P11.
- Budżet: 5V_SYS 200 mA, 3V3_IO 15 mA. PCB 100 × 80 mm, 2 warstwy, FR4 1,6 mm, Cu 35 µm/stronę. Rezystory pojedyncze THT DIN0207.

## Wymagane zachowanie

K1 rozłącza oba przewody czujnika. AGND_SENSOR nie może zostać zwarta z GND poza stykiem K1. Bez poprawnych obu szyn nie ma zezwolenia; FAULT TPS nie może tworzyć cyklu samoczynnego wyłączania/włączania EN. U8 wymusza LOW na EN podczas brownout. Bufory między płytkami muszą obsługiwać Ioff przy wyłączonej domenie; zamiana na HC125 niedozwolona.

R1=232 kΩ/1% daje około 117 mA typowo, obliczeniowo około 99–139 mA. Nie traktować tego jako zabezpieczenia 20 mA do identyfikacji nieznanego sensora. SENSOR_OK oznacza poprawne szyny; HEALTHY poprawne szyny i brak FAULT. Nie potwierdzają one styków przekaźnika ani napięcia na sensorze.

## Obowiązkowe zadanie integracji firmware — otwarte

Przed pierwszym PERMIT i po zaniku zasilania odczekać 750 ms ciągłego SENSOR_OK/HEALTHY. Zerować licznik przy braku gotowości, błędzie komunikacji i przeterminowaniu danych. Bazowy board_mode() z 100 ms nie spełnia tego kontraktu samodzielnie. Ten pakiet nie zmienia wspólnego firmware; zadanie jest otwarte do uruchamiania systemowego. Usterka w aktywnym TEST wymaga zatrzaśnięcia błędu, cofnięcia PERMIT i świadomego wznowienia.

## Bramka odbioru plików i sprzętu

Pliki: ERC/DRC/parity 0, niezależne kontrole netlisty i geometrii, kontrole negatywne, odtworzenie od pustego CAD, obejrzenie każdej strony PDF, manifest. Sprzęt: osobno wszystkie punkty verification/ODBIOR.md, w tym przymiarka, prąd, sekwencje szyn, brownout i margines cewki. Wyniku komputerowego nie przenosić do formularza pomiarów.
