---
name: kicad-pipeline-quirks
description: KiCad 10 pcbnew + Freerouting pitfalls hit while building EGRLab PCBs by script (P01 R2 … P04 R2, P03 R4 lokalna zmiana na gotowej płytce)
metadata:
  node_type: memory
  type: reference
  originSessionId: 1bdb3685-394a-4886-bbc7-14b9957d5ea4
  modified: 2026-09-28T19:34:15.391Z
---

Python KiCada: `/c/Program Files/KiCad/10.0/bin/python.exe` (pcbnew, PIL, numpy). Freerouting 2.1.0 + JRE 21: `C:/Users/tgorbacz/.codex/.chatgpt-projects/g-p-6a8827e57cc881919b26f761377a7bd3/.egrlab-toolchains/freerouting/` (`-mp 100` i `--router.max_passes` ignorowane — zawsze ~999 przebiegów; kończy się sam tylko, gdy nic nie zostaje do poprowadzenia; `--router.stop_pass_no=N` działa — P03 R4).

- Zapis płytki wczytanej z pliku bez obok leżącego .kicad_pro (np. `routing/prerouted.kicad_pcb`) nadpisuje docelowy `.kicad_pro` regułami domyślnymi → `set_rules.py` zaraz po imporcie.
- Freerouting nie widzi połączenia, gdy zablokowany odczep kończy się w środku odcinka szyny (T) — dubluje go. Szyny dzielić na odcinki z wierzchołkiem przy każdym odczepie/przelotce.
- Strefa miedzi eksportowana do DSN jako `plane` NIE jest przeszkodą dla innych sieci (P02: GND poprowadzone przez strefę VPROT) → w DSN zamienić na `keepout`.
- `-inc KLASA` nie wyjmuje sieci z licznika niepoprowadzonych → router mieli do limitu i nie zapisuje SES przy przerwaniu. Sieci robione wylewką/strefą (GND, VPROT) wyjmować z DSN przez `(pins)` puste — pady zostają przeszkodami.
- Freerouting jest wielowątkowy i niepowtarzalny: do wydania zapisywać SES i importować go ponownie (`--reuse-ses`).
- Import SES zostawia końce ścieżek rozjechane o < 5 µm i odcinki zerowe → DRC `track_dangling`; sprzątać (usunąć < 5 µm, skleić końce).
- Nowy PCB_TRACK dodany do wczytanej płytki potrafi zapisać się z siecią GND; `NetsByName().items()` zwraca złe obiekty (używać `FindNet`). Bezpieczniej modyfikować istniejące odcinki.
- `Remove()` na rysunkach płytki i pętle Remove/Add → segfault; napisy usuwać na poziomie pliku (sexpr) przed LoadBoard. Po pętlach Remove `FindFootprintByReference` zwraca SwigPyObject — iterować `GetFootprints()`.
- Tekst: `TransformShapeToPolygon` daje prostokąt; do glifów `TransformTextToPolySet`.
- PDF z KiCada stawia płytkę z początkiem (0,0) w rogu arkusza — własny generator PIL 600 dpi.
- pdftoppm jest w runtime Codexa (`.../codex-primary-runtime/dependencies/native/poppler/Library/bin/`).
- `CONNECTIVITY_DATA.GetConnectedPads(zone)` działa w Pythonie — dobre do kontroli „strefa łączy te pady”. Długość trasy po miedzi liczyć z padami THT jako węzłami (zmiana warstwy bez przelotki).
- Siatka o gęstym powtarzalnym wzorze (kolumny kanałów P00) — Freerouting zostawił 2 połączenia 3V3; lepiej poprowadzić wzór ręcznie i zablokować, router tylko do reszty.
- Własne zablokowane ścieżki: końce liczyć z pozycji padów po obrocie footprintu (P00: odczep HEART 1,27 mm obok padu J9 — DRC `track_dangling`); każdą taką pomyłkę wpisywać jako próbę ujemną.
- `kicad-cli pcb render` daje PNG z przezroczystym tłem — przed przycięciem nałożyć na biel (convert('RGB') daje czarne tło).
- Nadruk: DRC czysty to za mało — sprawdzać, czy oznaczenie nie leży w obrysie innej części i czy najbliższa jest jego własna (P02: „U2” w obrysie U1, „LV03” bliżej J4), a opisy nie pod korpusami (render 3D je chowa).

- `b.Remove()` w Pythonie pcbnew potrafi zepsuć SWIG całego procesu (potem `GetTracks`, `GetConnectivity`, nawet `LoadBoard` zwracają SwigPyObject) → ofiary wybierać po UUID (`t.m_Uuid.AsString()`), kasować na poziomie pliku (sexpr), wczytać ponownie (P03 `cleanup.py`).
- Freerouting łączy między sobą zablokowane kawałki GND (np. przelotki przy kondensatorach), choć piny GND wyjęto z DSN → sprzątanie „łańcuchów między zablokowaną miedzią”. Duplikaty odcinków (wyjście i powrót po tym samym torze) KiCad widzi jako `track_dangling` — najpierw usuwać duplikaty, potem ślepe końce.
- Pad GND potrafi zostać odcięty od obu wylewek przez trasy (losowo, zależnie od przebiegu) → ponawiać Freerouting do skutku i trzymać udany SES; `starved_thermal` może pojawić się dopiero po sprzątaniu → pętla solidyfikacji.
- Pełne połączenie padu z wylewką ustawiać PRZED sprawdzeniem łączności (zagłodzony pad liczy się jako niepołączony).
- Test „ścieżka w strefie” liczyć geometrią odcinka, nie bounding boxem (fałszywe trafienia na ukosach); zmiany wylewki w próbie ujemnej wymagają `ZONE_FILLER.Fill` przed zapisem, bo kontrola czyta zapisany fill.
- Rozmieszczenie: wyżarzanie (MST sieci bez GND, bloki IC+C, złącza na krawędziach) ściska wszystko przy MCU → dodać odstęp 3 mm między blokami; RUDY jako szybka miara zatłoczenia. Narzędzia w `Plytki/P03-R1-review/src/tools/place_*.py`.
- Nadruk: kolejność ma znaczenie (najpierw ciasne: KEY przy kluczach IDC, opisy TP, potem nazwy złączy, potem oznaczenia); bbox tekstu KiCad ma wysokość ok. 1,7 × rozmiar; znacznik pinu 1 IDC leży w kolumnie klucza 2.
- `ZONE.GetFilledPolysList(L)` dla warstwy, na której strefy nie ma → okno asercji wx blokuje proces bez żadnego wyjścia (wygląda na zawieszenie); zawsze najpierw `IsOnLayer(L)` (P04 R2).
- Czyste odtworzenie różniło się o 1 µm: sklejanie rozjechanych końców zależało od kolejności ścieżek w pliku, a ta od losowych UUID → sortować geometrycznie przed każdym krokiem zależnym od kolejności (P04 R2 `cleanup.py`, `stitch.py`).
- DRC `unconnected_items` z padem odciętym od wylewki podaje jako drugi koniec strefę z pozycją jej pierwszego wierzchołka (1; 1) → cel = największa wyspa wylewki; łączyć w rundach, bo DRC zgłasza jedną krawędź na klaster (P04 R2 `complete_routes.py --plan`).
- Kawałki wylewki zamknięte ścieżkami KiCad usuwa jako wyspy → wypełnić raz z `ISLAND_REMOVAL_MODE_NEVER`, w każdym takim kawałku postawić przelotkę tam, gdzie zachowana wylewka drugiej warstwy ma miejsce, przywrócić ALWAYS (P04 R2: +494 / +382 mm²).
- Przelotki są domyślnie zakryte maską (`tenting front/back yes`) — nadruk może przechodzić przez pierścień, omijać tylko otwór.
- Pętla routera: rozróżniać lukę trasowania (kod 3 → nowy Freerouting) od błędu skryptu (przerwać); SES każdej próby kopiować, inaczej po błędzie skryptu nie ma czego odtworzyć. Freerouting przy starcie sprawdza w sieci nową wersję.

- Gerbery dwóch przebiegów z tego samego projektu nie są identyczne bajtowo: numeracja apertur i kolejność obiektów idą za losowymi UUID, a wypełnienie wylewki potrafi zachować jeden współliniowy wierzchołek → porównywać semantycznie (`Plytki/P00-R3-review/src/gerber_equiv.py`: multizbiór flash/stroke/region, makra apertur, scalanie współliniowych wierzchołków, autotest).
- Próby ujemne na kopii płytki w innym katalogu: bez `fp-lib-table` DRC zgłasza `lib_footprint_issues` dla lokalnej biblioteki i oblewa każdą kopię → kopiować tabelę bibliotek (ścieżki bezwzględne) i zawsze dodawać próbę zerową (kopia bez wady = wszystko PASS, czysty DRC).
- Parsowanie opisów DRC działa tylko w jednym języku (P02 R2: angielski, P00 R2: polski „Pole PTH … na …”) → pady zawsze po UUID z raportu.
- Streszczenie WebFetch dla kart PDF bywa błędne (74LVC125A: podało VIH 0,65 VCC zamiast 2,0 V) → PDF zapisany przez WebFetch czytać pdfplumber z Pythona runtime Codexa i cytować tabelę.

- Skrypty porównujące dwa katalogi mogą pisać raport do pierwszego argumentu (P03-R2 `rebuild-compare.py` nadpisał plik wydania R2) → przed uruchomieniem cudzego skryptu sprawdzić, gdzie zapisuje; po każdej recenzji zweryfikować manifest oryginału.
- Próba ujemna „ścieżka odsunięta od padu” musi naprawdę odciąć miedź: przesunięcie o 1,27 mm przy padzie Ø1,7 i ścieżce 1 mm nadal łączy (P03-R2).

- Lokalna zmiana na gotowej płytce (P03 R4): nie trasować od nowa. Zasiać poprzedni SES jako zablokowaną miedź, DRC na zasianej płytce wskazuje sieci kolidujące (do przetrasowania), przed czyszczeniem odblokować zasiane elementy; zmianę kłaść ręcznie i blokować (`Plytki/P03-R4-review/src/seed_r3.py`, `unseed.py`, blok R4 w `route_critical.py`). Wynik: dokładny bilans miedzi do recenzji (`check_revision.py`).
- Freerouting w ciasnym korytarzu przy nowych częściach nie domknął 2 połączeń w 60 przebiegach i postawił ścianę 3V3 odcinającą inną sieć → ręczne, zablokowane poprowadzenie jest pewniejsze.
- Płytkę do eksportu DSN/DRC wczytywać w miejscu (obok `.kicad_pro`); wczytana z `routing/` dostaje reguły domyślne 0,2 mm / przelotki 0,6/0,3 i takie trafiają do DSN.
- DSN zapisuje współrzędne ≥ 100 mm z rozdzielczością 1 µm (6 cyfr znaczących) → zablokowana ścieżka kończy się 0,5 µm obok padu i Freerouting dokłada nakładający się odcinek („naprawa”), który DRC widzi jako `track_dangling` → importować wynik routera tylko dla sieci trasowanych.
- Paczki zamówieniowe (P04, 28.09): `kicad-cli pcb drc` tworzy `<nazwa>.kicad_prl`, gdy wydanie go nie ma → nie traktować jako zmiany projektu, usunąć. Excellon ma 0,001 mm, a pozycje dokładnie na połówce µm KiCad zaokrągla inaczej niż `round()` Pythona → otwory parować z tolerancją 0,001 mm i dołożyć próbę ujemną 5 µm. Wartości w specyfikacji (pierścień, liczba przelotek) liczyć z geometrii, nie z szablonu (P04: przelotki 0,8/0,4 → 0,20 mm).
- Freerouting nie zna prześwitu miedzi od krawędzi (poprowadził ścieżkę 0,43 mm od krawędzi) → w DSN dodać tylko dla routera pasy keepout 0,4 mm wzdłuż krawędzi.
- `--router.stop_pass_no=N` zatrzymuje Freerouting 2.1.0 po N przebiegach (R4: 60). Jego licznik „unrouted” nie jest miarą płytki (P03 R2/R3 kończyły z 5 przy kompletnej płytce) — rozstrzyga DRC KiCada po wylewkach.
- Nadruk: część sama w szczelinie między dwoma dużymi obrysami nie spełni reguły „najbliższy własny obrys” → nazwany wyjątek GAP (oznaczenie w tej samej szczelinie, reguła pomija tylko dwa obrysy szczeliny) + próba ujemna.

**How to apply:** przy każdej kolejnej płytce zaczynaj od `Plytki/P04-R2-review/src/` (najpełniejszy łańcuch: uzupełnienia z DRC w rundach, sprzątanie po UUID deterministyczne, zszywanie z ratowaniem wysp, KEY) albo `Plytki/P03-R1-review/src/` (najpełniejszy łańcuch: ponawianie routera, sprzątanie po UUID, zszywanie, nadruk z KEY) lub kolejności z `Plytki/P01-PCB-R2-review/verification/QA.md`. Zob. [[p01-pcb-r2-state]], [[p02-r1-state]], [[p03-r1-state]].
