# Zamrożony kontrakt P09-R1

1. Dwa kupione moduły MAX31856 XU, bez założenia identyczności z Adafruit. Dziewięć pinów w ustalonej kolejności;3Vo tylko do TP.
2. LV09=P02-R3/J9. TEMP=P03-R2/J7,10p KEY4. Brak zmian sąsiednich PCB i brak dodatkowych żył FLT/DRDY.
3. Logika3V3, dwa bufory74LVC125AD z Ioff, statyczny wybór MISO przez HC139. ObaCS=0 lub1: żaden MISO aktywny. Przerwa obuCSHIGH≥1µs wymagana w firmware.
4. VIN per moduł wybierany pomiędzy3,3 i5V pojedynczą zworą. Domyślnie brak zwór.5V wymaga kwalifikacji regulatora i interfejsu.
5. Dwie warstwy,100×100mm,1,6mm,Cu35µm; ścieżki≥0,30mm, prześwit≥0,25mm; bez wyłączeń DRC. Rezystory pojedyncze THT DIN0207.
6. Taśmy lutowane do PTH naP09, kotwy10–15mm od lutu. Zakupione moduły w rozłącznych listwach. Podparcie nylonowe, przymiarka przed produkcją.
7. Żadnych termoparowych sygnałów analogowych na nośniku; zaciski pozostają na module. Dwie termoparyK z izolowaną spoiną. Brak izolacji galwanicznej systemu.
8. Patch odczytu temperatury przeciwko niezmienionej bazowej v6.1, testy rzeczywistej funkcji i błędnych wariantów. Brak deklaracji pełnej integracji firmware lub badań fizycznych.
9. Pakiet do recenzji; Gerbery dopiero po fizycznym sprawdzeniu modułów i zatwierdzeniu finalnej geometrii.
