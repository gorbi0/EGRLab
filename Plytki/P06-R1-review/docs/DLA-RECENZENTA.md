# P06-R1 - zakres recenzji

To pierwsza realizacja PCB P06 I-LOGGER na podstawie v6.1-rc1. P07 pozostaje HOLD. Nie zmieniono poprzednich projektów PCB. Czytać przede wszystkim finalny schemat, PCB i BOM, a testy traktować jako dodatkowy dowód.

1. **Bocznik i bypass.** PBV F1: zewnętrzne nóżki prądowe, wewnętrzne Kelvin; nadana numeracja 1-4 od strony znakowania. SW1 S6A ma wspólne 2/5. BYPASS 2-3 i 5-6, MEASURE 2-1 i 5-4. Bocznik pozostaje w obwodzie. Bypass ma własną rezystancję i nie stanowi automatycznego zabezpieczenia.
2. **Rzeczywiste obudowy.** INA240 SOIC D ma inny pinout niż alternatywna obudowa. MCP1525, MCP1702 i MCP120 nie mają jednakowej kolejności nóżek TO92. Sprawdzić też średnice otworów PBV dla prostokątnych nóżek oraz lutowane przewody 2,5 mm².
3. **Filtr i zakres.** 5K1/5K1 + 470 nF, 133 Hz, ADC 2 ksps. Jest to trend prądu, nie oscyloskop PWM. Kalibracja ±6 A przed deklaracją zakresu; spadki 5VA ograniczają dodatnią stronę INA240 wcześniej niż nominalne ±10 A ADC.
4. **Zanik zasilania.** Ioff w U5/U6, R8=100K do lokalnej szyny oraz R24=1K. Sama obecność Ioff nie usuwa wstecznego prądu przez rezystor podciągający. Sprawdzić brak konfliktu na wspólnym DOUTA P03 i martwą szynę <0,1 V.
5. **Wzorzec i stabilność.** C5=4,7 µF przy MCP1525, bufor U2B, podział przez U2A i R5/C2 przy ADC. D1/D2 pomagają przy zaniku zasilania; wymagany test sekwencji i zwarć z ograniczonym prądem.
6. **Pobór i supervisor.** R21 celowo obciąża srebrny styk SW1. Podnosi budżet P06 do 180 mA. Zweryfikować napięcie minimalne, zwolnienie MCP120-450 i budżet HOLD całego P02. Histereza typowa nie jest gwarantowanym maksimum.
7. **PCB.** Prądowe trasy 6 mm na 70 µm, bez via; Kelvin lokalny; jeden połączony obszar GND. Obejrzeć prądy powrotne, termiki, opisy i dostęp do lutów, nie poprzestać na DRC.
8. **Wiązki.** ILOG porównany z P03-R2, LV06 z kontraktem P02. P11 jeszcze nie ma zatwierdzonej mechaniki. Przed wykonaniem W3 zweryfikować stronę i pasowanie MSTB.

Dowody: `verification/QA.md`, natywne ERC/DRC, testy netlisty i geometrii z kontrolami negatywnymi, hash wejść DRC, wynik odtworzenia. Formularz `ODBIOR.md` pozostaje niewypełniony: żaden test programowy nie jest pomiarem zmontowanej płytki.
