# P00-R3 — PCB i mechanika

Płytka 115 × 70 mm, FR4 1,6 mm, dwie warstwy miedzi po 35 µm. Cztery otwory NPTH 3,2 mm leżą 5 mm od narożników, każdy ze strefą bez miedzi Ø8 mm. Kolumny kanałów stoją co 11 mm, ze złączami, przełącznikami i LED. **Miedź i rozmieszczenie są identyczne z R2** (`verification/revision-checks.json`).

R5 560 Ω leży nad LED zasilania. R6 1 Ω jest poniżej sekcji regulatora, krótką ścieżką połączony z minusem C6. Powrót do U2 prowadzi wylewka GND. Gałąź C6 nie przenosi prądu DC obciążenia, tylko prąd ładowania i tętnień.

| Połączenie | Realizacja |
|---|---|
| J10-D1-U2 i odczepy kondensatorów | F.Cu, 1 mm |
| R5 i powrót C6 do R6 | F.Cu, 0,6 mm |
| Szyna 3V3 pod przełącznikami | B.Cu, 0,8 mm; doprowadzenie 0,6 mm |
| Powtarzalne kanały | F.Cu, 0,5 mm |
| Pozostałe połączenia | Router; zapisany wynik SES |
| Masa | Wylewki na obu warstwach, niepołączone wyspy usuwane |

**Nadruk R3.** Napis „+VIN 6-15V” stoi pod J10; najbliższym polem jest J10.1. Pole TP3 ma napis „ZA D1”, bo leży za diodą i służy tylko do pomiaru. W R2 napis +VIN stał 2 mm od TP3. Pozostałe napisy i oznaczenia bez zmian, do tego linia tytułowa „PCB R3”.

**Tab U2.** Tab TO-220 jest zwrócony do C5/C7, ok. 1,5 mm od ich obrysu. Radiator nasuwany na tab wymagałby przymiarki. Obliczenie go nie wymaga, a planem B dla temperatury jest zasilanie 12 V (`ZALOZENIA-P00-R2.md`).

R5 i R6 mają ten sam footprint DIN0207 z rastrem 10,16 mm co pozostałe rezystory. C6 ma D5 / P2. Wszystko lutuje się ręcznie, bez SMD. Przełączniki przed montażem sprawdzić omomierzem. Piny 1 i 2 J1–J9 odczytywać z nadruku; w widoku od góry lewy to GND, prawy to sygnał.

PDF montażowy pokazuje oznaczenia z warstwy Fab, niewidoczne na nadruku kolumn. Drukować w skali 100 %, zmierzyć belkę 100 mm i obrys 115 × 70 mm. Przymiarka części pozostaje fizycznym odbiorem. Modele 3D nie dowodzą dopasowania przełączników ani elementów bez modelu.
