# Odbiór PCB-R3 - uzupełnienie procedury elektrycznej R3

Nie zmieniać progów i limitów z `reference/R3-docs/ODBIOR.md` oraz METROLOGIA.md.
Wszystkie wyniki sprzętowe są na tym etapie NIE ZBADANE.

1. Zapisać wersje PCB-R3, SCH-R3, montaż A1; wpisać zmierzone R8 i R27, typ D3.
2. TP1 = SOURCE, TP2 = GATE. Podstawowy dostęp od spodu. Mierzyć VGS różnicowo,
   bez łączenia SOURCE z uziemioną masą sondy. Użyć zatwierdzonej konfiguracji
   z METROLOGIA; nowe położenie pól nie zwalnia z oceny błędu pomiaru.
3. Obejrzeć i sprawdzić lutowanie C6.GATE przy lokalnie przesuniętej tylnej szynie
   VS. Sprawdzić katodę D4 po prawej na widoku z góry, skierowaną do SOURCE.
4. Przeprowadzić kalibrację OVP, histerezę i UVLO według R3. Montaż R8=221 kΩ
   nie zmienia przyjętych kryteriów; nie korygować dokumentacji do nieudanego pomiaru.
5. Dynamika: wyłączenie J3/zanik AUX do |VGS|<0,5 V <=80 us; OVP od J1>18,5 V
   do |VGS|<0,5 V <=100 us, w tym detektor/bufor <=20 us. Zachować także próby
   hotplug/OFF oraz SOA. Same krótkie ścieżki D4 nie dowodzą zaliczenia tych prób.
6. Termika: sprawdzić osobno odcinek BAT_FUSED 3 mm i jego końce, przewężenia,
   połączenia D2/Q1/LK1/J6 i luty PTH, przy kolejnych obciążeniach 0,1/1/3,5/5 A.
   Jako dodatkowe kryterium PCB przyjąć przyrost temperatury miedzi i lutów toru
   roboczego <=20 K względem otoczenia, bez wzrostu w stanie ustalonym. Stosować
   termoparę izolowaną elektrycznie; uwzględnić przewodzenie ciepła z D2/Q1.
   Kryteria temperatur Q1/D2 i wnętrza obudowy nadal obowiązują z R3.

Pomiar niepewny zapisać jako NIE ROZSTRZYGNIĘTO. Każda korekta po przymiarce lub
pomiarach wymaga ponownego świeżego odbioru plików, nie tylko odświeżenia PDF.
