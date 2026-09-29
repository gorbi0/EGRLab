"""R2 documents; inputs are frozen R1 references plus actual R2 validation results."""
from pathlib import Path
import json,csv
P=Path(__file__).resolve().parents[1]
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
dyn=json.loads((P/'verification/dynamics.json').read_text(encoding='utf-8'))
rows={x['id']:x for x in dyn['results']}
def write(f,t):(P/f).write_text(t.strip()+'\n',encoding='utf-8')
def old(f):return (P/'reference/R1-docs'/f).read_text(encoding='utf-8')
write('README.md','''
# EGRLab P01 PROTECT — R2-review

23.09.2026. Rewizja po recenzji Opusa. R1 i baza EGRLab-v6.1-rc1 pozostają niezmienione.
**Schemat do ponownej recenzji, nie do zamówienia PCB.** P07 nadal HOLD.

Tor bramki: C5=10nF, C6=1µF (film ±5%), R21=100kΩ, R22=470kΩ, R27=10Ω/2W.
Q2 jest teraz P-MOS SUP53P06-20-E3 w TO-220; D9=15V chroni jego bramkę.
Nie zakładamy już dużego hFE małego PNP przy setkach mA. Pinout Q2 jest INNY niż w R1.

- `eda/P01.kicad_pro` — KiCad10, trzy arkusze, lokalne biblioteki.
- `output/pdf/P01-R2-schemat.pdf` — trzy arkusze A3.
- `docs/BOM.csv`, `ZAKUPY.csv`, `BOM-MECHANIKA.csv` — części i wiązki.
- `docs/ZMIANY.md` — odpowiedź na R1-01…R1-04.
- `docs/ANALIZA.md` — dobór, wyniki i granice modelu.
- `docs/PROCES.md` — dodatkowe kontrole dla następnych PCB.
- `docs/ODBIOR.md`, `PRZEGLAD.md` — próby oraz otwarte bramki.
- `simulation/decks`, `simulation/results` — talie SPICE i przebiegi CSV.
- `verification/` — rzeczywisty eksport XML, ERC, testy i obliczenia.

88 elementów,191 końcówek,34 sieci. ERC0 uwag przy zapisanych ustawieniach.
203 kontrole pakietu, w tym9 wykrywanych mutacji. Test dynamiki odrzuca znany
błędny wariant R1. R2 przechodzi zdefiniowane kryteria przesiewowe modelu.
Modele tranzystorów są przybliżone, detektor OVP zastępuje jawne opóźnienie.
Nie jest to gwarancja dla wszystkich egzemplarzy i temperatur ani kwalifikacja automotive.

Następnie: recenzja różnicy R1→R2, mocowanie radiatorów i konkretne części, layout2L,
kontrole produkcyjne i prototyp P01. Brak jeszcze PCB, Gerberów, DRC i pomiarów.
SAFE_N oznacza brak wykrytego błędu, nie gotowe VPROT. W integracji przed KPWR
potrzebny jest stabilny pomiar VPROT — szczegóły w ODBIOR, sekcja7.

## Powtórzenie kontroli

KiCad CLI10.0.6, Python3+numpy, biblioteka ngspice (DLL z KiCad w tej sesji).
Ustaw NGSPICE_LIBRARY na własną bibliotekę, gdy domyślna ścieżka autora nie istnieje.
Programów KiCad/ngspice nie dołączono do archiwum; talie.cir można uruchamiać w CLI.
Użyty solver: ngspice46, build14.04.2026. Dane wersji i skróty wejść w verification/.

```text
kicad-cli sch export netlist --format kicadxml -o verification/P01.xml eda/P01.kicad_sch
kicad-cli sch erc --format json -o verification/erc.json eda/P01.kicad_sch
python src/verify.py
python src/check_package.py
python src/bounds.py
python src/dynamics.py
python src/write_r2_docs.py
python src/check_release.py
```

Nie uruchamiać build_schematic.py po ręcznych zmianach w KiCad, by „naprawić” test.
Model czyta faktyczną XML, nie oczekiwany wynik generatora. `baseline/` oraz
`reference/R1-*` są historyczne, nie stanowią aktualnego projektu.
Jeśli regenerujesz CAD ze źródeł, KICAD_LIBRARY_ROOT wskazuje katalog KiCad
z podkatalogami symbols/footprints. Do samego otwierania projektu nie jest potrzebny.
''')
write('docs/ZMIANY.md','''
# R1 → R2 — decyzje i dowody

| Uwaga | Poprawka | Stan |
|---|---|---|
| R1-01: Q1 otwiera się przy szybkim VS mimo OFF | C5 220n→10n, C6 47n→1µ, R21 4k7→100k, R22 100k→470k, R27 47Ω→10Ω. Q2 PNP→P-MOS, D9 15V. | W CAD/BOM/modelu; rachunek tolerancji i SPICE; stara R1 odrzucona przez test. Do recenzji i pomiarów. |
| R1-02: start PSU maskuje hotplug | Oddzielna próba dołączenia ustalonego napięcia, rzeczywiste zbocze VS i prąd gałęzi Q1. | Nowa sekcja7 ODBIOR: przebiegi, kryteria, AUX OFF, bounce, precharge. Sprzęt niewykonany. |
| R1-03: niepewne PTH pod2,5mm² | J7 Ø2,4→3,2mm, pad5,2→6,0mm; raster7,62 i kotwy12,5 bez zmian. | Większy margines, nadal test rzeczywistej linki i kuponu. Przekrój nie określa średnicy wiązki drutów. |
| R1-04: brak mate BAT | EXT/J_BATA Phoenix1786174 IC2,5/2-ST-5,08 ↔1757019 na H_BAT. | Para potwierdzona na stronie producenta, dodana raz do BOM zewnętrznego. |

Opus prawidłowo wskazał kierunek zmiany C5/C6. Zestaw22n/680n przy ±5% i typowym
Crss dawał około0,835V przy24V wobec celu0,8V; przy48V zapas znikał. Większa C6
z małym Q2 wydłużałaby czas wyłączenia zależny od niegwarantowanego hFE.
R2 rozdziela ten kompromis: mała C5, duża C6, mocny zacisk i dobrane razem R21/R22.

Q2.1=OFF_BASE (historyczna nazwa, teraz bramka), Q2.2=OFF_COL, Q2.3=VS.
D9.K=VS, D9.A=OFF_BASE. Q4 pozostaje PNP EBC. Bez ENABLE R23 włącza Q2,
Q2 przez R27 podciąga GATE do VS. Z ENABLE Q4 wyłącza Q2.
Tab Q2=OFF_COL; nie łączyć z masą, VS ani innym radiatorem. Dla prądów bramki
Q2 nie wymaga radiatora; jego mocowanie i odstępy trzeba uwzględnić w placement.

Złącza zachowują numerację. OVP/UVLO/AUX/SAFE mają te same wartości i połączenia.
`design/changes.json` zawiera jawne zmiany elektryczne wobec zamrożonej bazy.
Nie zmieniano firmware ani innych PCB. P07 nadal HOLD.
''')
tab='\n'.join('| '+x['id']+f" | {x['peak_VSG_V']:.3f} | {x['peak_channel_A']:.3f} | "+(f"{x['off_to_0p5_us']:.2f}" if x['off_to_0p5_us'] is not None else '—')+' |' for x in dyn['results'])
write('docs/ANALIZA.md',f'''
# Dobór i analiza R2

## Części i obliczenia

Q1/Q2 [Vishay SUP53P06-20-E3](https://www.vishay.com/docs/68633/sup53p06-20.pdf):
TO-220 GDS, VDS60V, |VGS|20V, RDS(on) określone również przy4,5V. Napięcie progowe
nie jest napięciem pełnego otwarcia. Ciss3500pF zawiera Crss290pF (wartości typowe).

C5 [TDK B32529C1103J000](https://www.tdk-electronics.tdk.com/inf/20/20/db/fc_2009/B32520_529.pdf):
10nF/100V ±5%, P5mm, obrys7,3×2,5mm, H6,5mm. C6 B32529D1105J000:
1µF/100V ±5%, P5mm, obrys7,8×7,8mm, H13mm. Nie zamieniać bez analizy na MLCC.
R27 [PR02000201009FR500](https://www.vishay.com/docs/28729/pr010203.pdf):10Ω/2W±1%.

Szybki skok VS przy stałym wyjściu daje:
`ΔVSG≈ΔVS·(C5+Cgd)/(C5+Cgd+C6+Cgs)`.
Dla48V, C5+5%, C6−5%, założonego Cgd≤2nF i konserwatywnie pominiętej Cgs:
**VSG≤0,623V**. Cgd2nF jest założeniem do sprawdzenia, nie gwarancją producenta.
Rachunek nie obejmuje dzwonienia indukcyjnego. Cel0,8V dotyczy odbioru prototypu
0…50°C, nie dowolnej temperatury złącza. Rzeczywiste przewodzenie też mierzymy.

DC z niskim wejściem8,9V, spadkami0,95/0,3V i R±1% daje **VSG≈6,29V**.
R22 zwiększono wraz z R21, aby zachować zapas sterowania przy niskim napięciu.
Energia pojemności przy18V około0,173mJ; początkowa moc R27≤32,8W, krótki impuls.
Wykres PR02 str.9 ma zapas dla dziesiątek µs i okres/czas≥100. Odbiór wymaga
zmierzenia impulsu i jego powtarzalności; automatyczne próby zasilania najwyżej1Hz.
R23 przy VS48V i clampie15V: około0,495W, D9 około0,223W. Nie oznacza to dopuszczenia
ciągłego48V dla P01. SOA startu Q1 nie wolno oceniać na podstawie EAS avalanche.

## Zakres modelu

Model czyta z XML połączenia/wartości R17–R27,C5/C6,Q1–Q5,D4/D9. C1=10µF,
Cload=220µF i Rsource=50mΩ są parametrami stanowiska. To nie model instalacji auta.
ENABLE jest sterowane źródłem; w OVP narzucono około20µs opóźnienia detekcji.
Nie symulowano pełnego LM2903/D6/AUX/Q6 ani tłumienia TVS/D2. Odniesienie18,5V
w talii jest źródłem przed Rsource, nie fizycznym pomiarem J1.

Ogólne modele VDMOS/BJT ngspice **nie są modelami producentów wybranych części**.
Badane wartości: Vth0,8…3V,Kp4…20,Cgd0,1…2nF,Cgs2…3,21nF; Q2 Cgs10/20nF,
Cgd3/6nF; BJT BF30…100,TR1/3µs. Są to warianty wrażliwości, nie gwarantowane
granice procesu/temperatury ani pełny iloczyn wszystkich skrajności.
Minimalne wewnętrzne C modeli VDMOS1pF stabilizują solver; raportowany prąd gałęzi
Q1 zawiera ich śladowy składnik. Nie interpretować wyniku bliskiego0 jako zerowego
rzeczywistego upływu. KCL uwzględnia zewnętrzne prądy C5/C6.

Badamy C±5%, zmienione R±1%, oba kierunki kompromisu start/stop, precharge,
bounce,1µs i1ms. Osobny szybki start ma obie C−5%, małe Cgd i duże Kp.
Dla trzech prób zmniejszenie kroku2× zmienia wybrane metryki o<3%.
To kontrola błędu numerycznego, nie weryfikacja fizycznego modelu tranzystora.

## Wyniki modelu

| Próba | VSG szczyt [V] | gałąź Q1 szczyt [A] | wyłączenie [µs] |
|---|---:|---:|---:|
{tab}

Wiersze start dotyczą ON, więc wysokie VSG jest prawidłowe. OFF0/OFF1 liczą
od ENABLE do VSG<0,5V, OVP od źródłowego18,5V z narzuconym opóźnieniem.
Budżet:20µs detektor/bufor +80µs blok bramki =100µs. Te20µs jest wymaganiem
do pomiaru, nie gwarantowanym czasem LM2903. Najwolniejszy badany start osiąga
95%VS w około{max(x['start_to_95pct_ms'] or 0 for x in dyn['results']):.1f}ms po ENABLE.

Regresja R1 przy24V daje w tym modelu VSG{dyn['R1_regression']['peak_VSG_V']:.2f}V
i ładunek około{dyn['R1_regression']['positive_channel_charge_uC']:.0f}µC — znany błąd
zostaje wykryty. Nie wymagamy zgodności prądu z uproszczonym modelem Opusa.

**OVP przy już otwartym Q1 daje duży prąd:**17→24V to około
{rows['ovp_17_24_delay20us']['peak_channel_A']:.0f}A w tym modelu. PASS czasu nie oznacza
PASS tego impulsu. P01 nie ma aktywnego limitu5A. W odbiorze ocenić trajektorię
VDS/ID względem SOA z temperaturą, D2, TVS, ścieżki i bezpiecznik. Model nie
kwalifikuje zwarcia, reverse recovery, termiki ani load dump. Wszystkie pomiary
sprzętowe pozostają NIE ZBADANO. Pełny impuls wymaga opisu amplitudy, czasu,
impedancji i energii, nie samego hasła „48V”.
''')
write('docs/PROCES.md','''
# Proces wykrywający błędy zachowania obwodu

R1 przeszedł ERC, ponieważ zapis wiernie odtwarzał błędny obwód. Zabrakło analizy
prądu pojemności i wydajności drivera w przejściu. Wprowadzamy trzy oddzielne
kontrole: poprawność zapisu, zachowanie elektryczne i pomiar prototypu.

## Kontrakt modułu — jedna strona przed schematem

Wpisać wejścia/wyjścia, stan bez zasilania, domyślne OFF, napięcie/prąd/temperaturę,
obciążenie i pojemność, czasy reakcji oraz punkty pomiarowe. Oznaczać źródło limitu:
GWARANTOWANE, TYPOWE, ZAŁOŻONE lub ZMIERZONE. Typowe hFE nie staje się gwarancją
przy innym prądzie. Każde ważne założenie trafia do konkretnej próby.

P01:5A po termice; start C≤220µF/I≤1,5A, KPWR OFF; prototyp0…50°C; OVP18V,
od VIN18,5V do VGS<0,5V≤100µs. VS48V to limit napięcia resztkowego impulsu,
nie jego specyfikacja ani deklaracja ISO.

## Tabela przejść — obowiązkowa przed PCB

| Przejście | Co trzeba policzyć lub zmierzyć |
|---|---|
| OFF→podłączenie | i=C·dV/dt, dzielnik pojemności zanim AUX/MCU zdąży zadziałać. |
| OFF→ON | Ładowanie wyjścia, obciążenie, VDS/ID/czas i SOA, nie tylko moc średnia. |
| ON→błąd | Q/I, RC, wydajność drivera, storage, osobny czas detektora i odcięcia. |
| Zanik jednej szyny | Prądy przez złącza/diody, zasilanie USB/3V3 nadal obecne. |
| Błąd→powrót | Brak samoczynnego ARM, stabilność zasilania przed KPWR. |
| Odbicia i rozłączanie | Kondensator naładowany, indukcyjność, masa odniesienia. |

P05 dodatkowo: nasycenie, settling ADC, wejście przy wyłączonym zasilaniu.
P07: recyrkulacja, hamowanie/PWM, martwy czas, blokada ECU — po zdjęciu HOLD.

## Obliczenia i model

Najpierw niezależny rachunek skrajności: dzielnik, Q/I, RC, C/L, prąd szczytowy,
napięcie i moc. Potem lokalny model tam, gdzie rachunek nie wystarcza. Sprawdzić
szybki i wolny proces oraz przeciwne tolerancje; pojedyncza zmiana Vth nie jest
pełnym modelem temperatury. Granic nieznanych nie ukrywać w wartościach typowych.

Model pobiera R/C i połączenia z eksportu FAKTYCZNEGO schematu. Zapisywać XML,
hash, talie, parametry, wersję solvera i przebiegi. Brak wektora, błąd zbieżności
lub urwany przebieg oznacza błąd testu. Podwojenie rozdzielczości czasowej sprawdza
numerykę; niezależny rachunek i pomiar sprawdzają sens fizyczny. Pominięcia modelu
mają jawne próby sprzętowe, nigdy automatyczny PASS.

## Regresja każdej znalezionej usterki

ID uwagi → przyczyna → poprawka → test → dowód → status. Stary wariant zostaje
jako negatywna kontrola: test R1-01 musi odrzucać R1 pod tym samym bodźcem.
Kontrole XML celowo zamieniają piny, wartości i MPN w kopiach. Porównanie formuły
z nią samą nic nie sprawdza. Po zmianie C5/Q2 ponawiamy macierz całej bramki,
powiązane czasy i interfejs SAFE, nie cały niezmieniony firmware.

## Zamrożenie i recenzja różnicy

Recenzent dostaje jedną paczkę z hashem, deltę, kryteria i otwarte pozycje.
Ma odtworzyć poprzedni błąd i zbadać wpływ poprawki, nie generować niekończącej
się listy sugestii. Rozdziela błąd, sugestię i brak dowodu. Statusy:
OTWARTE → POPRAWIONE_W_PROJEKCIE → SPRAWDZONE_NIEZALEŻNIE → ZMIERZONE.
NIE_DOTYCZY wymaga uzasadnienia. Druga opinia nie jest pomiarem.

- Do layoutu: zero nierozstrzygniętych błędów schematu, przejścia przeanalizowane,
  recenzja różnicy, konkretne części/mocowania; jawna lista przyszłych pomiarów.
- Do zamówienia: DRC, PCB↔schemat, odczyt Gerberów/wierceń, wydruk1:1 z częściami,
  dostęp do TP, śrub i kotew, przewężenia i powroty prądów.
- Do integracji: sam moduł przeszedł protokół na stole; dopiero potem dołączamy
  kolejny moduł i badamy interfejs oraz zanik jednej szyny.

Dla P01 wystarczą lokalne obliczenia/model, recenzja i dobrze określone pomiary.
Żaden zielony raport nie zastępuje następnego etapu. Nie obiecujemy projektu bez
wszelkich błędów; tworzymy powtarzalny sposób znajdowania ich przed kolejnym kosztem.
''')
write('docs/PRZEGLAD.md','''
# Ponowny przegląd R2

Autor ponownie sprawdził Q1/Q2 GDS i D9, domyślny OFF, Q4 PNP, poziom ON,
prąd/energię bramki, start/stop, wpływ na SAFE, MPN, footprinty i wiązki.
To NIE JEST niezależna recenzja R2. Opus oceniał R1, nie tę poprawkę.

| ID | Stan | Do zamknięcia |
|---|---|---|
| R1-01 | POPRAWIONE_W_PROJEKCIE | Recenzja nowego toru, następnie hotplug/OVP na stole. |
| R1-02 | POPRAWIONE_W_PROJEKCIE | Odbiór protokołu, pomiar rzeczywistych zboczy. |
| R1-03 | POPRAWIONE_W_PROJEKCIE, fit otwarty | Przewód w PTH3,2 bez obcinania drutów; lut poprawnie zwilżony. |
| R1-04 | DOBÓR_ZAMKNIĘTY | Para1757019↔1786174 u producenta; przy montażu pin1/oznaczenia. |
| E-02 | OTWARTE przed layoutem | Niezależna recenzja delty Q2/C5/C6/D9 oraz granic modelu. |
| M-01 | OTWARTE przed layoutem | Rysunek mocowań dwóch radiatorów, miejsca na większy Q2 i C6. |
| B-01 | OTWARTE przed layoutem | MPN/dostępność/gabaryty, zwłaszcza H4,C1,C6 i próbka przewodu. |
| L-01 | NIE WYKONANO | Layout2L, DRC, Gerbery, wiercenia. |
| H-01 | NIE WYKONANO | Pełne100µs, dV/dt, SOA przy starcie/OVP, termika i reszta ODBIOR. |
| P07 | HOLD | Czekamy na moduł BTS7960. |

Recenzent: sprawdzić granice parametrów modelu, wyłączenie Q2 przez Q4 i budżet
detektor→ENABLE. Oddzielnie ocenić duży prąd przy OVP z Q1 już włączonym.
Nie zmieniać progów testu, aby dostać PASS. Zachować każdy niezaliczony przypadek.

`verification/legacy-static-model.json` używa STARYCH wartości bramki, nie jest
dowodem nowych czasów ani napięcia ON. Detektor/AUX/SAFE pozostały takie same
(XML). Nowe DC bramki jest w bounds.json, dynamika w dynamics.json.
''')
a=old('ODBIOR.md').replace('P01-R1','P01-R2')
a=a.replace('obowiązują korekty wykonawcze R1: Q2/Q4=2N5401YBU, C7/C9=50 V, R27=2 W.',
 'obowiązuje BOM R2: Q2=SUP53P06-20-E3 (GDS), Q4=2N5401YBU (EBC), D9=15 V,\nC5=10 nF, C6=1 µF, R21=100 kΩ, R22=470 kΩ, R27=10 Ω/2 W, C7/C9=50 V.')
a=a.replace('E-B-C Q2...Q8','G-D-S Q1/Q2 oraz E-B-C Q3...Q8').replace('D2/D3/D4/D5/D6','D2/D3/D4/D5/D6/D9')
a=a.replace('Sprawdź również start z 18-24 V:','Sprawdź również start z 19-24 V:')
a=a.replace('150-700 ms plus czas narastania AUX5.','150-700 ms plus czas narastania AUX5 i narastanie VPROT po ENABLE (do300ms według sekcji7).')
i=a.index('## 7.');j=a.index('## 8.',i)
write('docs/ODBIOR.md',a[:i]+'''## 7. Dynamika — protokół R2 zastępujący sekcję R1

Zapis każdej próby: PCB/BOM, temperatura, Cload, obciążenie, napięcie, impedancja
i ograniczenie energii źródła, rzeczywiste zbocze VS, sondy/pasmo/offset, przebieg.
Powtórzyć w0/25/50°C bez kondensacji. Najpierw bez P02/P07/silnika, Cload220µF
ŁĄCZNIE z C3. Zaczynać od mniejszej energii i napięcia.

Zasilacz już pracuje na ustalonym napięciu; osobny przełącznik/fixture podaje je
na układ. OUTPUT zasilacza jest inną próbą. COMBICON nie służy do łączenia pod
obciążeniem. Nie używać auta jako generatora przepięć.

Rejestrować VS, **VGS różnicowo bezpośrednio G–S Q1**, VPROT i prąd gałęzi Q1.
Masy oscyloskopu nie podłączać do SOURCE. Sonda różnicowa albo skompensowane
kanały względem GND z ocenionym błędem odejmowania. Prąd: sonda lub bocznik
w gałęzi Q1, nie całkowity prąd wejściowy (C1/AUX pobierają normalny impuls).
Stanowisko nie może istotnie spowalniać zbocza. Minimum10MS/s, pasmo10MHz,
efektywna rozdzielczość VGS≤0,1V; podać granicę detekcji prądu/ładunku.

1. **OFF/hotplug:** J3 zwarte;0→14V i0→24V, zbocza VS około1µs i1ms. Powtórzyć
   z wcześniej odłączonym AUX (U1/R1). Najpierw wyjście rozładowane, potem18→30V
   z VPROT naładowanym do17V przez odłączone źródło. VSG≤0,8V, bez utrzymującego
   się przewodzenia. Dla rozładowanego220µF: wzrost VPROT≤0,1V w pierwszych200µs,
   dodatni ładunek gałęzi Q1≤10µC po ocenie offsetu i displacement. Gdy pomiar
   tego nie rozróżnia: NIE ROZSTRZYGNIĘTO, nie PASS. Powtórzyć kontrolowane odbicia.
   OFF po10ms i1s z1kΩ: VPROT≤0,2V; upływ może ładować nieobciążony kondensator.
2. **48V:** dopiero po niższych napięciach, jako krótki impuls z określonym
   kształtem, impedancją i energią dopuszczalną dla TVS. Mierzyć rzeczywiste VS
   (≤48V), nie zakładać go z nastawy przed D1/D2. Te same kryteria VSG, zapis
   VPROT. Bez specyfikacji generatora próba pozostaje NIE ZBADANO. Nie stałe48V.
3. **Start:** VIN10,5/13,8/16V, C≤220µF, Iload0/0,1/1,5A, KPWR OFF. Szczyt≤5A
   jest kryterium testu, nie aktywnym limitem. VPROT≥95%VS w≤300ms po ENABLE;
   ustalone |VGS|≥4,5V. Zapis ID/VDS/czas i porównanie SOA z temperaturą Q1.
   Nie wystarczy ½CV² ani znamionowe53A.
4. **Wyłączenie:** wymusić J3 i zanik AUX: ENABLE→|VGS|<0,5V≤80µs. OVP14→24V:
   od VIN na J1 przekraczającego18,5V do |VGS|<0,5V≤100µs. Osobno detektor/bufor
   ≤20µs i bramka≤80µs. Przekroczenie podbudżetu wymaga analizy, nie zmiany
   punktu początku czasu. Obserwować SAFE_N i prąd; duży impuls przed odcięciem
   trzeba ocenić pod względem SOA/D2/TVS/źródła także przy czasie<100µs.
5. **Powrót:** brak oscylacji, spokojny start, ARM ponownie tylko fizycznie.
   SAFE_N zwalnia po ENABLE zanim VPROT się ustali. Przed KPWR wymagany pomiar
   VPROT w zakresie dopuszczenia następnego modułu, stabilny przez≥300ms.
   Sam SAFE_N nie wystarczy, zwłaszcza przy CORE z USB. To wymaganie integracyjne
   do sprawdzenia na P04/P07; firmware nie był zmieniany w pakiecie P01.

Automatyczne powtórzenia odbioru najwyżej1Hz. VPROT nie musi spaść do zera w100µs;
pozostaje energia kondensatorów. Wynik zawsze przypisać do właściwego stanu i czasu.

'''+a[j:])
write('docs/WIAZKI.md',old('WIAZKI.md').replace('PTH Ø2,4 mm','PTH Ø3,2 mm')+'''

## R2: komplet BAT

EXT/J_BATA = **Phoenix1786174 IC2,5/2-ST-5,08**, styki męskie, zaciski śrubowe,
po stronie źródła ZA bezpiecznikiem5A. H_BAT ma żeńskie1757019.
[Producent1757019 wymienia1786174 jako mate](https://www.phoenixcontact.com/en-us/products/pcb-plug-mstb-25-2-st-508-1757019).
Stronę źródła osłonić i zamocować w obudowie, nie pozostawiać luźnych odsłoniętych
pinów. Rozłączać/montować bez zasilania (złącze nie jest łącznikiem mocy).
Pin1=plus po F1,2=GND; sprawdzić numery komór obu części, nie widok od lewej.
Dwie tulejki EXT są osobne od tulejek H_BAT, ujęte raz w BOM-MECHANIKA.
J7: padØ6mm/otwórØ3,2mm; przed PCB próbka rzeczywistej linki i kupon. Nie obcinać
drutów, żeby weszły; po lutowaniu sprawdzić zwilżenie. Kotwy pozostają12,5mm.
''')
fp=old('FOOTPRINTY.md').replace('| C2/C4/C6 | TDK B32529, obrys7,3×2,5mm, raster5mm; C5 obrys7,3×3,5mm. |','| C2/C4/C5 | TDK B32529, obrys7,3×2,5mm, P5. |\n| C6 | B32529D1105J000: obrys7,8×7,8, H13mm, P5. |').replace('| Q1/D2 |','| Q1/Q2/D2 |').replace('| Q2–Q8 | TO-92 wide, E-B-C; Q2/Q4 tylko wybrany bondout YBU bez -C. |','| Q3–Q8 | TO-92 wide EBC, Q4 YBU bez -C. Q2 teraz TO-220 GDS. |').replace('D4/D6–D8','D4/D6–D9')
write('docs/FOOTPRINTY.md',fp+'\nR2:J7 PTH3,2/pad6,0/P7,62; Q2 jak Q1; D9 DO-35 K1/A2.\n')
write('mechanical/MECHANIKA.md',old('MECHANIKA.md').replace('P01-R1','P01-R2')+'''

R2: blok drivera musi zmieścić TO-220 Q2 i C6 obrys7,8×7,8/H13mm. Q2 bez
radiatora, tab=OFF_COL. Rysunek stref nie dowodzi zmieszczenia elementów.
Pętla Q2–R27–Q1–VS lokalna; D9 przy G/S Q2, bez przedłużania wiązką.
J7 ma większe pady/otwory; uwzględnić przewężenia toru5A i kotwy przy placement.
''')
write('mechanical/P01-strefy.svg',old('P01-strefy.svg').replace('/ R1','/ R2').replace('Q2 / D4 / C5 / C6','Q2 TO-220 / D9 / C5-C6'))
with (P/'docs/BOM-MECHANIKA.csv').open('w',encoding='utf-8-sig',newline='') as f:
 base=list(csv.reader((P/'reference/R1-docs/BOM-MECHANIKA.csv').open(encoding='utf-8-sig'),delimiter=';'))
 w=csv.writer(f,delimiter=';');w.writerows(base);w.writerows([
 ['EXT/J_BATA Phoenix1786174 IC2.5/2-ST-5.08','1','Za F1; mate1757019; osłonić/zamocować, bez dodatkowej PCB'],
 ['EXT/J_BATA tulejka2.5mm2 dobrana do zacisku','2','Osobne od H_BAT']])
group={}
for p in parts.values():
 if p['mpn'].startswith(('PCB','Tinned')):continue
 g=group.setdefault(p['mpn'],{'Nazwa':p['display'],'MPN':p['mpn'],'Ilosc_szt':0,'Oznaczenia':[],'Zrodlo':p['url']});g['Ilosc_szt']+=1;g['Oznaczenia'].append(p['ref'])
with (P/'docs/ZAKUPY.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,['Nazwa','MPN','Ilosc_szt','Oznaczenia','Zrodlo'],delimiter=';');w.writeheader()
 for g in group.values():g['Oznaczenia']=', '.join(g['Oznaczenia']);w.writerow(g)
write('verification/QA.md',f'''
# R2: zakres kontroli

- XML88 elementów/191 końcówek/34 sieci; zgodność bazy+jawnej delty.
- ERC0 naruszeń; domyślnie pominięte kategorie wyszczególnione werc.json.
- Pakiet203 kontrole,9 wykrywanych mutacji.
- Dynamika{len(dyn['results'])} scenariuszy R2, regresja R1,3 porównania kroku;
  łącznie{len(dyn['checks'])} kryteriów PASS. Dwa rachunki w bounds.json.
- PDF: kontrola wizualna zapisywana po finalnym eksporcie.
- Niezależna recenzja R2, layout, DRC i sprzęt:NIE WYKONANO.

PASS modelu nie zamyka sprzętu ani SOA/termiki poza zakresem modelu.
''')
print('R2 documents generated')
