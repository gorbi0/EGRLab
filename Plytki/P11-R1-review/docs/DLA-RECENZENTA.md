# Zakres i punkty recenzji P11-R1

To kolejny moduł po P10. Baseline v6.1-rc1 P11 zamieniono na samodzielny,
odtwarzalny projekt KiCad z rzeczywistą PCB. Architektura połączeń zachowana.

| Zmiana | Powód / dowód |
|---|---|
| Zasilanie styków nazwane PANEL_3V3 | P04-R2.1 ma R40=100 Ω; nie wolno traktować J5.1 jak nieobciążonej szyny3V3 |
| J11 zbiera18 przewodów kontaktów | Szeregowe połączenia NC i rozdzielenie obu torów są na PCB i w testowanej netliście |
| X2/X3/X8 oraz X11…X17 poza PCB | Dobór obudowy, przycisków i mechanizmu detekcji bez zmiany footprintów PCB |
| X16 pomocniczy NO całkowicie NC | Baseline zasilał nieużywany COM_NO; tu obie końcówki odizolowane |
| Cztery tory silnikowe3 mm/70 µm,bez przelotek | TEST i LOGGER oddzielne; szerokość i długość sprawdzane na końcowej miedzi |
| Każdy PTH ma własną kotwę | Odległość osi10,5–14,7 mm; J9 jednorządowy12 mm; keepout pod opaską |
| Konkretne J1 i J7 | Phoenix1755752 i Molex39-29-9129,z kołkami; nie zastępować wersją bez kołków |
| Ochrona odczepów pozostaje w AT/AL1/AL2 | P11 nie przenosi rezystorów z końca samochodowego za długi przewód |

Kontrole nie opierają się wyłącznie na tym samym generatorze. `verify_electrical.py`
porównuje wyeksportowaną netlistę z kopią baseline i pięcioma sąsiednimi płytkami.
Symulacja grafu zamyka fizyczne kontakty zgodnie ze stanami i sprawdza osiągalność
MECH_OK, TEST_KEY, LOGGER_CLEAR, STOP_NC_OUT i TEST_PRESENT dla64 kombinacji.
Dodatkowo przerywa wybrane żyły pętli. Testy mutacyjne celowo omijają NC,
łączą masę sensora z GND, mieszają TEST/ECU i zmieniają footprinty.

**Granica weryfikacji:** model zakłada zdrowe styki. Nie dowodzi, że mechanika
otworzy NC dostatecznie wcześnie, że styki nie zostaną sklejone ani że dwie
sekcje jednego przycisku są niezależnymi kanałami bezpieczeństwa. TEST_PRESENT
jest informacją CORE, nie dodatkowym fizycznym przekaźnikiem mocy.

Najważniejsze odbiory przed aktywnym TEST:

1. Mechanika L1/L2 otwiera oba NC zanim którykolwiek styk elektryczny DT zacznie
   przewodzić; potwierdzić powolnym i szybkim wsuwaniem oraz przy przekoszeniu.
   W czasie pierwszego kontaktu napięcie MOTOR_PERMIT/PWM_OUT musi już być niskie.
   Samo wskazanie miernika „NC otwarte” nie mierzy opóźnienia układu P04.
2. LOOP_OUT–MECH_OK zwierane dopiero przy końcu adaptera AT. Żadnej zwory na P11.
3. Nie dopuścić dwóch adapterów naraz. Wspólne TAPy wymieszają pomiary,
   a LOGGER_CLEAR nie rozróżnia L1 i L2. Preferowana przesłona jednego dostępnego
   portu; brak takiej mechaniki wymaga zdyscyplinowanej procedury wymiany przy STOP.
4. Zmierzyć SAFE_N przy minimalnym zasilaniu, nagrzaniu i pełnej obsadzie P03/P04/P08,
   później P07. Model rezystorów daje2,748 V przy3,18 V; dodatkowe5 µA pochłania
   prawie cały zapas do progu odbiorczego2,7 V. To nie jest gwarantowany limit
   upływności gotowego systemu. Wynik opisano w `OBLICZENIA.md`.
5. Przymierzyć J1/J7 do wydruku1:1; wszystkie przewody zweryfikować od numeru pinu
   PCB do numeru komory we wtyku. Rząd DTtail jest nietypowy:7–12 u góry,1–6 na dole.

Zamienniki kontaktów mogą być tańsze, ale muszą obejmować obciążenia STOP około
27 µA/3 V. Wybrany referencyjny STOP to zatrzaskowy przycisk funkcyjny low-level,
bez deklaracji certyfikowanego wyłącznika awaryjnego. Lamp nie zasilać z PANEL_3V3.

Przed zamówieniem PCB recenzent zapisuje PASS/FAIL i listę usterek w nowym pliku.
Nie poprawiać równolegle pakietu, którego dotyczą zapisane raporty i sumy kontrolne.
