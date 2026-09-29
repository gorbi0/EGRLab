# Mechanika i montaż

Obrys 160 × 120 mm, FR4 1,6 mm, dwie warstwy Cu 35 µm. Otwory M3 NPTH 3,2 mm: (5,5), (155,5), (5,115), (155,115), (155,38) mm. Miedź odsunięta od otworów; bez elementów pod łbem/podkładką. Pozycje M1, SD1 i wszystkich złączy zachowane z R1.

M1 stoi na dwóch listwach żeńskich 1×22, raster 2,54 mm, rozstaw rzędów 22,86 mm zmierzony przez użytkownika. Usunąć/odłączyć RGB obciążające GPIO38 zgodnie z kontraktem v6.1. USB przy górnej krawędzi. Strefa anteny bez miedzi po obu stronach (+3 mm na boki, +8 mm za modułem) jest kompromisem prototypu; nie stanowi kwalifikacji RF.

U3 pozostaje na posiadanym PA0085. Sprawdzić ciągłość numerów 1–6 adaptera i dołożyć lokalne odsprzęganie na samym adapterze, jeżeli pętla przy scalaku okaże się zbyt długa. C3 na CORE leży teraz przy rzeczywistym VDD=6, a nie MR=3. U11–U14/U21–U23 na adapterach Kamami 575068; uwzględnić wysokość modułów i sąsiednich elementów.

U4, U5, U6 i Q1 lutować bezpośrednio na PCB: SOT23-5, TSOT23-6, SOT23-5, SOT23; C12–C15 i R41 1206. U6, C15 i R41 (R4) stoją tuż przy obudowie J4 i adapterze U12: lutować je przed J4 i przed listwami adaptera U12. Poza R41 (SMD 1206) rezystory to THT DIN0207, raster 10,16 mm. Wiązka LV03 lutowana do metalizowanych otworów J10; kotwa opaski 12,5 mm od lutu. Po lutowaniu oczyścić okolice sygnałów i SMD.

J1 to gniazdo 2×8 kątowe przy prawej krawędzi, P05 stoi obok, z wtykiem kątowym przy lewej. Kandydat z R1: SSW-108-02-G-D-RA / TSW-108-08-G-D-NA. Pozycja 2 niepołączona i mechanicznie zablokowana. Genericzny footprint nie potwierdza wysokości osi rzędów ani głębokości zazębienia konkretnej pary. **Przed zamówieniem P03/P05 zatwierdzić wspólny przekrój mechaniczny i przymiarkę części.** H2/H5 podpierają złącze; nie wciskać modułów bez dystansów.

Złącza IDC J2–J8: odciąć wskazany pin KEY i zaślepić otwór we wtyku. Długie osie przy krawędzi, rząd sygnałowy do środka. Wtyki i czoła oznaczyć nazwą połączenia, a nie samym Jn.
