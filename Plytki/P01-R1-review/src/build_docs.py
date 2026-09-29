from pathlib import Path
import json,csv,collections,html,shutil
P=Path(__file__).resolve().parents[1]
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
def write(path,text):(P/path).write_text(text.strip()+'\n',encoding='utf-8')

write('README.md','''
# P01 PROTECT — R1-review

23.09.2026 · baza EGRLab-v6.1-rc1 · prototyp, montaż ręczny THT, plan PCB 2L.

Pakiet zawiera funkcjonalny schemat P01 w KiCad, listę części, lokalne biblioteki,
rysunek podziału płytki, kartę wiązek i dowody kontroli. **Etap: przegląd schematu,
przed prowadzeniem ścieżek.** Nie zawiera Gerberów ani zatwierdzonej płytki do produkcji.

P07 jest WSTRZYMANE: rozważany moduł BTS7960 zamiast Pololu 1451. Wrócić do P07 po
otrzymaniu egzemplarza. Decyzję zapisano także w EGRLab-AKTYWNE.md; P01 nie zależy
od rozstrzygnięcia sygnałów sterowania P07, ale jego budżet pozostaje 5 A.

## Otwieranie

- `output/pdf/P01-R1-schemat.pdf` — trzy arkusze A3 do czytania i wydruku.
- `eda/P01.kicad_pro` — projekt KiCad 10; otwórz główny `P01.kicad_sch`.
- `docs/BOM.csv` — części per oznaczenie, MPN, footprint, źródło.
- `docs/ZAKUPY.csv` — części zgrupowane; osobno `docs/BOM-MECHANIKA.csv`.
- `docs/ZMIANY.md` — różnice względem bazy; bez zmian topologii P01.
- `docs/WIAZKI.md` — lutowanie, kotwy i mapowanie pinów.
- `mechanical/P01-strefy.svg` i `mechanical/MECHANIKA.md` — plan 160 × 100 mm.
- `docs/ODBIOR.md` — procedura pomiarów, wszystkie próby sprzętowe jeszcze niewykonane.
- `docs/PRZEGLAD.md` — kolejna bramka procesu i kwestie do zamknięcia.

## Co jest sprawdzone

Porównanie rzeczywistego eksportu KiCad XML z zamrożoną bazą: 87 elementów (77 z bazy
+ 10 pól pomiarowych), 189 końcówek i 34 sieci. Zero różnic połączeń.
ERC: zero błędów i ostrzeżeń. Raporty znajdują się w `verification/`.
Kontrola padów dotyczy numeracji, rastra wybranych kondensatorów i kotew wiązek;
**nie zastępuje** odbioru gabarytów zakupionych części na wydruku 1:1.

Testy mutacyjne celowo podmieniają D/S Q1, wejścia OVP, odłączają SAFE_N i usuwają
footprint J6 w kopiach netlisty. Każda zmiana musi zostać wykryta. Obliczenia DC
z bazy uruchomiono na kopii, bez zmieniania bazy; nie są symulacją przełączeń.

## Co trzeba zamknąć przed layoutem

1. Niezależna recenzja tych konkretnych trzech arkuszy i doboru części.
2. Rysunek mocowania wybranego radiatora: obrys przewidziano, jego otworów jeszcze
   nie przeniesiono na PCB. Nie zgadywać wymiarów ze zdjęcia handlowego.
3. Dostępność dokładnych MPN, zwłaszcza C1 i rezystorów H4. Zamiennik wymaga
   sprawdzenia gabarytów, pinów i parametrów, zanim zostanie wpisany do layoutu.

Biblioteki są lokalne w `eda/libraries`; projekt otwiera się bez generatora.
Skrypty `src/build_*` to narzędzia autora, które nadpisują wygenerowane pliki.
Po ręcznej edycji w KiCad nie uruchamiać ich ponownie bez przeniesienia zmian.
`src/cadlib.py` szuka źródłowych bibliotek KiCad w lokalnym katalogu narzędzi autora;
ta ścieżka dotyczy regeneracji, nie otwierania projektu.

Wydania V3/V5/V6/6.1-rc1 pozostają niezmienione. `baseline/` jest kopią odniesienia
ze skrótami SHA-256; nie stanowi drugiej bieżącej wersji schematu.
''')

write('docs/ZMIANY.md','''
# Rejestr zmian P01-R1-review

| ID | Zmiana | Skutek i sprawdzenie |
|---|---|---|
| P01-001 | Trzy funkcjonalne arkusze KiCad: tor mocy, AUX/OVP/UVLO, SAFE | Eksport XML porównany pin po pinie z 6.1-rc1. |
| P01-002 | J_PGB → J5, J_SUPPLYA → J6, J_BATB → J7, J_PRES → J8, W_PRES → R34 | Wyłącznie oznaczenia. Pole BaselineRef zachowuje powiązanie. Numeracja pinów zewnętrznych bez zmian. |
| P01-003 | Lokalny symbol TL431BILP: 1=K, 2=A, 3=REF | Standardowy symbol biblioteki miał inne przypisanie 1/3. W tym układzie 1 i 3 są zwarte, ale funkcje pinów muszą być poprawne. Kontrola automatyczna funkcji. |
| P01-004 | Dokładne serie rezystorów: większe MFR-50/H4; R1/R23/R27 PR02 2 W | Wartości R i progi bez zmian. R27 zwiększony z 0,5 do 2 W; nie jest to dowód odporności impulsowej całej gałęzi. |
| P01-005 | C7 22 µF/50 V i C9 47 µF/50 V | Wyższe napięcie znamionowe, te same pojemności. R2=1 Ω nadal w szeregu z C9. |
| P01-006 | C8/C10/C11/C12/C13 w wykonaniu Vishay H5, 5 mm | W trakcie doboru odrzucono L2 (2,5 mm); nie był to wariant opublikowany. Konkretny MPN i footprint są zgodne. |
| P01-007 | TP1–TP10: dodatkowe PTH do pomiarów | Brak nowej funkcji obwodu; same pola, nie zamawiać 10 złączy. |
| P01-008 | H_PG i H_BAT lutowane; kotwy 12,5 mm od rzędu lutów | PG 200 mm/AWG22; BAT 200 mm/2,5 mm². Zgodnie z 6.1. Otwory opasek 3,2/4,2 mm. |
| P01-009 | Q2/Q4: do zakupu onsemi 2N5401YBU zamiast starszego 2N5401G | E-B-C, PNP 150 V, 600 mA; brak zmiany sieci. Nowy producentowy bondout potwierdzony w karcie. Czas odcięcia pozostaje próbą sprzętową; nie zakładać identycznej dynamiki serii. Nie zamawiać wariantu -C. |
| P01-010 | J6 Phoenix 1757255; gniazdo kątowe MSTBA 3p 5,08 | Zgodne z rodziną MSTB 5,08. Wiązka SUPPLY należy do P02. |
| P01-011 | Q1/D2: otwory TO-220 powiększone do 1,4 mm, pady 2,1×3 mm | Zwykły footprint miał 1,1 mm, mniej niż przekątna maksymalnej nóżki Q1 ok.1,18 mm. Rozstaw2,54 bez zmian, odstęp miedzi między padami0,44 mm. |
| P07-HOLD | Zatrzymanie P07 do odbioru modułu BTS7960 | Bez zmian P07 w bazie. Nie zamawiać jego PCB ani Pololu według starej listy. |

Nie zmieniono wartości dzielników, punktów pracy, połączeń SAFE_N, budżetu 5 A,
ani strategii zewnętrznego bezpiecznika. Dokładny dobór zamienników przy zakupie
jest kontrolowaną zmianą; nie wolno go ukrywać pod tym samym numerem pakietu.
''')

write('docs/WIAZKI.md','''
# P01 — wiązki i punkty dostępu

Wymiar 200 mm oznacza długość gotowego odcinka od rzędu lutów PCB do czoła wtyku,
z tolerancją montażową ±10 mm. Materiał przyciąć z zapasem do obróbki. Żyły numerować
na obu końcach; kierować się numerami komór producenta, nie widokiem „od lewej”.

## H_PG: 1 komplet na P01

Sześć żył AWG22 (około 0,34 mm²), izolacja OD 1,3–2,0 mm, 200 mm.
P01/J5: lut do sześciu PTH w rastrze 2,54 mm; brak gniazda na P01.
P04: obudowa Mini-Fit Jr 6p Molex **39-01-2060**, sześć styków żeńskich Au
**39-00-0429**, dobranych do AWG22. Materiały i zakres AWG:
[Molex](https://www.molex.com/en-us/products/part-detail/39000429).

| Pin J5 / komora wtyku PG | Sieć |
|---:|---|
| 1 | 3V3_IO — z odbiornika, nie z AUX5 |
| 2 | SAFE_N — otwarty kolektor Q7 |
| 3 | GND |
| 4 | PG_SEND |
| 5 | PG_LINK |
| 6 | GND |

Opaska 2,5 mm przechodzi przez dwa otwory NPTH Ø3,2 mm, 12,5 mm od rzędu lutów.
Otwory PTH Ø1,1 mm. Przewody prowadzić bez ostrych zgięć, opaska obejmuje izolację,
nie odizolowaną żyłę. Nie dociągać opaski tak, aby przeciąć izolację. Nie prowadzić
tej wiązki razem z przewodami silnika. Styków we wtyku nie zalewać cyną po zacisku.
Można zamówić gotowe przewody z tymi stykami, przyciąć i polutować koniec P01.

## H_BAT: 1 komplet na P01

Dwie żyły linki miedzianej 2,5 mm², po 200 mm, plus czerwony, masa czarna.
P01/J7: lut do PTH Ø2,4 mm w rastrze 7,62 mm. Kotwa 12,5 mm od rzędu lutów,
dwa NPTH Ø4,2 mm, opaska 3,6 mm. Rozstaw kotew 13,62 mm; środek wiązki między nimi.
Na drugim końcu wtyk Phoenix **1757019**, MSTB 2,5/2-ST-5,08, z tulejkami
2,5 mm² dopasowanymi długością do zacisku. Nie cynować linki do zacisku śrubowego.
Pin 1=BAT_FUSED, pin 2=GND. Bezpiecznik 5 A jest **przed** H_BAT, blisko źródła.

## SUPPLY: wiązka po stronie P02

Na P01/J6 zamontować Phoenix **1757255**, MSTBA 2,5/3-G-5,08.
Wtyk przewodu P02: **1757022**, MSTB 2,5/3-ST-5,08. Pin 1=VPROT, 2=GND, 3=NC.
Nie mostkować pinu 3. Oznakowanie BAT/PG/SUPPLY zachować również na obudowie.
W BOM P01 nie liczyć ponownie wiązki SUPPLY ani gniazda PG na P04.

## Pomiar i serwis

J1: BAT_FUSED/GND; J2: VPROT/GND; J4: 3V3_IO/SAFE_N/GND;
J8: PG_SEND/PG_LINK. Są to pola pomiarowe, nie dodatkowe kupowane złącza.
J3 jest rzeczywistą listwą 2p 2,54 mm: zwarcie wymusza OFF, normalnie otwarte.
TP1 VS, TP2 GATE, TP3 AUX_IN, TP4 AUX5, TP5 REF, TP6 OK, TP7 ENABLE,
TP8 OV_SENSE, TP9 UV_SENSE, TP10 GND. Każdy punkt oznaczyć na silkscreenie.

Przed podłączeniem P04/P02 sprawdzić każdą żyłę miernikiem i próbą poruszenia
wiązki. Obecność modułu: ciągłość PG_SEND–R34–PG_LINK, brak zwarcia do SAFE_N.
''')

write('mechanical/MECHANIKA.md','''
# Założenia mechaniczne P01-R1

Plan stref znajduje się w `P01-strefy.svg`. To rozplanowanie powierzchni, nie
rysunek wierceń radiatorów ani rozmieszczenie każdego elementu.

PCB 160 × 100 mm, FR4 1,6 mm, 2 warstwy. Propozycja miedzi: 70 µm na warstwę;
mało kosztowny zapas dla prototypu. Cztery otwory mocujące NPTH Ø3,2 mm:
(5,5), (155,5), (5,95), (155,95) mm względem lewego górnego rogu.
Rezerwacja wolna od miedzi i elementów Ø8 mm wokół każdego mocowania.
Wymiary do utrwalenia po przeglądzie; nie używać SVG jako pliku produkcyjnego.

## Radiatory i dostęp

Kandydat: dwa osobne **Fischer SK 129 63,5 STIS**, nominalnie 4,5 K/W w warunkach
producenta. Profil 42 × 25 mm, długość 63,5 mm; plan zakłada pionową długość 63,5 mm
i obrys w PCB 42 × 25 mm. Rezerwować dwa pola 46 × 30 mm oraz wolną wysokość
co najmniej 75 mm nad PCB. Przed przyjęciem obudowy potwierdzić tę orientację
na rysunku konkretnego wariantu TO-220 oraz sposób przykręcenia tranzystora.

[Karta Fischera](https://www.tme.eu/Document/3f44de1970b9ae8f6a3dac0e6790ddd5/SK12963.5STIS.pdf)
potwierdza profil i Rth; **położenie kołków oraz otworów nie zostało przeniesione
do footprintu**. To otwarta pozycja M-01 przed layoutem, nie „zatwierdzone wiercenie”.
Alternatywa mechaniczna: osobne radiatory przykręcone do wspornika obudowy,
pod warunkiem krótkich wyprowadzeń D2/Q1 oraz ponownego zatwierdzenia mocowania.

D2 tab=VS, Q1 tab=VPROT. Oba mocowania z izolacją elektryczną: podkładka termiczna
i tulejka śruby; sprawdzić omomierzem po dokręceniu. Nie polegać na anodowaniu
aluminium jako izolatorze. Nie łączyć różnych tabów wspólnym metalowym mocowaniem.
Jeżeli wariant STIS zawiera podkładkę, nie dokładać drugiej; tulejkę dobrać do śruby.
Radiator nie może wisieć wyłącznie na nóżkach TO-220.

## Prowadzenie płytki

Tor BAT_FUSED–D2–Q1–VPROT w górnej strefie; szerokie pola po obu stronach PCB,
krótkie połączenia i kontrola przewężeń przy padach. Startowe minimum korytarza
miedzi 5 mm; po trasowaniu obliczyć wzrost temperatury dla rzeczywistych długości,
miedzi i przewężeń. Sama szerokość nie nadaje płytce deklaracji „10 A”. Dopuszczony
prąd systemu pozostaje 5 A po odbiorze. Możliwość przylutowania równoległej linki
2,5 mm² na torze mocy przewidzieć jako rezerwę, nie obejście błędnego layoutu.

D1 tuż przy J7, D3 przy Q1/wyjściu, powroty TVS krótkie do GND mocy.
Masa komparatora/wzorca osobną drogą do punktu GND_STAR przy wejściu, bez prądu
transili w tej ścieżce. Nie tworzyć przerwy w masie pod sygnałami przez dzielenie
poligonu „na oko”. Q2/R27/D4/C5/C6 blisko Q1, pętla wyłączenia minimalna.
R1 i R23 unieść około 3 mm nad PCB i odsunąć od wzorca oraz dzielników.
U3/D6/R5–R11 nie umieszczać przy radiatorach. RV1 dostępny dla izolowanego wkrętaka.

Odległość rzędu lutów H_BAT/H_PG od kotwy: 12,5 mm, już zawarta w footprintach.
Przewody wychodzą w stronę kotwy; elementy nie mogą zajmować pasa między lutem
i kotwą. Dodatkowo pozostawić dostęp do zamka opaski i przestrzeń dla gięcia żył.
Duże transile podparte, bez naprężania obudowy podczas gięcia końcówek.

## Biblioteka a rzeczywiste części

TO-92 używa rastra szerokiego 2,54 mm: końcówki części o rastrze 1,27 mm trzeba
delikatnie uformować przed lutowaniem. Nie rozginać ich przy samym plastiku.
Przed Gerberami wydrukować stronę montażową 1:1, sprawdzić miarką skalę oraz
przymierzyć TO-220, transile P600, złącze Phoenix, kondensatory i radiatory.
Przymiarka nie zastępuje kontroli średnic otworów w pliku PCB.
''')

write('docs/PRZEGLAD.md','''
# Przegląd i przejście do layoutu

Stan 23.09.2026: sprawdzenia autora zakończone; recenzja niezależna NIE WYKONANA;
PCB/layout, DRC, pomiary sprzętowe NIE WYKONANE. Nie stawiać znaków PASS dla etapów,
które dopiero są opisane.

| ID | Do rozstrzygnięcia | Kryterium zamknięcia |
|---|---|---|
| E-01 | Niezależny przegląd schematu i warunków granicznych | Recenzent podaje pin/sieć/warunek i dowód błędu albo potwierdza sprawdzenie. Uwagi trafiają do rejestru; brak zmian „przy okazji”. |
| M-01 | Mocowanie dwóch radiatorów | Rysunek konkretnego wykonania TO-220, pozycje kołków/śrub i dostęp do śrub przeniesione do footprintu, zweryfikowane 1:1. |
| B-01 | Zamknięcie zakupów | Dokładne dostępne MPN dla H4, C1 i złącza J6. Sprawdzenie maksymalnych gabarytów i średnic wyprowadzeń, w szczególności TO-220 względem otworu footprintu. Zamienniki ze zmianą w rejestrze. |
| L-01 | PCB 2L | Placement, ścieżki, płaszczyzny, DRC, porównanie PCB–schemat, odczyt Gerberów niezależną przeglądarką. |
| H-01 | Odbiór P01 na stole | Wypełniony protokół ODBIOR.md, bez przenoszenia wyników obliczeń do rubryki pomiarów. |

## Zakres recenzji E-01

- Orientacja D2/Q1; brak obejścia odłącznika przez body diode i radiator.
- Domyślny OFF bez AUX5, startup MCP120, wspólna sieć OC/OK, INHIBIT.
- OVP/UVLO/histereza, obciążenie TL431, ESR C9+R2, tolerancje i temperatura.
- Praca Q2/Q4 z wybranym 2N5401YBU; budżet czasu wyłączenia wraz z C5/C6.
- Wyjście SAFE_N przy zaniku zasilania P01 i nadal obecnym 3V3_IO.
- Energia TVS, SOA Q1 i regeneracja: rozdzielić przyjęty cel od wyniku pomiaru.
- Konkretne footprinty i numeracja; nie wystarcza samo „TO-92/TO-220”.

ERC i porównanie połączeń wykrywają błędy przeniesienia projektu do CAD; nie
udowadniają poprawności samej architektury. Test mutacyjny potwierdza działanie
kontroli regresji, nie pełne pokrycie wszystkich możliwych awarii.

## Jak poprawiać

Zamrozić otrzymaną paczkę. Każda uwaga ma ID, wagę, dowód, decyzję i kontrolę,
która wykryje powtórzenie błędu. Kolejny pakiet P01-R2 powstaje tylko dla zmian
wynikających z przeglądu. Po zmianie elektrycznej ponownie XML/porównanie/ERC;
po zmianie footprintu także pad mapping i kontrola wymiarów. Po poprawkach recenzent
sprawdza różnicę i punkty dotknięte zmianą. Nie przenosić prac na P07.

## Powtórzenie kontroli

W katalogu pakietu, z KiCad CLI 10 i Pythonem 3:

```text
kicad-cli sch export netlist --format kicadxml -o verification/P01.xml eda/P01.kicad_sch
kicad-cli sch erc --format json -o verification/erc.json eda/P01.kicad_sch
python src/verify.py
python src/check_package.py
```

Nie wykonywać `build_schematic.py` po ręcznej edycji jako sposobu na „naprawienie”
wyniku testu. Eksport i porównanie mają badać rzeczywisty zapis edytora.
''')

# Baseline acceptance procedure remains available unchanged; current cover clarifies the stage and pin aliases.
base=(P/'baseline/P01-PROTECT/URUCHOMIENIE.md').read_text(encoding='utf-8')
write('docs/ODBIOR.md','''
# P01-R1 — odbiór modułu

**Wszystkie pomiary do wykonania.** To etap po PCB i montażu. Najpierw sama P01,
bez ECU, EGR, ESP32 i dalszych płytek. Procedura poniżej pochodzi z bazy 6.1;
obowiązują korekty wykonawcze R1: Q2/Q4=2N5401YBU, C7/C9=50 V, R27=2 W.
J4 zachowuje pinout; do P04 docelowo idzie wiązka J5, więc nie łączyć równocześnie
dwóch przewodów SAFE_N przez J4 i J5. J1/J2/J4 są polami, nie gniazdami.

Próby obejmujące KPWR/mostek i silnik pozostają etapem integracji po odwieszeniu
P07. Nie odblokowują ani nie kończą automatycznie jego przeglądu.

---
'''+base)

groups=collections.OrderedDict()
for r,p in parts.items():
 if r.startswith('TP') or p['mpn'].startswith(('PCB','Tinned')):continue
 key=(p['mpn'],p['display'])
 groups.setdefault(key,[]).append(r)
with (P/'docs/ZAKUPY.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Nazwa / MPN','Ilość szt.','Wartość','Oznaczenia','Status'])
 for (mpn,val),refs in groups.items():w.writerow([mpn,len(refs),val,', '.join(refs),'DOBÓR DO RECENZJI; dostępność niepotwierdzona'])
mechanical=[
 ['PCB P01 FR4 1.6 mm, 2L, 160x100 mm, proponowane Cu70um',1,'dopiero po layout/DRC'],
 ['H_PG: wiązka 6xAWG22, gotowa 200mm, PTH -> Mini-Fit Jr Au 6p',1,'komplet; składniki poniżej, nie liczyć podwójnie'],
 ['H_PG / obudowa Molex 39-01-2060',1,'składnik wiązki'],
 ['H_PG / styk Molex 39-00-0429 Au',6,'składnik wiązki; AWG22'],
 ['H_PG / linka AWG22 OD1.3-2.0mm po ok.230mm do obróbki',6,'składnik wiązki; gotowa długość200mm'],
 ['H_PG / opaska 2.5mm',1,'składnik wiązki'],
 ['H_BAT: 2x2.5mm2, gotowa 200mm, PTH -> MSTB 2p',1,'komplet; składniki poniżej'],
 ['H_BAT / wtyk Phoenix1757019',1,'składnik wiązki'],
 ['H_BAT / przewód2.5mm2 po ok.230mm czerwony/czarny',2,'składnik wiązki'],
 ['H_BAT / tulejka2.5mm2 dobrana do zacisku',2,'składnik wiązki'],
 ['H_BAT / opaska3.6mm',1,'składnik wiązki'],
 ['R34 / zwora z drutu cynowanego0.6mm',1,'odcinek do rastra15.24mm; bez rezystora'],
 ['Radiator Fischer SK12963.5STIS, wykonanie TO-220',2,'kandydat; M-01 mocowanie do zamknięcia'],
 ['Zestaw izolacyjny TO-220: podkładka+tulejka M3',2,'bez dublowania podkładki dołączonej do radiatora'],
 ['Śruba M3 + podkładka + nakrętka do TO-220',2,'długość po doborze radiatora; nie kupować w ciemno'],
 ['Dystans izolacyjny M3 10mm',4,'montaż PCB'],
 ['Śruba M3 do dystansu PCB',8,'długość do obudowy i dystansu'],
 ['Zworka serwisowa2.54mm do J3',1,'normalnie zdjęta'],
 ['Bezpiecznik5A DC i oprawa przy źródle',1,'element zewnętrznego zasilania; jeżeli już jest, nie dublować'],
 ]
with (P/'docs/BOM-MECHANIKA.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Nazwa','Ilość','Uwagi']);w.writerows(mechanical)

write('docs/FOOTPRINTY.md','''
# Kontrola bibliotek — zakres i źródła

Wszystkie użyte footprinty i symbole są w paczce. `verification/footprint-pads.csv`
zawiera rzeczywiste numery padów i średnice z tych plików, a nie nazwę oczekiwanej
obudowy. Pozwala to recenzentowi odnieść konkretny otwór do konkretnego wyprowadzenia.

| Grupa | Dobór / kontrola |
|---|---|
| R ogólne | Yageo MFR-50, 0,5 W, 1%; obrys10,2×4mm, raster15,24, otwór1mm. Nie miniaturowe MFR-50S. |
| R5–R11 | HOLCO H4, 0,5W, 0,1%, 15ppm/K; wspólny większy footprint15,24mm. Dokładne MPN dostępnościowo do zamknięcia w B-01. |
| R1/R23/R27 | Vishay PR02, 2W, raster17,78, otwór1,1mm. |
| D1/D3 | Duże obudowy P600, raster20,32, otwór1,6mm; D3 katoda pad1, D1 dwukierunkowy bez polaryzacji. Nie footprint DO-201 dla tych dwóch transili. |
| D5 | DO-201, raster15,24; katoda pad1. D4/D6–D8 DO-35, raster10,16. |
| C2/C4/C6 | TDK B32529, obrys7,3×2,5mm, raster5mm; C5 obrys7,3×3,5mm. |
| C8/C10/C11/C12/C13 | Vishay K15, wykonanie H5, raster5mm; obrys uwzględnia wygięte końcówki, nie symboliczny dysk. |
| Elektrolity | C1 D5/P2; C3 D8/P3,5; C7 D5/P2; C9 D6,3/P2,5. Wartości i napięcia w BOM. |
| Q1/D2 | Lokalny TO-220 pionowy, G-D-S / A-K-A, raster2,54, otwory1,4mm, pady2,1×3mm. Maksymalna nóżka Q1 1,01×0,61mm (przekątna1,18mm); standardowe1,1mm za małe. Mocowanie radiatora osobno w M-01. |
| Q2–Q8 | TO-92 wide, E-B-C; Q2/Q4 tylko wybrany bondout YBU bez -C. |
| U1 | LM2936 TO-92: OUT1/GND2/IN3. |
| U2 | LM2903P, DIP8; wyjścia1/7, VCC8, GND4; nie zmieniać automatycznie na wariant innego producenta. |
| U3 | TI TL431BILP, K1/A2/REF3. Lokalny symbol poprawiony względem symbolu ogólnego. |
| U4 | MCP120-450DI/TO, bondout D: RESET1/VDD2/GND3. |
| J6 | Phoenix1757255: lokalna kopia footprintu konkretnego modelu, raster5,08mm; pin3 NC. |

Źródła per MPN są w BOM. Dla rezystorów H4 adres reprezentatywnej części rodziny
nie jest potwierdzeniem dostępności wszystkich wartości. Lista źródeł pobranych
automatycznie w `reference/sources.json` jawnie zachowuje również nieudane próby
pobrania; nie należy interpretować HTTP403 jako dowodu przeczytania datasheetu.

Kluczowe źródła kontroli:

- [TL431 TI, LP](https://www.ti.com/lit/ds/symlink/tl431.pdf)
- [LM2936 TI](https://www.ti.com/lit/ds/symlink/lm2936.pdf)
- [2N5401 onsemi, YBU](https://www.onsemi.com/download/data-sheet/pdf/2n5401-d.pdf)
- [2N5550/2N5551 onsemi](https://www.onsemi.com/download/data-sheet/pdf/2n5550-d.pdf)
- [K series Vishay — kod H5](https://www.vishay.com/docs/45171/kseries.pdf)
- [TDK B32520–B32529](https://www.tdk-electronics.tdk.com/inf/20/20/db/fc_2009/B32520_529.pdf)
- [MFR Yageo](https://www.yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf)
- [PR02 Vishay](https://www.vishay.com/docs/28729/pr010203.pdf)

Nie skopiowano modeli STEP, więc brak pełnej kontroli kolizji3D. Zamknięcie B-01
oznacza również sprawdzenie największych wymiarów, tolerancji oraz miejsc na lut
i narzędzie; nie tylko dopasowania numerów pinów.
''')

# Native vector overview; dimensional zones, explicitly not PCB artwork.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="940" viewBox="0 0 240 188">',
'<rect width="240" height="188" fill="#fff"/>',
'<style>text{font-family:Arial,sans-serif;fill:#24364b} .t{font-size:2.7px} .s{font-size:2.3px} .h{font-size:4px;font-weight:bold}</style>',
'<text x="15" y="10" class="h">P01 PROTECT / R1 — plan stref do przeglądu</text>',
'<text x="15" y="16" class="t">160 × 100 mm · PCB 2L · widok od strony elementów · bez tras i wierceń radiatorów</text>',
'<g transform="translate(30,32)"><rect width="160" height="100" rx="1" fill="#f7fafb" stroke="#24364b" stroke-width="0.5"/>']
for x,y in [(5,5),(155,5),(5,95),(155,95)]:
 svg += [f'<circle cx="{x}" cy="{y}" r="4" fill="none" stroke="#c9d4dd" stroke-dasharray="1 1"/><circle cx="{x}" cy="{y}" r="1.6" fill="white" stroke="#24364b" stroke-width="0.3"/>']
def zone(x,y,w,h,title,line,color):
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="1" fill="{color}" stroke="#8ca4b5" stroke-width="0.3"/><text x="{x+2}" y="{y+5}" class="t">{html.escape(title)}</text><text x="{x+2}" y="{y+10}" class="s">{html.escape(line)}</text>')
zone(9,12,20,35,'BAT / D1','lut + kotwa','#e0eef8')
zone(34,10,46,30,'D2 + radiator','rezerwa 46 × 30','#ffebce')
zone(88,10,46,30,'Q1 + radiator','rezerwa 46 × 30','#ffebce')
zone(136,14,18,31,'J6 / D3','SUPPLY','#e0eef8')
zone(91,44,43,18,'Sterowanie Q1','Q2 / D4 / C5 / C6','#f8eddb')
zone(10,51,35,34,'AUX / U1','R1 poza wzorcem','#e7edfb')
zone(49,52,38,34,'OVP / UVLO','RV1 dostępny','#deefeb')
zone(91,69,43,19,'SAFE / Q7','3V3 z odbiornika','#e7edfb')
zone(138,62,16,27,'PG','kotwa','#e0eef8')
svg+=['<path d="M0,-5 H160 M0,-7 V-3 M160,-7 V-3" stroke="#24364b" fill="none" stroke-width="0.3"/><text x="74" y="-7" class="t">160 mm</text>',
'<path d="M-6,0 V100 M-8,0 H-4 M-8,100 H-4" stroke="#24364b" fill="none" stroke-width="0.3"/><text x="-20" y="50" class="t">100 mm</text></g>',
'<text x="30" y="142" class="t">Mocowania PCB: (5,5), (155,5), (5,95), (155,95), NPTH Ø3,2; rezerwa Ø8 mm.</text>',
'<text x="30" y="149" class="t">Radiatory: pozycje wstępne. Wolna wysokość ≥75 mm; osobne i izolowane mocowania.</text>',
'<text x="30" y="156" class="t">Kotwy wiązek: 12,5 mm od rzędu lutów, bez elementów i ostrych zgięć w pasie wiązki.</text>',
'<text x="30" y="163" class="t">D1/D3 — krótkie pętle mocy. U3/D6/dzielniki — z dala od źródeł ciepła.</text>',
'<text x="30" y="175" class="h">NIE JEST PLIKIEM DO PRODUKCJI PCB</text></svg>']
write('mechanical/P01-strefy.svg',''.join(svg))
print('Review documents, procurement tables and mechanical SVG created')
