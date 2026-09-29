# Raport wydania P01-R3-review

23.09.2026. Schemat i dokumentacja przed layoutem; sprzęt NIE ZBADANO.

| Kontrola | Wynik |
|---|---|
| Eksport CAD | 89 elementów, 193 końcówki, 35 sieci; zgodny z bazą i jawną deltą |
| ERC KiCad 10.0.6 | 0 naruszeń w raporcie; nie rozszerzano listy domyślnie pomijanych kategorii |
| Kontrole pakietu | 207 PASS, w tym 11 celowo wprowadzonych błędów wykrytych |
| Spójność wydania | 19 PASS |
| Delta R2, mechanika i kontrakt HOLD | 107 PASS, w tym 4 błędne topologie HOLD odrzucone |
| Dynamika | 30 kontroli PASS: 26 scenariuszy, wykrycie błędu R1, 3 porównania kroku |
| Powrót, seria, rezerwa, zimny start | 12 kontroli PASS, w tym oczekiwane wykrycie zaniku bez rezerwy i jej wyczerpania |
| Granice algebraiczne | 2 kontrole PASS; Cgd≤2nF jest założeniem, nie gwarantowaną granicą części |
| Podtrzymanie | Warunkowe obliczenie 85.38 ms wobec wymaganych 50 ms |
| PDF | 3 strony schematu P01 i 1 strona obwodu HOLD; kontrola wizualna w VISUAL-QA.md |

Zimny start modelu przy 11,5 V / 6 W: napięcie banku po 15 s
9.836 V, szczyt prądu kanału Q1 1.518 A.
Zerowe napięcie na początku tej próby jest oczekiwane; nie jest testem już
naładowanej rezerwy. C bezpośrednio obciążające P01 to 198+22=220 µF.

Najważniejsze ograniczenia: modele MOS są przybliżone, odbiornik jest modelem
stałej mocy z założonym odcięciem 6,5 V. Nie potwierdzono SOA, termiki, pełnego
toru detektora OVP, odporności automotive, działania przetwornic ani zapisu SD.
P02-HOLD jest obwodem i kontraktem do włączenia w przyszłą P02. Dobór końcowy
bezpiecznika, kodowanie opcjonalnej wiązki, nadzór rezerwy i firmware są zadaniami
etapu P02/CORE. Nie są zamknięte samym raportem PASS.

W pierwszej wersji testu powrotu błędnie oczekiwano zaniku poniżej 7 V dla każdego
Vth. Zachowano wynik w recovery-initial-expectation.json. Test obecny wymaga
wykrycia zaniku w konkretnych przypadkach; nie twierdzi, że każdy egzemplarz
zrestartuje logikę. Kryteriów ciągłości z HOLD nie obniżono.

Logi zawierają ostrzeżenia o niedostępnym profilu/rejestrze KiCad, cache fontów
oraz pliku inicjalizacji ngspice. Eksporty powstały, symulacje zakończyły się,
wektory i końcowe renderowanie zostały sprawdzone. Talii nie oparto na zewnętrznym
spinit. Szczegóły wykonania są w plikach *-run.txt.

Kontrola historii: 87/88 plików R1 oraz
170/170 plików R2 zgodnych z manifestami;
oba archiwa zgodne z opublikowanymi SHA256. W obecnym R1 plik P01.kicad_pro
różni się od archiwalnego pustego {}: zawiera ustawienia projektu KiCad.
Zachowano jego bieżącą treść; różnica w R1-project-settings.diff. To jedyna
wykryta rozbieżność historii, nie poprawka schematu wykonana w R3. Ten proces
nie zapisuje do R1/R2 ani do recenzji.

Następny etap: layout P01 2L według MECHANIKA/METROLOGIA, kontrola wydruku 1:1
oraz DRC. Do produkcji potrzebna jest osobna kontrola gotowej PCB. P07: HOLD.
