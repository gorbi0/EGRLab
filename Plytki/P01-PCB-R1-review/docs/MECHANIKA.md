# P01-PCB-R1 - przymiarka przed eksportem produkcyjnym

Stan wszystkich pozycji poniżej: **NIE ZBADANO NA RZECZYWISTYCH CZĘŚCIACH**.
Wydruk 1:1 jest w PDF, strona 2. Drukować w 100%, bez "dopasuj do strony".
Zmierz belkę kontrolną 100 mm i oba wymiary płytki: 160 × 120 mm.

| Kontrola | Kryterium | Wynik / uwagi |
|---|---|---|
| Obudowa | PCB 160×120, otwory (5;5), (155;5), (5;115), (155;115), Ø3,2 | NIE ZBADANO |
| HS1/HS2 | Fischer SK129-63STS; kołki P25,4 pasują do Ø2,8; profil 42×25 | NIE ZBADANO |
| Wysokość | 63,5 mm radiatora + prześwit, PCB, dystanse i pokrywa | NIE ZBADANO |
| D2 i Q1 | A-K-A / G-D-S; raster2,54, Ø1,4; tab dochodzi do radiatora bez naprężenia nóżek | NIE ZBADANO |
| Izolacja | Podkładka i tulejka M3; oba radiatory odizolowane od tabów i sieci PCB | NIE ZBADANO |
| Dostęp do śruby | Śruba M3x10 i narzędzie mieszczą się; długość śruby dobrana do faktycznego zestawu | NIE ZBADANO |
| C6 | WIMA MKS2D041001K00JO00, P5, korpus7,2×7,2, H13 | NIE ZBADANO |
| J6 | Phoenix1757255 +1757022; dostęp do wtyku i wkrętaka od prawej krawędzi | NIE ZBADANO |
| H_BAT | Dwie linki2,5mm², Ø3,2 PTH, opaska3,6mm; kotwa12,5mm od lutu | NIE ZBADANO |
| H_PG | SześćAWG22, Ø1,1 PTH; opaska2,5mm; kotwa12,5mm od lutu | NIE ZBADANO |
| LK1 | Cu2,5mm² między dużymi padami P10/Ø2,4; dostęp do odlutowania i osobnych pól sense | NIE ZBADANO |
| TP1/TP2 | Dostęp do SOURCE/GATE także po przykręceniu radiatora, bez dotykania tabów | NIE ZBADANO |
| Rezystory | MFR-50/H4 P15,24; PR02 P17,78; R1/R23 uniesione ok.3mm | NIE ZBADANO |

## Wiązki i orientacja

J7 przy (15;25) mm: pad1 po lewej BAT_FUSED, pad2 po prawej GND. Wiązka wychodzi
w górę do kotew Y=12,5 mm. Gotowe 200 mm; przy źródle bezpiecznik i część żeńska,
zgodnie z R3. H_PG na J5 wychodzi w lewo do kotew X=130,5 mm. Nie kłaść żył nad
rezystorami ani nie napinać ich między lutem i opaską.

J5: pad1 jest na dole (Y112), pad6 u góry (Y99,3). Od dołu: 3V3_IO, SAFE_N,
GND, PG_SEND, PG_LINK, GND. Numeracja komór Mini-Fit jest ważniejsza niż kolory.

J6: od dołu pad1 VPROT (Y32), pad2 GND (Y26,92), pad3 NC (Y21,84). Pin3 zostaje
niepodłączony. J1/J2/J4/J8 są polami pomiarowymi, nie dodatkowymi złączami.

Nie zmieniono długości wiązek R3: H_BAT 200 mm, H_PG 200 mm. Zwiększenie PCB
nie jest podstawą do samowolnej zmiany pinoutu lub kierunku wtyków.

## Kolejność montażu

1. Sprawdzić gołą PCB, ciągłość sieci i izolację DRAIN-VPROT przy braku LK1.
2. Wlutować drobne THT, podstawkę/układ U2, zworki i elementy bierne; sprawdzić polaryzację.
3. Złożyć mechanicznie Q1/D2 z radiatorami i izolacją przed ostatecznym lutowaniem
   ich nóżek; nie przenosić siły dokręcania przez złącza lutowane.
4. Wlutować pozostałe duże elementy, J6, wiązki i LK1 według schematu odbioru.
5. Zamocować opaski na izolacji przewodów; sprawdzić każdą żyłę i izolację radiatorów.
6. Uruchomić samą P01 z ograniczeniem prądu według ODBIOR R3. Nie zaczynać od auta.

Data przymiarki: __________  Wykonawca: __________  Uwagi: __________

Po zmianie footprintu, pozycji lub wymiaru: ponowny DRC, kontrola delty oraz nowy
wydruk. Eksport Gerber/Excellon dopiero po uzupełnieniu powyższych wyników.
