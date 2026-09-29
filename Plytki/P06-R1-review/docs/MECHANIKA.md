# PCB, montaż i przymiarka

120 × 100 mm, FR4 1,6 mm, 2 × 70 µm Cu, HASL bezołowiowy. Odstęp elektryczny co najmniej 0,25 mm, zwykła ścieżka co najmniej 0,30 mm, przelotki 0,8/0,4 mm. Cztery otwory M3 3,2 mm: (5,5), (115,5), (5,95), (115,95). Pod opaskami i podkładkami M3 obowiązują obszary bez ścieżek i wylewek.

Elementy na górze. U1 SOIC8 i U5/U6 SO14 mają raster 1,27 mm, bez pól ukrytych pod obudową. Można je lutować grotem z topnikiem. Kondensatory odsprzęgające 0805; U2/U3 DIP8, U7 DIP14, U4/U8/U9/U10 TO92; rezystory osiowe i duże kondensatory przewlekane. Podstawki pod DIP są opcją serwisową, nie częścią krytycznego toru Kelvina. Nie stosować podstawki/adaptera pod INA240 w tej rewizji PCB.

PBV stoi pionowo. Korpus 22,5 × 4,45 mm w rzucie, wysokość od PCB zależy od uformowania wyprowadzeń; zarezerwować co najmniej 25 mm pod pokrywą i sprawdzić rzeczywistą część. Raster pinów patrząc na stronę znakowania: 5,08 / 7,62 / 5,08 mm. Numery nadane w bibliotece 1-4 od lewej; zewnętrzne są I, wewnętrzne U. Drille 2,3 mm dla prądowych i 2,0 mm dla pomiarowych uwzględniają przekątną maksymalnego prostokątnego przekroju wyprowadzenia z rysunku producenta. Sprawdzić również pobielenie i luz rzeczywistego egzemplarza. Nie pomylić numeracji umownej z nadrukiem producenta.

S6A na panelu: otwór nominalny 12,5 mm, gwint M12×1, panel do 4 mm według katalogu; zastosować element przeciwobrotowy. Rezerwacja za panelem: co najmniej 40 × 35 × 45 mm wraz z lutami i łukiem przewodów, do przymiarki. SW1.1 pozostaje niepodłączony i zaizolowany. Opisy BYPASS/MEASURE nanieść dopiero po sprawdzeniu omomierzem faktycznych styków 2-3/5-6 oraz 2-1/5-4. Położenia dźwigni nie ustalać „na oko” ze zdjęcia.

R21 2 W odsunąć od laminatu o 3-5 mm. Jest daleko od U10 i RSH1. Nie prowadzić nad nim taśmy ani opaski. Rezystory zwykłe mają obrys DIN0207 / P10,16; R6 DIN0411 / P15,24; R21 DIN0617 / P25,4. Większy footprint D2 DO35 mieści mniejszy korpus BAT85 DO34 - uformować nóżki do P7,62, nie dociągać szkła naprężeniem. Kondensatory elektrolityczne: C3 D8/P3,5; C4/C5 D5/P2. D1/D2 pasek = katoda = pad 1.

Na rysunkach miedzi obie strony oglądamy z góry przez laminat. B.Cu nie jest gotowym lustrzanym szablonem trawienia. PDF montażowy drukować bez skalowania; sprawdzić belkę 100 mm. Wszystkie opisy referencji znajdują się na PCB; część opisów R/U jest pod korpusem i służy przed lutowaniem. Wiązki mogą po montażu zasłonić małe numery padów - zachować dokumentację i oznaczyć same przewody.

M01 przed Gerberami: przymierzyć PBV, TO92, kondensatory, rezystory mocy, przewód 2,5 mm² w otworze 2,4 mm, wtyki i opaski. Zmierzyć wysokość pod pokrywą. Zaznaczyć wynik w ODBIOR.md; rysunek 1:1 nie zastępuje przymiarki części.
