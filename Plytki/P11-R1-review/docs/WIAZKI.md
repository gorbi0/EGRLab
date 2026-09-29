# Wiązki, numeracja i mechanika P11

Źródłem montażowej listy każdej żyły jest `lista-przewodow.csv`.
`interfejsy.csv` określa długość, zakończenia, lutowany koniec i właściciela BOM.
Wszystkie długości liczone od lutu do styku, wraz z łukiem odciążającym.

PCB:160×110 mm, patrząc od strony elementów napis EGRLab u góry.
M3:(5,5),(155,5),(5,105),(155,105) mm. Dystanse≥10 mm,podkładki OD≤8 mm.
J1/J7 pionowe; zostawić miejsce na zatrzask Mini-Fit i wyjęcie wtyku MSTB,
co najmniej30 mm wolnej wysokości ponad PCB jako wstępna przestrzeń obsługowa.
Przymiarka konkretnych wtyków rozstrzyga wymagania obudowy.

| PCB | Rząd górny od lewej | Rząd dolny od lewej |
|---|---|---|
| J2,J3,J8 ogonki DT | 7,8,9,10,11,12 | 1,2,3,4,5,6 |
| J4 CORE8 | 1,2,3,4 | 5,6,7,8 |
| J5 SAFE10 | 1,2,3,4,5 | 6,7,8,9,10 |
| J11 CONTACT20 | 1…10 | 11…20 |
| J7 Mini-Fit12 | 1…6 | 7…12 |

J1:1–4 od lewej. J9:1–5 od lewej. J6/J10:1,2 od lewej.
PTH1 jest kwadratowy. **Nie jest to numeracja IDC „nieparzyste/parzyste”.**
Nie wnioskuj z ułożenia żył o numerze styku po drugiej stronie. Numery komór
DEUTSCH i Mini-Fit czytać z oznaczeń producenta, osobno dla strony czołowej/tylnej.

Kotwy PTH mają po dwa otwory NPTHØ3,2 mm i strefę bez miedzi pod opaską.
Odległość osi kotwy od rzędów: J2/J3/J8=10,5/14,7 mm,J4/J5/J11=10,5/14 mm,
J6/J10=10,5 mm,J9=12 mm po przeciwnej stronie. Lutować linkę do otworów,
zostawić łuk; opaska2,5 mm trzyma izolację, nie cynę. Obciążenie wiązki nie może
przenosić się na lut. Nie ciągnąć przewodów nad otworami M3 ani zatrzaskiem J7.

PANELSAFE i PANELCORE:300 mm,AWG22, oddzielne od torów silnika.
Obsadzać tylko wskazane pozycje; NC zostawić puste. W1=7 styków,W2=7,W4=2.
Na samej PCB NC mają pola wyłącznie dla czytelnej numeracji.
W3 TMOTOR:2×2,5 mm²150 mm,nie wykonywać wtyku do czasu zatwierdzenia P07.
W4 TSENSOR:2×AWG22 150 mm,do P08/J4;AGND_SENSOR nie jest GND panelu.

Ogonki portów W5/W6/W7:150 mm do gniazd DT. Moc1,5 mm²,pozostałe0,5 mm²,
stosownie do TE0460-202-1631. Moc można skręcić parą; TAPy prowadzić z dala
od PWM/motoru, z uporządkowanym powrotem GND. Nie dodawać GND do X8.12 ani
zwory AGND_SENSOR–GND. NC komór portów zaślepić. TE pin Au po obu stronach
pary musi współpracować z odpowiednim stykiem Au socket w adapterze.

W8:18 żył AWG24 po maks.200 mm. Pary:

| J11 | Funkcja | Kontakt poza PCB |
|---|---|---|
| 1–2 | KEY TEST | X15 NO |
| 3–4 | L1 pętla sprzętowa | X12 NC_A |
| 5–6 | L1 diagnostyka | X12 NC_B |
| 7–8 | L2 pętla sprzętowa | X13 NC_A |
| 9–10 | L2 diagnostyka | X13 NC_B |
| 11–12 | STOP | X16 NC |
| 13–14 | ARM | X11 NO |
| 15–16 | MARK | X14 NO |
| 17–18 | TEST_PRESENT | X17 NO |
| 19–20 | rezerwa | NC;nie prowadzić żył |

Numery pinów X11…X17 w schemacie są umowne, funkcjonalne. Przed lutowaniem
odnaleźć pary rzeczywistych zacisków zakupionego elementu i wpisać ich oznaczenia
w formularzu odbioru. Dwa styki L1/L2 nie mają wspólnego COM. Nie łączyć toru
diagnostycznego z pętlą sprzętową.

W9 SCOPE:RG174100 mm,środek do J6.1,ekran J6.2. Izolowane gniazdo BNC
w metalowym panelu zapobiega nieplanowanemu dodatkowemu połączeniu masy.
Odbiornik oscyloskopu1 MΩ; terminacja50 Ω nadmiernie obciąża GPIO przez R12=330 Ω
w CORE. AUX BNC jest elementem P05, a nie dodatkowym wyjściem P11.

Wiązka TAPS należy do P05:50 mm maks.,5 par sygnał/GND do J7.
Wiązka ISERIES należy do P06:150 mm,2×2,5 mm²,MSTB4p do J1.
Panelowy BYPASS NKK S6A i jego przewody również należą do P06.

**Mechanika detekcji nie jest częścią obudów DT.** Zbudować trzy uchwyty na
osobnej listwie panelu. Popychacz L1/L2 ma nacisnąć oba NC przed dojściem do
styków DT; po wyjęciu kontaktów NC mogą wrócić. Ogranicznik przejmuje siłę
wsuwania i chroni przycisk przed przekroczeniem skoku. TEST NO naciskany dopiero
po całkowitym osadzeniu. Nie wykorzystać zatrzasku DT jako niezweryfikowanego
czujnika. Przymierzyć uchwyt do realnego wtyku i zarejestrować sekwencję elektryczną.
Odległości popychaczy celowo nie zamrożono bez wymiarów zakupionych gniazd
i obudowy; ich zmiana nie wpływa na pliki PCB.

Preferowana przesuwna osłona odsłania tylko jeden port. Przełączanie adapterów:
STOP,kluczyk poza TEST,brak ruchu,zamiana,potwierdzenie trybu,ponowne ARM.
Rozłączenie taśm wewnętrznych i MSTB tylko przy wyłączonym zasilaniu.
