# Weryfikacja pliku produkcyjnego JLCPCB (Confirm Production file) — M1-PCB-R1

*9.10.2026. Plik od JLCPCB: `DO-ZAMOWIENIA_M1-PCB-R1-z-pasta_Y21.zip` (sha256 02b11866…), zamówienie 13670462A_Y21, wyjście jlccam pro 3.5.2.*

Metoda: rastrowanie każdej warstwy JLC (`ok/*`) i naszej (`DO-ZAMOWIENIA_M1-PCB-R1-z-pasta.zip`) w 20 px/mm po wyrównaniu początku układu (JLC: lewy dolny róg, przesunięcie +80 mm w Y), porównanie z tolerancją 0,1 mm (kompensacja trawienia).

| Warstwa JLC | Nasza | Wynik |
|---|---|---|
| tl | F_Cu | zgodna (0 px poza tolerancją) |
| l2 | In1_Cu (GND) | zgodna; JLC usunęło niepodłączone pola otworów (NFP) — prześwity w płaszczyźnie zachowane |
| l3 | In2_Cu | zgodna; ścieżki i podłączone pola zachowane, niepodłączone pola usunięte (NFP) |
| bl | B_Cu | zgodna |
| ts / bs | F/B_Mask | zgodne; JLC dodało otwarcia nad 4 otworami M3 w narożach i pasek wzdłuż krawędzi |
| to / bo | F/B_Silkscreen | zgodne; brak dodanego numeru zamówienia |
| ko | Edge_Cuts | zgodny, 150 × 80 mm |
| drl | PTH + NPTH | 269 otworów, liczby na średnicę zgodne; przelotki 0,3 / 0,4 bez zmian, PTH +0,15 mm, NPTH +0,05 mm (naddatek na metalizację / narzędzie) |
| sk | — | zaślepianie przelotek: 149 (82 × 0,3 + 67 × 0,4) = wszystkie przelotki, żadne pole elementu |

Parametry z `YG/4te.json`: 4 warstwy, kolejność L1 F_Cu.gtl / L2 In1_Cu.g1 / L3 In2_Cu.g2 / L4 B_Cu.gbl, FR-4 1,6 mm, miedź 1 / 0,5 oz, maska zielona, opis biały, wykończenie ENIG (沉金), przelotki zaślepione farbą (过孔塞油), bez numeru klienta (不加客编), 15 × 8 cm. Stos (JLC04161H-7628) i szablon nie występują w tym pliku — sprawdzić w szczegółach zamówienia.
