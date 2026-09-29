# Kamami, przewody (TME, osobny plik), uzupełnienie Farnell/Mouser, pozycje otwarte — stan 28.09.2026
# Kamami: ceny brutto ze strony produktu, dostępność z pola #product-availability
KAMAMI = [
 ('1191911', 'ZOBD SET ABS — zestaw OBD2 (12 V, typ A) z obudową, Kradex', 1, 17.02, 'Dostępny (5)', 'P10 W3', 'TME ma tylko wersję 24 V; przewody lutowane do pinów 6/14 — sprawdzić przy odbiorze'),
 ('648', 'Podstawka DIP14 precyzyjna', 2, 0.98, 'Dostępny (39)', 'P04 U2, U3', '4 szt. dla P04 z 24.09 już są'),
 ('1207058', 'Podstawka precyzyjna DIP-8P, złocone styki', 1, 5.02, 'Dostępny (16)', 'P00 U1', ''),
 ('649', 'Podstawka DIP16 precyzyjna', 1, 0.80, 'Dostępny (22)', 'P09 U3 (opcja)', 'opcjonalna wg ZAKUPY P09'),
 ('204596', 'Przewody połączeniowe F-F 17 cm, 40 szt.', 1, 5.69, 'Dostępny (276)', 'P00 wiązka stanowiskowa', 'potrzeba ok. 25'),
 ('1184699', 'Przycisk panelowy monostabilny 16x22 mm, czerwony', 1, 5.90, 'Dostępny (43)', 'P00 ARM', 'styk NO sprawdzić przy odbiorze'),
 ('1184697', 'Przycisk panelowy monostabilny 16x22 mm, zielony', 1, 5.90, 'Dostępny (44)', 'P00 SAFE_N_TEST', 'jw.'),
]

# Przewody — osobny plik TME, bo szpule są dużo dłuższe niż potrzeba (do decyzji: TME albo zakup lokalny)
WIRES = [
 ('LGY0.35/25-BK', 25, 2.97, 825, 'ok. AWG22: 12,4 m łącznie (LV, PANELSAFE/PANELCORE, VSENSE, P00)', 'szpula 25 m; drugi kolor np. LGY0.35/25-RD'),
 ('LGY0.50/25-BK', 25, 3.56, 500, '0,5 mm2: DEUTSCH P11 3,15 m + R_CHARGE P02 0,4 m', 'szpula 25 m'),
 ('LGY1.5/10-BK', 10, 8.9, 180, '1,5 mm2: P11 W5/W7 0,6 m', 'szpula 10 m'),
]
WIRES_NOTE = 'AWG24 (P05 TAPS 0,5 m, P11 W8 3,6 m): w TME tylko szpule 250 m (LIY-0.25); Kamami: silikon 24AWG 4 m — oczekiwanie na dostawę. RG174 0,15 m (P05 AUX, P11 SCOPE) z posiadanego zapasu.'

# Uzupełnienie: (pozycja, ilość, płytki, farnell(kod, cena, ilość_zakupu, stan) | None, mouser(nr, cena, stan) | None, dostawca 'F'/'M', uwaga)
SUPP = [
 ('MCP100-300DI/TO', 1, 'P04 U11', ('1332051', 1.54, 1, '1675'), ('579-MCP100-300DI/TO', 1.59, '1289'), 'F', 'TME ma tylko wariant H (inny bondout)'),
 ('TBD62083APG', 2, 'P05 U4, P08 U2', ('4178763', 12.41, 2, '1713'), None, 'F', 'Mouser: „nie sprzedaje tego produktu w Twoim regionie”; TME: DIP tylko po 79 szt.'),
 ('LTC4412IS6#TRPBF', 1, 'P03 U5', ('LTC4412IS6#TRPBF', 21.94, 1, '1986'), None, 'F', 'Mouser: „ograniczona dostępność”; TME 0 szt.; w pliku Farnella numer producenta'),
 ('G6K-2P-Y DC5', 4, 'P05 K1-K3, P08 K1', ('4446136', 19.45, 4, '5031'), None, 'F', 'Mouser 0 szt. (dostawa 08.01.2027); TME 0 szt. (tydz. 8/2027)'),
 ('STPS20100CT', 1, 'P02 (druga sztuka)', ('4035972', 11.48, 1, '517'), None, 'F', 'Mouser min. 2000; TME 0 szt. (tydz. 43/2026)'),
 ('Phoenix 1766246 GMSTBA 2,5/3-G-7,62', 1, 'P02 VMOTOR', ('2671273', 6.92, 1, '308'), None, 'F', 'TME 0 szt., termin do potwierdzenia'),
 ('Molex 39-29-6048 (4p Au, bez kołków)', 9, 'P02 J3-J10; P00 wiązka (męskie do H_LV04)', ('2751659', 6.71, 10, '538'), ('538-39-29-6048', 8.32, '489'), 'F', '10 szt. po 6,71 taniej niż 9 po 9,87; TME 0 szt., min. 10'),
 ('Molex 39-29-9069 (6p z kołkami)', 1, 'P04 J7', ('2612451', 14.31, 1, '23'), ('538-39-29-9069', 13.33, '0 (dostawa 23.11.2026)'), 'F', 'TME min. 32'),
 ('YR1B232KCC (232k 0,1 % zamiast 1 %)', 1, 'P08 R1', ('1083509', 4.19, 5, '1415'), None, 'F', '232k 1 %: Mouser i TME bez stanu w detalu; 0,1 % spełnia wymóg 1 %; Farnell min. 5'),
 ('REF5025ID (zamiast ADR4525BRZ)', 1, 'P05 U2', None, ('595-REF5025ID', 35.82, '5354'), 'M', 'ADR4525BRZ nigdzie na stanie (DigiKey 33 tyg.); REF5025: ten sam pinout SOIC-8 (2 VIN, 4 GND, 6 VOUT; 3 TEMP i 5 TRIM zostają wolne jak w P05); klasa wysoka 0,05 %, 3 ppm/K — REF5025AIDR (0,1 %) nie spełnia okna DAQ_OK (P05 R2, 29.09); zasila tylko dzielniki okna DAQ_OK'),
 ('SN74LVC1G37DBVRQ1 (zamiast SN74LVC1G37DBVR)', 1, 'P03 U4 (R5)', None, ('595-N74LVC1G37DBVRQ1', 1.10, '1883'), 'M', 'DBVR: TME 0 bez terminu, Mouser niedostępny (16 tyg.), Farnell brak; Q1 = wersja AEC-Q100 tego samego układu, SOT23-5'),
 ('MCP120-300DI/TO', 1, 'P08 U8', None, ('579-MCP120-300DI/TO', 2.27, '894'), 'M', 'TME i Farnell: min. 2000 szt.'),
 ('YR1B38K3CC (38,3k 0,1 %)', 1, 'P02 R9', ('1083424', 3.56, 1, '1239'), ('279-YR1B38K3CC', 3.86, '1726'), 'M', 'TE, 15 ppm'),
 ('YR1B15KCC (15k 0,1 %)', 1, 'P05 R3', ('1083381', 2.40, 5, '7230'), ('279-YR1B15KCC', 3.82, '7699'), 'M', 'Farnell min. 5'),
 ('YR1B6K04CC (6,04k 0,1 %)', 1, 'P05 R5 (P5-02)', None, ('279-YR1B6K04CC', 3.86, '785'), 'M', 'Farnell: brak tej wartości'),
 ('YR1B5K11CC (5,11k 0,1 %)', 3, 'P05 R7 (P5-02); P06 R3, R4', ('1083330', 2.43, 5, '183'), ('279-YR1B5K11CC', 3.82, '1038'), 'M', 'P06: 5k11 zamiast 5k1 — dzielnik R3/R4 zostaje dokładnie 1:2, obciążenie INA240 10,22 kΩ (warunek >= 10 kΩ); 5k1 0,1 % nigdzie w detalu'),
 ('YR1B24K9CC (24,9k 0,1 %)', 1, 'P05 R8', ('1083404', 3.74, 5, '965'), ('279-YR1B24K9CC', 3.86, '2825'), 'M', 'Farnell min. 5'),
 ('YR1B499KCC (499k 0,1 %)', 1, 'P05 R31', ('1083547', 1.87, 5, '1194'), ('279-YR1B499KCC', 1.93, '5336'), 'M', 'Farnell min. 5'),
 ('YR1B10RCC (10R 0,1 %)', 2, 'P06 R1, R2', ('1083036', 2.17, 5, '4468'), ('279-YR1B10RCC', 2.35, '2193'), 'M', 'Farnell min. 5'),
 ('RN55E3003BB14 (300k 0,1 %)', 1, 'P05 R33', None, ('71-RN55E3003B', 7.44, '661'), 'M', 'Vishay Dale RN55, charakterystyka E = 25 ppm/K (potwierdzić w karcie); YR1B nie ma 300k'),
 ('C&K 7201SYCBE', 1, 'P05 SW1', None, ('611-7201-054', 57.55, '10'), 'M', 'TME ma tylko 7201SYZBE (końcówki lutownicze); sprawdzić, czy 611-7201-054 to wersja SYCBE'),
 ('Molex 39-29-6148 (14p Au)', 1, 'P02 J11', None, ('538-39-29-6148', 33.13, '5730'), 'M', 'TME: min. 10 po 36,99'),
 ('Molex 39-29-6088 (8p Au, bez kołków)', 1, 'P03 J9', None, ('538-39-29-6088', 15.27, '3962'), 'M', 'BOM P03: 39-28-x08x; TME: min. 23; cynowy MX-5566-08A w TME 1,92 zł — decyzja (styki Au)'),
 ('Molex 39-29-9109 (10p z kołkami)', 1, 'P04 J8', None, ('538-39-29-9109', 22.79, '404'), 'M', 'TME: min. 21'),
 ('Molex 39-29-6128 (12p Au, bez kołków) zamiast 39-29-9129', 1, 'P11 J7', None, ('538-39-29-6128', 28.25, '2523'), 'M', '39-29-9129: Mouser 0 szt. (23.10), TME i Farnell brak; footprint 5566-12A2 przyjmuje wersję bez kołków, otwory na kołki zostają puste'),
 ('Würth 450301014042 (WS-SLTV)', 9, 'P00 CH1-CH9', None, ('710-450301014042', 8.54, '15537'), 'M', 'TME nie prowadzi Würtha'),
 ('TE DEUTSCH DT04-12PB', 1, 'P11 X2', None, ('571-DT04-12PB', 17.64, '5888'), 'M', 'TME: 0 szt., min. 32'),
 ('TE DEUTSCH DT04-12PC', 1, 'P11 X3', None, ('571-DT04-12PC', 18.83, '2450'), 'M', 'TME: min. 22'),
 ('Adafruit 4682 (microSD)', 1, 'P03 SD1', None, ('485-4682', 13.24, '812'), 'M', 'brak w TME i Kamami'),
]

OPEN = [
 ('PBV-R005-F1-0.5 (Isabellenhütte)', 1, 'P06 RSH1', 'dostępny tylko w DigiKey: 4423-PBV-R005-F1-0.5-ND, 1498 szt., 163,30 zł netto (wysyłka gratis od 300 zł); w TME, Farnellu i Mouserze brak'),
 ('EAO 14-412.036K, 14-432.036 x2, 14-435.036 x3, 14-473.036', 7, 'P11 (panel, poza PCB)', 'w TME: 14-473.036 17 szt. (132,48 zł), 14-435.036 2 szt. (77 zł), 14-412.036K 0 (389,55 zł), 14-432.036 0 (130,55 zł); zamiennik z dostępnych przycisków dobrać przy P11 R2 — nie wpływa na PCB'),
]

HOLD = [
 ('SSW-108-02-G-D-RA', 1, 'P03 J1', 'TME 9 szt., 13,56 zł', 'do zatwierdzenia przekroju B2B P03–P05'),
 ('TSW-108-08-G-D-RA', 1, 'P05 J1', 'TME 23 szt., 8,93 zł', 'BOM P05 ma TSW-108-08-G-D-NA; MECHANIKA P03 opisuje wtyk kątowy — do rozstrzygnięcia razem z przekrojem'),
]

OPTIONAL = [
 ('OBJ35', 3, 'P02 bank HOLD', 'TME: obejma poliamidowa do kondensatora Ø35 mm, 11,23 zł, na stanie 1 szt.; mechanika do przymiarki'),
 ('7J360100020100A000', 2, 'P09 TC1, TC2', 'TME: termopara K Guenther, PFA, -40..260 C, 1 m, wtyk mini-K, 64,96 zł; spoina izolowana nie jest potwierdzona w parametrach. Tylko jeśli termopary nie przyszły z modułami MAX31856'),
 ('ICVT-18P', 10, 'P05 U4, P08 U2 (opcja)', 'TME: podstawka DIP18 (nie precyzyjna), min. 10, 0,60 zł; w Kamami DIP18 czeka na dostawę'),
]
