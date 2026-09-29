> Historia poprzedniego wydania. Korekta R17 i aktualny status: ZMIANY-R2.2.md, README.md.

# P04 — zamknięcie recenzji projektu

26.09.2026 · Codex. Oceniona baza: P04-R2-review. Wydanie po recenzji: **P04-R2.1-review**, rewizja elektryczna i PCB nadal **R2**.

**Werdykt: projekt schematu i PCB zamknięty do wykonania prototypu. Nie stwierdziłem błędu wymagającego zmiany połączeń, elementów lub prowadzenia ścieżek.** Nie zalecam kolejnej rundy przeprojektowania przez model. Następny etap to przymiarka rzeczywistych części i wykonanie jednej serii prototypowej, potem odbiór na stole.

Ta decyzja nie oznacza zaliczenia przymiarki ani pomiarów sprzętu. Przed wysłaniem plików do fabryki pozostaje M01 z `ODBIOR.md`; przed integracją E01–E22. Gerberów w tej paczce nie ma. P07 pozostaje HOLD do zbadania modułu BTS7960.

## Co rzeczywiście sprawdzono

| Obszar | Wynik i dowód |
|---|---|
| Nienaruszona baza recenzji | 123/123 pliki manifestu R2 zgodne; `audit/source-manifest-check.json` |
| Schemat | Świeży ERC: 0. 98 części, 355 przypisań pinów, 92 sieci; netlista zgodna ze specyfikacją generatora |
| PCB | Świeży natywny DRC wszystkich poziomów z kontrolą schematu: 0 naruszeń, 0 braków połączeń, 0 różnic schemat–PCB |
| Kontrole niezależne od obrazka | 26/26 PCB, 22/22 logiki, dodatkowe 11/11 wartości/BOM/interfejsów/obliczeń |
| Skuteczność kontroli | Wykryte 11/11 celowych błędów PCB, 14/14 połączeń i 24/24 zmian wartości/MPN |
| Funkcje | 131 072 kombinacje logiczne; sekwencje ARM/reset/powrót READY; wyłączenie przez watchdog także przy przerwanym Q1 |
| Wartości | R1/C1 watchdoga, R2/R3/C2 ARM, R4/R5/C18 SAFE, wszystkie rezystory polaryzacji i ograniczające prąd, kondensatory, dokładny wariant U11; niezależnie od `parts.py` |
| Sąsiednie płytki | Eksporty P01 PCB-R3.1, P02-R2, P03-R2 i P05-R1: zgodność wszystkich 34 pozycji łączy PG/PSUOK/SAFE/DAQOK. HOLD_READY z P02 na pinie 3 pozostaje na P04 celowo NC |
| Masa | 249 elementów grafu miedzi GND tworzy jedną połączoną grupę; dodatkowo DRC 0. Nie jest to pomiar impedancji ani test EMI |
| Odtworzenie | Nowy katalog, ponowna generacja schematu i PCB ze źródeł, odtworzenie SES i tras uzupełniających, ERC/DRC oraz kontrole. Odcisk geometrii zgodny z R2 |
| Oględziny | Obejrzano 6 stron schematu i 4 strony dokumentacji PCB po rasteryzacji PDF. Numeracja, nadruki, kotwy, RC, trasy i wylewki bez wykrytej kolizji wymagającej zmiany layoutu |

Wyniki znajdują się w `verification/`. Kontrola wartości oraz zgodności z sąsiadami: `value-checks.json`; niezależne odtworzenie: `independent-rebuild.json`; graf masy: `ground-islands.json`. Skróty kontrolne finalnych plików i ZIP są w manifeście wydania.

## Poprawki w R2.1

1. **Poprawiono opis progu resetu.** MCP100-300 jest właściwym kierunkiem zmiany. Histereza 50 mV jest jednak typowa, bez gwarantowanego maksimum. Oszacowany zapas wynosi 130 mV przy 3,18 V DC albo 110 mV przy dolinie 3,16 V, przy założeniu tej typowej histerezy. Wcześniejsze „+135 mV” było nieprawidłowe. Skorygowano `PROJEKT.md`, historię zmian oraz uwagę U11 w generatorze i BOM. Sam U11 i PCB bez zmian. Źródło: [Microchip DS11187F, tabela 1-1](https://ww1.microchip.com/downloads/en/DeviceDoc/11187f.pdf).
2. **Usunięto zapewnienie o łagodnych skutkach zwarcia wyjść HC.** Zwarcie wyjścia push-pull może uszkodzić bramkę i zakłócić zasilanie. E22 dotyczy tylko wyjść przez R38/R39/R40; SAFE_N wolno zwierać do GND jako przewidziany sygnał wyłączenia. Wyjść MOTOR/PWM/ARM_CLK/HW_ARMED/INTERLOCK/SENSOR nie zwierać. Rezystory szeregowe pozostają opcją przy integracji odbiorników, nie zamkniętym wymaganiem tej płytki. Źródła: [TI HC08](https://www.ti.com/lit/ds/symlink/sn74hc08.pdf), [TI HC74](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf), wartości absolute maximum nie są parametrami ochrony zwarciowej.
3. **Dołożono niezależne testy wartości i ich negatywne próby.** R2 kontrolowała połączenie C1, lecz mogła nie wykryć dziesięciokrotnej zmiany jego wartości. Teraz zmiana 1 µF → 100 nF lub zamiana folii na niekwalifikowany X7R jest odrzucana. Dodano też kontrolę spójności wartości i MPN między XML a BOM oraz rzeczywistych map sąsiednich modułów.
4. **Domknięto dokumentację złączy.** Pozyskano kartę Würth 10p i porównano rysunki z CAD. W Molex potwierdzono również rozstaw rzędów ogonków i kołki, a nie tylko nazwę rodziny. Wyniki w `MECHANIKA.md`, źródła poniżej.
5. Formularz odbioru obejmuje teraz jawnie **E01–E22**, także próbę drugiej drogi watchdoga i ograniczenia prądu; poprzednie zakończenie tekstu pomijało E21/E22.

Wszystkie pliki `eda/` używane do projektu oraz oba PDF są identyczne bajtowo z R2 (porównanie z pominięciem lokalnego `.kicad_prl` i plików blokad). PDF zachowują tytuł R2 i dawny opis statusu „do recenzji”; aktualny status określa ten dokument. Nie ma dwóch różnych wersji miedzi.

## Ocena zmian Opusa R4-01…R4-07

Zmiany przyjęte: niższy próg U11, bezpośrednia druga droga WD_Q, R38/R39/R40 na wyjściach zasilających wiązki, filtr C18/R5 przy wejściu SAFE, czytelne KEY, zszycie masy i R41/R42 przy panelu. Nie znalazłem powodu do ich cofania. Druga droga watchdoga rzeczywiście dochodzi do CLR U3 oraz obu torów zezwolenia, co potwierdza model oparty na pinach eksportowanej netlisty.

R40 = 100 Ω / 0,25 W wystarcza do założonego panelu stykowego. Zwarcie przy 3,465 V i −1% rezystancji daje ok. 35 mA i 0,121 W. Pełne narożniki tolerancji rezystorów opisano w `value-checks.json`. Panel nie może z tej linii zasilać dodatkowych LED ani elektroniki bez ponownego obliczenia poziomów.

## Co pozostaje fizycznym odbiorem

- **Przed fabryką:** wydruk 100%, belka kontrolna 100 mm; przyłożyć zakupione J3–J8, adaptery 575068 i podstawki. Sprawdzić kierunek pinów, kołki, obszar zatrzasków przy rezystorach oraz dostęp do punktów pomiarowych. Złącze o innym MPN wymaga własnego porównania wymiarów. To jedna przymiarka operatora, nie kolejna runda modelowej recenzji.
- **Po montażu:** z P00, bez samochodu i silnika, wykonać E01–E22. Szczególnie czas watchdoga 50–150 ms przy rzeczywistym 3,3 V, STOP, ARM trzymany podczas startu i błędu, poziom SAFE_N, reset przy dolnym napięciu, Ioff i druga droga wyłączenia z Q1 zablokowanym. Nie wpisano wyników pomiarów jako PASS.
- **Przy integracji:** sprawdzić SAFE_N pod obciążeniem P01/P07, firmware heartbeat związany ze świeżymi próbkami, P08 SENSOR6 i domyślne stany P07. P03 R14 = 0 Ω pozostaje osobną uwagą integracyjną: zmiana na 1 kΩ ograniczyłaby skutki zwarcia CORE_LINK. Nie zmienia to poprawności pinoutu ani potrzeby przebudowy P04; nie wprowadzano zmian do P03 w tej recenzji.

Nie otwieramy kolejnej rewizji P04 bez konkretnej niezgodności z przymiarki, pomiaru lub zmiany kontraktu modułów. Ewentualny dobór samego R1 po pomiarze czasu watchdoga zapisujemy jako wariant montażowy z pomiarem, a nie automatycznie nowy layout.

## Źródła mechaniczne

- [Würth 61201021621, karta producenta](https://www.we-online.com/components/products/datasheet/61201021621.pdf): J3, raster 2,54 mm, korpus 20,36 × 9,0 mm; CAD ma miejsce i zalecany rozmiar otworów. J4–J6: [61200621621](https://www.we-online.com/components/products/datasheet/61200621621.pdf). Kopie w `audit/datasheets/`.
- Molex katalog F-49, strona 2 [archiwalnego pakietu producenta udostępnionego przez dystrybutora](https://datasheet.octopart.com/39-29-9163-Molex-datasheet-7546482.pdf): tabela obejmuje dokładnie 39-29-9069 i 39-29-9109; otwory styków 1,4 mm, kołków 3,0 mm, rzędy ogonków 5,5 mm, rozstaw kołków 17,8 / 26,2 mm. Aktualne strony [39-29-9069](https://www.molex.com/en-us/products/part-detail/39299069) i [39-29-9109](https://www.molex.com/en-us/products/part-detail/39299109) potwierdzają wersje pionowe Au z kołkami. Bieżącego szczegółowego rysunku sprzedażowego nie udało się pobrać; nie przedstawiam archiwalnej karty jako nowej rewizji producenta.
