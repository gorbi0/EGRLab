# P01 — ustawienia zamówienia

1. Wybierz wykonanie samych PCB i wgraj **DO-ZAMOWIENIA_P01-PCB-R3.1.zip**.
2. Sprawdź rozpoznanie dwóch warstw i ustaw poniższe parametry.
3. Porównaj podgląd producenta z `podglad/CAM-top.png` i `CAM-bottom.png`.
4. Wybierz liczbę sztuk. Archiwum zawiera **jeden projekt jednej płytki**, bez panelizacji.

| Pole formularza | Wartość |
|---|---|
| Base material | FR4 |
| Layers | 2 |
| Size | **160 × 120 mm** |
| PCB thickness | **1.6 mm** |
| Outer copper weight | **1 oz**, nominalnie **35 µm na obu stronach** |
| Surface finish | Lead-free HASL |
| Solder mask | Green, both sides |
| Silkscreen | White, both sides |
| Electrical test | Yes / flying probe |
| Delivery format | Single boards |
| Controlled impedance | No |
| Edge plating / gold fingers / castellations | No |
| Via filling / resin plugging | No |
| PCB assembly / stencil | No |

**Zmiana 28.09.2026: miedź 35 µm zamiast 70 µm** (decyzja użytkownika, koszt 70 µm ok. 4×). Uzasadnienie: przy 5 A najwęższe odcinki toru mocy (2 mm) grzeją się wg IPC-2221 o ok. 17 °C zamiast 5 °C, a sam rejestrator bez P07 pobiera poniżej 1 A. Warunek: przed pierwszym uruchomieniem P07 próba nagrzewania toru mocy przy 0,1 / 1 / 3,5 / 5 A (ODBIOR R3). Pliki CAM bez zmian — grubość miedzi to tylko parametr zamówienia. Dokumenty w `projekt/` opisują pierwotne założenie 70 µm.

Przelotki są przykryte maską zgodnie z plikami; nie zamawiać
kosztownego wypełniania. Otwory PTH mają średnice docelowe po metalizacji;
dobór większego wiertła technologicznego należy do producenta.

Obrys to linia środkowa prostokąta 160 × 120 mm. Niektóre przeglądarki podają
**160,05 × 120,05 mm**, doliczając grubość linii obrysu 0,05 mm. Nie skalować
projektu: w zamówieniu wpisać 160 × 120 mm. Obrys tylko w `P01-Edge_Cuts.gm1`.

## Zawartość archiwum

| Plik | Rola |
|---|---|
| P01-F_Cu.gtl | miedź górna |
| P01-B_Cu.gbl | miedź dolna |
| P01-F_Mask.gts | otwarcia maski górnej |
| P01-B_Mask.gbs | otwarcia maski dolnej |
| P01-F_Silkscreen.gto | nadruk górny |
| P01-B_Silkscreen.gbo | nadruk dolny |
| P01-Edge_Cuts.gm1 | obrys cięcia |
| P01-PTH.drl | 202 otwory metalizowane, w tym 3 przelotki |
| P01-NPTH.drl | 8 otworów niemetalizowanych |

Średnica 3,2 mm występuje zarówno w PTH, jak i NPTH; nie łączyć plików według
samej średnicy. Otwory Ø2,8 mm pod kołki radiatorów pozostają metalizowane.
Nie wykonywać dodatkowego odbicia lustrzanego warstwy dolnej ani wierceń.
Wszystkie pliki mają wspólny początek współrzędnych i jednostki mm.

Najwęższy odcinek ścieżki ma 0,40 mm. Minimalny odstęp dopuszczony regułami
projektu wynosi 0,25 mm; odstęp miedź–krawędź co najmniej 0,50 mm.
Najmniejszy otwór to 0,60 mm. Wymagane parametry nie obejmują mikroprzelotek
ani otworów ślepych. Zmiany CAM naruszające połączenia, wielkość pól, położenie
otworów lub obrys wymagają ponownej oceny; nie akceptować automatycznego skalowania.

Przed wysłaniem zlecenia pozostaje praktyczne sprawdzenie kupionych radiatorów,
Q1/D2 z izolacją, C6 i złącza J6 na wydruku 1:1. W przekazanych materiałach
brak potwierdzenia takiej przymiarki. Sama zgodność Gerberów z CAD tego nie zastępuje.

## Odbiór dostarczonych PCB

Sprawdzić wymiary, otwory i metalizację; obejrzeć maskę i lutowalność pól,
szczególnie Q1/D2, J7, LK1 i J5. Sprawdzić brak zwarć, a po montażu izolację
tabów Q1/D2 od radiatorów. Dalszy odbiór zgodnie z procedurami R3.1 w `projekt`.
