# P00-R2 - PCB i mechanika

115 x 70 mm, FR4 1,6 mm, dwie warstwy miedzi po 35 µm. Cztery otwory NPTH 3,2 mm w odległości 5 mm od narożników, strefa bez miedzi Ø8 mm. Zachowane kolumny kanałów co 11 mm, ich złącza, przełączniki i LED.

R5 560 Ω dodano nad LED zasilania. R6 1 Ω leży poniżej sekcji regulatora; krótka ścieżka łączy go z minusem C6. Powrót do U2 stanowi wylewka GND. Gałąź C6 nie przenosi prądu DC obciążenia, tylko prąd ładowania i tętnień.

| Połączenie | Realizacja |
|---|---|
| J10-D1-U2 i odczepy kondensatorów | F.Cu, 1 mm |
| R5 i powrót C6 do R6 | F.Cu, 0,6 mm |
| Szyna 3V3 pod przełącznikami | B.Cu, 0,8 mm; doprowadzenie 0,6 mm |
| Powtarzalne kanały | F.Cu, 0,5 mm |
| Pozostałe połączenia | Router; zapisany wynik SES |
| Masa | Wylewki na obu warstwach, usuwanie niepołączonych wysp |

R5/R6 używają tego samego montażu DIN0207, raster 10,16 mm, co pozostałe rezystory. C6 pozostał D5 / P2. Wszystkie elementy lutowane ręcznie, bez potrzeby montażu SMD. Przełączniki przed montażem sprawdzić omomierzem. Piny 1 i 2 J1-J9 identyfikować z nadruku; widok od góry: lewy GND, prawy sygnał.

PDF montażowy pokazuje oznaczenia Fab niewidoczne na nadruku kolumn. Druk 100%, zmierzyć belkę 100 mm i obrys 115 x 70 mm. Przymiarka części oraz sprawdzenie miejsca na ewentualny radiator TO-220 pozostają fizycznym odbiorem. Modele 3D nie są dowodem dopasowania przełączników ani elementów bez modelu.
