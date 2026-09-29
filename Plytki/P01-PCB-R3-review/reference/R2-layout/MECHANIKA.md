# P01-PCB-R2 - przymiarka przed eksportem produkcyjnym

Stan wszystkich pozycji poniżej: **NIE ZBADANO NA RZECZYWISTYCH CZĘŚCIACH**.
Wydruk 1:1 jest w PDF, strona 2 (montaż). Drukować w 100%, bez "dopasuj do strony".
Zmierz belkę kontrolną 100 mm i oba wymiary płytki: 160 × 120 mm.

Względem R1 zmieniło się położenie C6, TP1/TP2, J5 i większości drobnych elementów.
Obrys, otwory M3, radiatory, D2/Q1, J7, D1, J1, LK1, J6, D3, C3 i C4 stoją jak w R1.

| Kontrola | Kryterium | Wynik / uwagi |
|---|---|---|
| Obudowa | PCB 160×120, otwory (5;5), (155;5), (5;115), (155;115), Ø3,2 | NIE ZBADANO |
| HS1/HS2 | Fischer SK129-63STS; kołki P25,4 pasują do Ø2,8; profil 42×25 | NIE ZBADANO |
| Wysokość | 63,5 mm radiatora + prześwit, PCB, dystanse i pokrywa | NIE ZBADANO |
| D2 i Q1 | A-K-A / G-D-S; raster 2,54, Ø1,4; tab dochodzi do radiatora bez naprężenia nóżek; gruba linia nadruku = strona taba | NIE ZBADANO |
| Q2 | TO-220 bez radiatora; metalowy tył po stronie grubej linii i napisu `TAB`, czyli w górę, do szyny VS | NIE ZBADANO |
| Izolacja | Podkładka i tulejka M3; oba radiatory odizolowane od tabów i sieci PCB | NIE ZBADANO |
| Dostęp do śruby | Śruba M3x10 i narzędzie mieszczą się; długość śruby dobrana do faktycznego zestawu | NIE ZBADANO |
| C6 (R2: we wnęce HS2) | WIMA MKS2D041001K00JO00, P5, korpus 7,2×7,2, H13. Korpus 2,75 mm od czoła Q1; szerokość wnęki między ściankami ok. 17 mm | NIE ZBADANO |
| TP1/TP2 (R2) | Pady 2 mm w kieszeniach wnęki HS2: ok. 1 mm od czoła Q1, 1,25/1,45 mm od korpusu C6, 1,6/1,4 mm od ścianek radiatora. Dojście sondy z góry po montażu; jeśli się nie da, pady są PTH (Ø1 mm) i dostępne od spodu, albo wlutować pętelki | NIE ZBADANO |
| J6 | Phoenix 1757255; wtyk 1757022 należy do przewodu P02 (WIAZKI R3); dostęp do wtyku i wkrętaka od prawej krawędzi | NIE ZBADANO |
| H_BAT | Dwie linki 2,5 mm², Ø3,2 PTH, opaska 3,6 mm; kotwa 12,5 mm od lutu | NIE ZBADANO |
| H_PG (R2) | Sześć AWG22, Ø1,1 PTH; opaska 2,5 mm przez otwory Ø3,2 w (128,8; 113,5) i (147,5; 113,5); kotwa 12,5 mm od lutu | NIE ZBADANO |
| LK1 | Cu 2,5 mm² między dużymi padami P10/Ø2,4; dostęp do odlutowania i osobnych pól sense | NIE ZBADANO |
| Rezystory | MFR-50/H4 P15,24 (zamówione MF0207/MF0204/YR1B, patrz `ZAKUPIONE-CZESCI.md`); PR02 P17,78; R1/R23 uniesione ok. 3 mm | NIE ZBADANO |

## Wiązki i orientacja

J7 przy (15;25) mm: pad1 po lewej BAT_FUSED, pad2 po prawej GND. Wiązka wychodzi
w górę do kotew Y=12,5 mm. Gotowe 200 mm; przy źródle bezpiecznik i część żeńska,
zgodnie z R3. Bez zmian od R1.

**J5 (R2):** pady w poziomym rzędzie na Y=101. Pad1 jest po prawej (X=144,5), pad6
po lewej (X=131,8); numery 1–6 są na nadruku pod padami. Od prawej: 3V3_IO, SAFE_N,
GND, PG_SEND, PG_LINK, GND. Przewody schodzą w dół do opaski na Y=113,5 i dalej do
dolnej krawędzi (Y=120). W pasie między padami a opaską nie ma elementów. Nie kłaść
żył nad rezystorami ani nie napinać ich między lutem i opaską. Numeracja komór
Mini-Fit jest ważniejsza niż kolory.

J6: od dołu pad1 VPROT (Y32), pad2 GND (Y26,92), pad3 NC (Y21,84). Pin3 zostaje
niepodłączony. J1/J2/J4/J8 są polami pomiarowymi, nie dodatkowymi złączami; w R2
mają nazwy sieci na nadruku (J8: S = PG_SEND, L = PG_LINK).

Nie zmieniono długości wiązek R3: H_BAT 200 mm, H_PG 200 mm. Zmiana kierunku wyjścia
J5 nie zmienia pinoutu ani kolejności komór.

## Kolejność montażu

1. Sprawdzić gołą PCB, ciągłość sieci i izolację DRAIN-VPROT przy braku LK1.
2. Wlutować drobne THT, podstawkę/układ U2, zworki i elementy bierne; sprawdzić polaryzację.
   **C6 wlutować w tym kroku, przed Q1/HS2** — po złożeniu wnęka jest ciasna. Jeśli
   przymiarka pokaże, że sonda nie dojdzie do TP1/TP2 z góry, pętelki też teraz.
3. Q2 wlutować metalowym tyłem w stronę grubej linii nadruku (`TAB`).
4. Złożyć mechanicznie Q1/D2 z radiatorami i izolacją przed ostatecznym lutowaniem
   ich nóżek; nie przenosić siły dokręcania przez złącza lutowane.
5. Wlutować pozostałe duże elementy, J6, wiązki i LK1 według schematu odbioru.
6. Zamocować opaski na izolacji przewodów; sprawdzić każdą żyłę i izolację radiatorów.
7. Uruchomić samą P01 z ograniczeniem prądu według ODBIOR R3. Nie zaczynać od auta.

Data przymiarki: __________  Wykonawca: __________  Uwagi: __________

Po zmianie footprintu, pozycji lub wymiaru: ponowny DRC, kontrola delty oraz nowy
wydruk. Eksport Gerber/Excellon dopiero po uzupełnieniu powyższych wyników.
