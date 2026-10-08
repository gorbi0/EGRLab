# M1-R1 — niezależna notatka analog / PCB / CAM

Agent analog_pcb, 8.10.2026. Nie czytano wcześniejszego raportu Astra. Oryginał był tylko odczytywany. Wszystkie kopie, skrypty i wyniki są w `work-analog`. Przeczytano zakres oraz zatwierdzone AUDYT/SPECYFIKACJA; przyjętych uproszczeń nie kwalifikowano jako wad.

**Wniosek:** nie wykazano nowej pewnej usterki blokującej w zbadanych torach analogowych ani CAM. Poniższe ograniczenia i zalecenia nie są dodatkowymi potwierdzonymi usterkami PCB.

Baza ścieżek źródłowych: `C:/Users/tgorbacz/Documents/GORBI/Priv/Kia/Sportage/EGRLab/Plytki/M1-R1-do-recenzji/`.

- PCB: `Plytki/M1-R1-review/eda/M1.kicad_pcb`, SHA-256 `2b39a9ef6a1859437d935b1c7fb7464b49a346cf886a65b2d6c3c769a95a4c8b`.
- ZIP: `Plytki/M1-PCB-R1-zamowienie/DO-ZAMOWIENIA_M1-PCB-R1.zip`, SHA-256 `824058fb1497f3f717d213b366616b3687a044896e8437c0ed62d6853e908ac4`.

## A. PWM — ważne ograniczenie diagnostyki

Miejsce: `Plytki/M1-R1-review/src/parts.py:165–174`, `Rewizje/EGRLab-v6.3-m1/firmware/main/board.c:38,201,226` i `firmware/main/Kconfig.projbuild:15–38`.

Niezależne obliczenia filtrów (bez pasożytniczych pojemności):

| Tor | R Thevenina | Tau | Fc |
|---|---:|---:|---:|
| MOTOR, 300 kΩ / 100 kΩ / 220 pF | 73,892 kΩ | 16,256 µs | 9,790 kHz |
| SENSOR, 100 kΩ / 220 pF | 98,039 kΩ | 21,569 µs | 7,379 kHz |
| VSENSE, 499 kΩ / 100 kΩ / 220 pF | 81,940 kΩ | 18,027 µs | 8,829 kHz |
| CH6, 1 kΩ / 1 nF | 999,80 Ω | 0,9998 µs | 159,187 kHz |

Uwzględniono nominalne 5 MΩ wejścia ADC. AD7606B Rev.B, tablice 3/17: OS ×8 trwa 9,6–9,9 µs, z pasmem około 20 kHz przy ±10 V. Rejestr 0x08 = 0x03 uśrednia osiem szybkich próbek, nie całe 500 µs pomiędzy wyzwoleniami 2 kS/s. Domyślne PWM = 1 kHz daje tylko dwa punkty fazy na okres. Harmoniczne aliasują; LOGGER dodatkowo nie jest synchronizowany z ECU.

Surowe próbki pozostają prawidłowymi próbkami przebiegu po filtrze, lecz nie gwarantują poprawnego wyliczenia duty, RMS ani średniej PWM. Nie znaleziono tutaj algorytmu wyprowadzającego duty z próbek, któremu można przypisać błędny wynik; dlatego jest to ograniczenie, nie potwierdzona usterka.

**Kwalifikacja:** generator 0–12 V, np. duty 20%, okolice 1 kHz i inne częstotliwości PWM, kilka faz próbkowania; porównanie z oscyloskopem. Jeśli wymagane są metryki PWM, zastosować szybszą akwizycję i właściwą decymację albo osobny pomiar okresu/duty. Prąd trzeba ocenić osobno na zaworze, ponieważ jego indukcyjność może silnie zmniejszyć tętnienie.

## B. Drogi odsprzęgania — zalecenie layoutu i kwalifikacji

Finalne PCB odczytano przez pcbnew 10.0.6. Przeczytaną metodę `gndpath.py` skopiowano do katalogu pracy, zmniejszono krok do 0,1 mm i rozszerzono pary na ADC oraz stronę zasilania. Wyniki są przybliżonymi najkrótszymi drogami miedzi, nie impedancją HF; metryka rastrowa ma błąd kilku procent i nie dolicza pełnej długości baryłek przelotek.

| Para cap / V pin / GND pin | Droga V [mm] | Droga GND [mm] |
|---|---:|---:|
| C6 / U3.1 / U3.2 | 2,0 | 10,0 |
| C8 / U3.38 / U3.40 | 3,0 | 5,9 |
| C9 / U3.48 / U3.47 | 3,4 | 5,9 |
| C10 / U3.23 / U3.26 | 2,4 | 7,9 |
| C24 / U4.6 / U4.2 | 6,9 | 7,7 |
| C25 / U5.14 / U5.7 | 4,7 | 9,8 |
| C28 / U7.14 / U7.7 | 3,7 | 15,3 |

C24 → U4.6 przechodzi przez dwie przelotki i B.Cu. U3.37/38 mają wspólny lokalny C8. C7 opisany jako kondensator przy pinie 37 jest odległy około 24,7 mm drogą 5VA; nie oznacza to nieodsprzęgniętego pinu 37. C7 warto opisać jako dodatkową pojemność 5VA albo przenieść przy pin, jeśli celem jest oddzielne 100 nF dla każdego AVCC.

Karty ADC i INA zalecają lokalne kondensatory i krótkie drogi obu stron pętli. Pomiary geometrii nie dowodzą niestabilności. Przy następnej rewizji skrócić szczególnie pętle C6/U3.1 i C24/U4. Kwalifikacja: sonda ze sprężyną masową przy pinie podczas aktywnego ADC, Wi-Fi, SD i mostka.

Dowody: `geometry.json`, `paths.json`, `inspect_board.py`. Uwaga techniczna: pole `pad.layer` w JSON pochodzi z `GetLayer()` i nie służy do rozpoznawania strony odwróconych padów; właściwy pomiar używa `IsOnLayer()`.

## C. Zakres dowodu QA — zalecenie procesu

Miejsce: `src/board.py:51–64`, `src/return_check.py:17–21`, `src/verify_pcb.py:123–148`.

- `return_check` sprawdza sześć par C24–C29. C6–C15 przy ADC są świadomie wyłączone.
- Sprawdza drogę GND; pomija stronę zasilania i całą pętlę.
- Limit `1,3 × odległość prosta + 3 mm` rośnie po odsunięciu kondensatora. PASS nie oznacza bezwzględnie krótkiej pętli.
- Mutacje `verify_pcb` zmieniają gotowy snapshot lub flagę wyniku. Nie zmieniają geometrii PCB i nie powtarzają wydobycia cechy.

**Poprawka:** stałe limity krytycznych par, obie strony pętli, przelotki; próby negatywne przez zmianę kopii PCB i ponowny pomiar. Dotychczasowe mutacje dowodzą reakcji predykatu, nie całego toru kontroli. Sam brak tego testu nie jest usterką bieżącego PCB.

## D. Kelvin, prąd, footprinty i dokładność

Pinout INA240A2 zgodny z TI: 8 IN+, 1 IN−, 2 GND, 3 REF2, 4 NC, 5 OUT, 6 VS, 7 REF1. REF1 = VS i REF2 = GND jest poprawnym trybem dwukierunkowym. Nominalna skala wynosi 0,25 V/A. Rezystory R22/R23 = 10 Ω dodają około 0,33% błędu wzmocnienia (TI, tabela 9-1); należy uwzględnić go w kalibracji/budżecie, nie traktować jako samodzielnej usterki.

Zero zależy od VS/2. Zmiana VS o 50 mV po kalibracji daje około 0,10 A pozornego prądu. Jest to analiza wrażliwości, nie pomiar zakłóceń. Kwalifikacja powinna objąć zmianę obciążenia Wi-Fi/SD, temperatury i zasilania. Jeśli wymagania dokładności nie są spełnione, potrzebne będzie stabilniejsze odniesienie albo kompensacja VS.

Finalne długości: K_PLUS 8,960 mm na F.Cu, INA_PLUS 4,570 mm; K_MINUS 25,019 mm na F.Cu/In2.Cu przez dwie przelotki, INA_MINUS 3,570 mm. Sense i force są rozdzielone prawidłowo. In1 ekranuje elektrycznie odcinek In2 od F.Cu, ale nie dowodzi braku sprzężeń magnetycznych. Rzut pętli ma dwie części około 52,6 i 51,1 mm² o przeciwnych znakach; małe pole algebraiczne 1,49 mm² nie dowodzi małej podatności w niejednorodnym polu. Model pomocniczy łączy piny wewnątrz INA i bocznika prostymi odcinkami. Dowód: `kelvin-geometry.json`.

Kwalifikacja: skok napięcia wspólnego przy zerowym prądzie oraz PWM z niezależnym wzorcem prądu. Sam test DC nie bada tego ryzyka. CH1 ma 34,910 mm miedzi węzła wysokiej impedancji, CH2 31,807 mm; sprawdzić przesłuch i zgodność czasową, bez przypisywania pewnej usterki wyłącznie długości.

WSK25125L000FEA to 5 mΩ, 1%, 1 W. Wymiary footprintu force 2,29 mm, sense 1,70 mm i rozstaw odpowiadają zakresowi 5–200 mΩ w aktualnej karcie Vishay. Straty: 7,5 A → 0,281 W, 10 A → 0,5 W. Nie jest to kwalifikacja termiczna całego toru miedzi, oprawki i pól przewodów: ta pozostaje **NIE ZBADANO**.

W LOGGER bezpiecznik F1 nie znajduje się w linii ECU–bocznik–EGR. Argument dokumentacji „zakres ±9 A wystarcza, bo F1 ma 7,5 A” nie uzasadnia zakresu LOGGER; bezpiecznik też nie jest precyzyjnym ogranicznikiem amplitudy. Nie wykazano wymagania pomiaru powyżej 9 A, więc jest to korekta uzasadnienia i punkt kwalifikacji, nie nowa potwierdzona usterka.

## E. ADC — sprawdzenie mapy i biasu

Z kartą porównano piny zasilania i masy, VxGND, serial/software OS = 111, wewnętrzną referencję, zwarcie REFCAP 44/45, oddzielne REGCAP 36/39, DOUTA 24 i rezystor źródłowy 33 Ω. Nie znaleziono zamiany pinów ADC/INA. C14/C15 mają nominalnie 22 µF; efektywnej pojemności po DC biasie nie potwierdzano wykresem TDK.

Nominalne skale 4,06 / 1,02 / 6,0898 / 1,0002 uwzględniają 5 MΩ. Wejście ADC ma bias: `I ≈ (Vin − 2 V)/5 MΩ`. Stąd `Vsource = k × Vadc − 2 × Rtop/5 MΩ`: korekty −120 mV MOTOR, −40 mV SENSOR, −199,6 mV VBAT, −0,4 mV CH6. Główny audyt potwierdził obowiązkową kalibrację dwupunktową ośmiu kanałów i bramkę `vcalok`; dlatego nie zgłoszono błędu. Kalibracja usuwa ten offset. Model samych skal nie uzasadnia pomiaru bez kalibracji.

## F. Niezależne odtworzenie CAM

Na własnej kopii `eda-copy` wykonano eksport KiCad CLI 10.0.6: Gerbery dziewięciu warstw, precision 6, subtract-soldermask, disable-aperture-macros, check-zones; wiercenia Excellon mm/decimal/absolute, separate-th. Wyniki w `fresh-cam`.

- 11/11 plików ZIP dokładnie odpowiada bajtom katalogu `gerber`.
- Po pominięciu wyłącznie metadanych daty/wersji/projectID identyczne ze świeżym eksportem są obie maski, oba nadruki, obrys, In1, In2, PTH i NPTH.
- F.Cu/B.Cu mają 16/7 różniących się fragmentów wierzchołków. Porównanie wierzchołek–łamana w obu kierunkach: maksimum `1e−6 mm = 1 nm`. Zmiany obejmują zbędne współliniowe wierzchołki i zaokrąglenia; bez znaczenia produkcyjnego.
- Rzeczywista kolejność warstw i rozszerzenia zgadzają się ze specyfikacją: F.gtl, In1.g1, In2.g2, B.gbl.

Dowody: `compare_cam.py`, `cam-comparison.json`, `cam_geometric_diff.py`, `cam-geometric-diffs.json` oraz pliki `.diff`. W tym podaudytcie nie wykonano osobnego świeżego DRC/ERC; koordynuje je audyt główny. Zgodność CAM nie potwierdza parametrów zmontowanego sprzętu.

## Źródła pierwotne

- [AD7606B Rev.B](https://www.analog.com/media/en/technical-documentation/data-sheets/ad7606b.pdf): tablice 2, 3, 17; pinout, referencja, filtr i layout.
- [TI INA240 SBOS662C](https://www.ti.com/lit/ds/symlink/ina240.pdf): pinout, midpoint, tabela 9-1, Kelvin i odsprzęganie.
- [Vishay WSK2512, dokument 30108](https://www.vishay.com/docs/30108/wsk2512.pdf): parametry, footprint, sense/force.
- [TRACO TSR2](https://www.tracopower.com/products/tsr2.pdf): oficjalny wynik wyszukiwarki; pełne pobranie zwróciło 403. Margines zasilania prowadzi agent power_interfaces.

Pamięć użyta tylko dla zasad zachowania historii i oddzielenia CAD od prób sprzętowych: MEMORY.md:77–78,90–91; rollout `01a0c505-1ade-72a2-b534-fb8b3c702841`. Starsze wyniki nie zastępują bieżącego sprawdzenia.
