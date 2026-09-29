"""Current documentation from frozen R2 and current generated tables/results."""
from pathlib import Path
import csv,json
P=Path(__file__).resolve().parents[1]
def write(f,t):(P/f).write_text(t.strip()+'\n',encoding='utf-8')
def old(f):return (P/'reference/R2-docs'/f).read_text(encoding='utf-8')
parts=json.loads((P/'docs/parts.json').read_text(encoding='utf-8'))
dyn=json.loads((P/'verification/dynamics.json').read_text())
rec=json.loads((P/'verification/recovery.json').read_text())

write('README.md','''
# P01 PROTECT R3 — poprawki przed layoutem

23.09.2026. Nowy pakiet po recenzji R2; R1/R2 i system 6.1 pozostają niezmienione.
**Projekt schematu i przygotowanie do layoutu. Nie ma jeszcze produkcyjnej PCB ani pomiarów prototypu.** P07: HOLD.

Zmiany elektryczne P01: rozłączalny LK1 w drenie Q1, z dostępem Kelvina.
C6 zmieniono na dostępny WIMA 1µF/100V/±5%; wartości RC i zabezpieczenia zachowano.
H_BAT ma teraz męski 1786174, a przewód od źródła żeński 1757019.
Radiatory dobrano jako SK129-63STS z lokalnym footprintem; J7 ma termiki.

## Pliki do pracy

- `eda/P01.kicad_pro` — trzy arkusze i lokalne biblioteki.
- `output/pdf/P01-R3-schemat.pdf` — aktualny schemat do przeglądania.
- `docs/ZMIANY.md` — zamknięcie każdej uwagi i pozostałe próby fizyczne.
- `docs/BOM.csv`, `ZAKUPY.csv`, `BOM-MECHANIKA.csv`, `ZAKUPY-NOWE.md` — części.
- `docs/METROLOGIA.md`, `ODBIOR.md` — przyrządy, niepewność i procedura.
- `mechanical/MECHANIKA.md` — radiator, termiki, punkty pomiarowe, montaż.
- `integration/P02-HOLD/` — ustalony kontrakt oraz obwód podtrzymania do P02;
  to dodatek do przyszłego projektu P02, nie zatwierdzona kompletna płytka P02.
- `verification/` — wyniki testów; `simulation/` — talie i przebiegi.
- `docs/PROCES.md` — obowiązkowa kontrola powrotu po usterce i wykonalności pomiarów.

Do rozpoczęcia layoutu używać tej rewizji i jej delty. Przymiarka realnych części
i kontrola gotowego rozmieszczenia są konieczne przed Gerberami. Podtrzymanie P02
nie zmienia złącza ani limitu pojemności widzianej bezpośrednio przez P01.

## Odtworzenie weryfikacji

KiCad CLI 10, Python z numpy, ngspice DLL. Ustaw `NGSPICE_LIBRARY` na bibliotekę
ngspice, a tylko przy regeneracji CAD `KICAD_LIBRARY_ROOT` na share/kicad.
Nie regeneruj schematu po ręcznych edycjach, aby wymusić przejście testów.

```text
kicad-cli sch export netlist --format kicadxml -o verification/P01.xml eda/P01.kicad_sch
kicad-cli sch erc --severity-all --format json -o verification/erc.json eda/P01.kicad_sch
python src/verify.py
python src/check_package.py
python src/bounds.py
python src/dynamics.py
python src/recovery.py
python src/hold_budget.py
python src/write_r3_docs.py
python src/check_release.py
python src/check_r3.py
```

Modele tranzystorów są przybliżone. Raporty rozdzielają pozytywne kryteria,
oczekiwane wykrycie zaniku zasilania oraz wyczerpanie rezerwy. PASS nie jest
potwierdzeniem SOA, odporności automotive ani działania konkretnego egzemplarza.
''')

write('docs/ZMIANY.md','''
# R2 → R3 — mała delta i sposób zamknięcia uwag

| Uwaga | Wprowadzona zmiana | Dowód / dalszy odbiór |
|---|---|---|
| R2-01, przerwa 10–27ms po krótkim błędzie | Ustalono rozdział: P01 chroni i wyłącza silnik, P02 podtrzymuje pomiary. Kontrakt 50ms/6W na wejściu przetwornic, obwód 3×22000µF przez ładowanie rezystorowe i diody. | recovery.json i hold-budget.json. Rzeczywiste P02 i pomiary jeszcze przed nami. |
| R2-02, mierzalność | LK1 przed całym VPROT, pola siłowe i Kelvin; rozdzielenie prób małego ładunku i dużego prądu. Budżet niepewności i reguły PASS/FAIL w METROLOGIA. | XML, footprint, test obejścia LK1; odbiór stanowiska przed oceną PCB. |
| R2-02, powerbank | Nie stosować masy DHO804 na SOURCE. Pozostać przy właściwym pomiarze różnicowym i uziemieniu zgodnym z instrukcją Rigola. | Instrukcja DHO800 §1.1. |
| R2-03, BAT | Zamieniono strony 1757019/1786174 we wszystkich bieżących dokumentach wiązki i BOM. | Brak zmiany pinów J7: 1=BAT_FUSED, 2=GND. |
| R2-04, C6 | WIMA MKS2D041001K00JO00, 1µF/100V/±5%, P5, korpus 7,2×7,2/H13mm. | Karta WIMA, oferta detaliczna TME, footprint i ponowne scenariusze RC. |
| R2-05, J7/TP | Termiki 1,2mm/gap0,3; radiator SK129-63STS z footprintem P25,4/D2,8; wymogi lokalizacji TP1/TP2 i LK1. | Właściwe rozmieszczenie oraz wypełnienie miedzi do sprawdzenia w layout/DRC. |

Q1.2 i tab Q1 to teraz **P01_Q1_DRAIN**. LK1.1=DRAIN, LK1.2=VPROT.
Wszystkie wcześniejsze odgałęzienia VPROT, w tym C5, pozostają za LK1.
LK1 nie jest zworą logiczną ani elementem do przełączania pod obciążeniem.
Zachowano Q2 P-MOS, D9, C5/C6 nominalnie, R21/R22/R27 i cały tor AUX/OVP/UVLO/SAFE.
`design/changes.json` to pełna jawna delta względem zamrożonej bazy 6.1;
`verification/r3-checks.json` sprawdza osobno wąską różnicę względem XML R2.

Znany błąd R1 dalej jest wykrywany. Nie wracamy do jego szybszego restartu.
Uzupełnienie testu powrotu ujawniło, że przypadek Vth=1V nie zawsze traci zasilanie:
to zależy także od zacisku Q2 i długości impulsu. Pierwsza zbyt szeroka asercja
„każdy przypadek spada poniżej 7V” była błędem oczekiwania testu. Wynik zachowano
w recovery-initial-expectation.json. Nie zmieniono progów ochrony P01; wymaganie
jest konkretne: wykryć przypadki utraty zasilania bez rezerwy i sprawdzić bufor
w określonej dziedzinie. Wyniku modelu nie uogólniać na wszystkie egzemplarze.
''')

table='\n'.join('| '+r['id']+f" | {r['peak_VSG_V']:.3f} | {r['peak_channel_A']:.3f} | "+(f"{r['off_to_0p5_us']:.2f}" if r['off_to_0p5_us'] is not None else '—')+' |' for r in dyn['results'])
rt='\n'.join('| '+r['id']+f" | {r['bus_min_V']:.3f} | "+('TAK' if r['bus_below_7V'] else 'NIE')+' |' for r in rec['results'])
write('docs/ANALIZA.md',f'''
# R3 — obliczenia i granice

C5=10nF±5%, C6=1µF±5%, R21=100k, R22=470k, R27=10Ω/2W. C6 WIMA ma takie same
wartość i tolerancję jak poprzednia TDK; obrys nowej części jest 7,2×7,2mm.
Nie zatwierdzono automatycznie zamienników ±10%. Źródła: reference/WIMA_MKS2.pdf,
reference/sources.json. WIMA podaje 15V/µs dla tej pojemności/napięcia; w próbach
ocenić dV/dt na samym C6, nie utożsamiać go ze zboczem VS.

Rachunek podłączenia przy założonym Cgd≤2nF daje VSG≤0,6234V przy 48V.
Cgd to obwiednia inżynierska do weryfikacji, nie gwarantowane maksimum producenta.
LK1 ma w modelu 0,2mΩ; jego rzeczywisty opór i indukcyjność wynikną z wykonania.
Prąd kanału Q1 w modelu i prąd całej gałęzi zmierzony na LK1 są różnymi wielkościami.

| Scenariusz | VSG peak [V] | I kanału peak [A] | wyłączenie [µs] |
|---|---:|---:|---:|
{table}

## Powrót i obciążenie stałej mocy

Model odbiornika odłącza pobór poniżej 6,5V. Nie modeluje wewnętrznego UVLO,
zapasów regulatora ESP ani pracy karty SD. Przypadki powrotu z HOLD zaczynają
się z naładowaną rezerwą; oddzielny hold_cold_start sprawdza start z0V i ładowanie
przy C+20%/R+5%. Pojemność bezpośrednio widziana przez P01:198µF+22µF=220µF.

| Scenariusz | minimum szyny odbiorników [V] | spadek poniżej 7V |
|---|---:|---|
{rt}

HOLD ma jawny budżet: 6W na wejściu przetwornic, Ceff≥52,8mF, początek≥9,5V,
łączny spadek gałęzi≤1,2V, szyna≥7V. Rachunek daje około85ms wobec wymogu50ms.
To warunkowy zapas obliczeniowy. Minimalne Ceff, spadek, upływ i pobór podlegają
odbiorowi w0/25/50°C. Czas nie oznacza gwarantowanego dokończenia zapisu SD.

## OVP, SOA, temperatura

Duży prąd w talii OVP pochodzi ze sztywnego źródła i ładowania220µF.
Modele bramki nie zawierają pełnej charakterystyki TVS i źródła samochodowego.
Nie uznajemy wyniku energii modelu za zamknięcie SOA. D3=5KP18A: VBR20–22,1V
przy5mA, VC max29,2V przy174,7A; nie zakładamy idealnego ograniczenia do21V.
Oceniać jednocześnie ID, VDS, czas, temperaturę, D2, D3 i impedancję źródła.
Źródło: https://www.littelfuse.com/assetdocs/littelfuse_tvs_diode_5kp_datasheet.pdf?assetguid=b1ddd6a2-fccb-4327-bea1-7d77c0793479

Rth radiatora4,5K/W odnosi się do warunków producenta. Dla Q1 przy5A i przyjętym
gorącym RDS≤50mΩ moc≤1,25W. D2 liczymy zachowawczo do5W; przy otoczeniu50°C
sam radiator wzrósłby o22,5°C. Dodać izolator, przejście złącze-obudowa i wpływ
obudowy. Pomiar wymagany: Tc<85°C, oszacowane Tj<110°C. Radiatory nie dowodzą
dopuszczalności zwarcia ani liniowej pracy Q1 podczas narastania.
''')

text=old('WIAZKI.md');text=text[:text.index('## R2: komplet BAT')]
# All historical occurrences of 1757019 on the module side are changed here.
text=text.replace('1757019','1786174').replace('MSTB 2,5/2-ST-5,08','IC 2,5/2-ST-5,08').replace('P01-R1','P01-R3').replace('P01-R2','P01-R3')
write('docs/WIAZKI.md',text+'''
## R3: BAT

H_BAT przy P01: **1786174 IC2,5/2-ST-5,08**, styki męskie.
EXT/J_BATA przy akumulatorze, za bezpiecznikiem: **1757019 MSTB2,5/2-ST-5,08**,
styki żeńskie. Nie zmieniać numerów pinów:1=plus po F1,2=GND. Orientację sprawdzić
po numerach komór obu wtyków, nie po widoku od lewej. Obie części z tulejkami2,5mm².
Złącze rozłączać bez obciążenia; część źródłową osłonić i zamocować.
J7: PTH3,2mm/pad6mm/raster7,62mm; gotowa wiązka200mm, kotwy12,5mm od lutów.
H_PG:200mm,6×AWG22, PTH po stronie P01, Mini-Fit Jr6p po stronie P04.

Potwierdzenie pary: https://www.phoenixcontact.com/en-us/products/pcb-plug-mstb-25-2-st-508-1757019
''')

fp=old('FOOTPRINTY.md').replace('P01-R2','P01-R3').replace('B32529D1105J000: obrys7,8×7,8','MKS2D041001K00JO00: obrys7,2×7,2')
write('docs/FOOTPRINTY.md',fp+'''

R3: LK1 ma dwa pola mocy P10/Ø2,4/pad4,8 oraz dwa Kelvin Ø1/pad2.
Pola1=(0,0) i(2,5;3), pola2=(10,0) i(7,5;3)mm. Dodatkowe pola nie przenoszą prądu.
LK1.1 i LK1.2 nie mogą być połączone ścieżką ani poligonem omijającym zworę.
Mostek ma być zdejmowany przez odlutowanie. Nie zakładać przewodu na polach sense.

HS1/HS2 są elementami mechanicznymi do dodania podczas layoutu:
`P01:HS_Fischer_SK129_63.5_STS_D2.8`, P25,4, otwory2,8mm pod kołki max2,3mm.
Kołki połączone z metalem radiatora, pady pozostają odizolowane od sieci elektrycznych.
Nie używać jako punktu GND. Nominalny obrys42×25mm, wysokość63,5mm plus prześwit.
''')

write('mechanical/MECHANIKA.md','''
# P01 R3 — wykonanie mechaniczne do layoutu

PCB160×100mm,2L,FR4 1,6mm,Cu70µm. Mocowania NPTHØ3,2:(5,5),(155,5),(5,95),(155,95).
Wokół mocowań Ø8mm bez miedzi i elementów. To założenia layoutu, nie Gerbery.

## HS1/HS2

Dwa **Fischer SK129-63STS**, pionowo, L63,5mm, profil42×25mm, Rth4,5K/W.
Wybrano STS z kołkami, nie niedostępny STIS. Źródło wymiarów: rysunek producenta
001020452 w reference/Fischer_SK129_STS.pdf. KołkiØ≤2,3mm, raster25,4mm,
wystają≤4,5mm. Footprint lokalny daje Ø2,8mm/pad4,8mm. Zostawić wolny obrys
46×30mm i wysokość75mm. Pady kołków są odizolowane od wszystkich sieci.

Tranzystor/dioda na środkowym żebrze, otwór na wysokości13,5mm od dolnej krawędzi
radiatora. Pozostałe fabryczne otwory18,3/25,4mm nie są otworami PCB.
Użyć M3×10, podkładki, nakrętki, izolatora TO-220 i tulejki dopasowanej do M3.
Izolator≤0,3mm; cienka pasta przy mice zgodnie z instrukcją izolatora.
Nie traktować anodowania jako izolacji. Po skręceniu sprawdzić izolację tab–radiator.

Nominalnie środek D2/Q1 względem środka HS jest x=0; płaszczyzna tab przy przedniej
powierzchni żebra. Footprint TO-220 ma tył obudowy y=-3,15mm od rzędu padów;
przy żebrze+0,9mm i izolatorze0,25mm wstępna pozycja rzędu padów wynosi y=4,30mm,
a pad1 x=-2,54mm względem osi radiatora. To wymiar montażowy do potwierdzenia
na rzeczywistym komplecie, nie tolerancja gwarantowana przez model KiCad.
Najpierw skręcić element z radiatorem, dopiero potem lutować wyprowadzenia bez
naprężeń. Niewielkie formowanie nóg jest dopuszczalne z dala od korpusu.
Radiatory opierają się na PCB i własnych kołkach; w obudowie dodać obejmę/podparcie
izolacyjne przeciw drganiom. Nie mogą wisieć na nogach półprzewodnika.

## Miedź i lutowanie

J7: cztery szprychy na warstwę, szerokość1,2mm, szczelina0,3mm. Ustawienia zapisano
w footprintcie. Przy wypełnieniu obu warstw sprawdzić, że wszystkie szprychy rzeczywiście
powstały i nie ma przewężeń. Wypadkowy przekrój8×1,2×0,07=0,672mm² na krótkim odcinku;
nie zastępuje to odbioru termicznego całej ścieżki. Lutować grotem o dużej pojemności
cieplnej; możliwość podgrzania PCB pozostaje. Nie obcinać żył dla dopasowania do PTH.

Tor mocy: szerokie pola, korytarz początkowo≥5mm na obu warstwach; ocenić także
przewężenia przy TO-220 i LK1. LK1: zwora z linki/drutu Cu2,5mm², odcinek około20mm,
uformowana P10, pozostawiona dostępna od góry. Trwały opór połączenia zmierzyć
czteroprzewodowo, docelowo≤0,5mΩ. Model przyjmuje0,2mΩ; bez weryfikacji nie
przypisywać mu dowolnej obciążalności impulsowej.

TP1 i TP2 umieścić przy nóżkach S/G Q1, docelowo≤5mm ścieżki. Para sense LK1
odchodzi od wewnętrznych brzegów padów mocy; nie pobiera prądu odbiorników.
Brak odgałęzienia VPROT przed LK1. Pętla Q2–R27–GATE–SOURCE krótka, C5/C6/D4
lokalnie. R1/R23 uniesione3mm i odsunięte od TL431/dzielników. D1 przy BAT,
D3 przy wyjściu, powrót ich prądów poza masą pomiarową komparatorów.

Wiązki: PTH i kotwy12,5mm od lutów; pas do opaski pusty. Przed Gerberami sprawdzić
wydruk1:1 i realne części. Kontrola radiatorów jest teraz określona wymiarowo;
przymiarka i ocena zamkniętej obudowy pozostają czynnościami fizycznymi.
''')

write('docs/ZAKUPY-NOWE.md','''
# Zakupy zmienione względem R2

Sprawdzenie ofert23.09.2026; stan magazynu nie jest rezerwacją.

| Element | Na urządzenie | Zamówienie / uwaga |
|---|---:|---|
| WIMA MKS2D041001K00JO00,1µF/100V/±5% |1| TME pokazywało1364szt., cenę od2szt.; zamówić2, druga zapas. |
| Fischer SK129-63STS |2| TME pokazywało389szt., MOQ1. |
| Phoenix1757019 |1| Ten sam komplet co R2, ale teraz przy źródle. |
| Phoenix1786174 |1| Ten sam komplet co R2, ale teraz na H_BAT. |
| Cu2,5mm² na LK1 |1 odcinek| około20mm przed formowaniem, bez cynowania całej giętej części. |
| M3×10 + podkładka + nakrętka |2 komplety| Izolatory TO-220 i tulejki M3 liczone oddzielnie,2komplety. |

C6: https://www.tme.eu/pl/details/mks2-1u_100-5%25-r/kondensatory-foliowe-tht/wima/mks2d041001k00jo00/
Radiator: https://www.tme.eu/en/details/sk129-63sts/heatsinks/fischer-elektronik/

Nie kupować C6 z tolerancją10% jako automatycznego zamiennika. Zakupy P02-HOLD
są w jego oddzielnym BOM; nie dodano tych elementów do P01.
''')

rows=list(csv.reader((P/'reference/R2-docs/BOM-MECHANIKA.csv').open(encoding='utf-8-sig'),delimiter=';'))
for row in rows[1:]:
 if row[0].startswith('H_BAT / wtyk'):row[0]='H_BAT / wtyk Phoenix1786174 (męski)'
 if row[0].startswith('EXT/J_BATA Phoenix'):row[0]='EXT/J_BATA Phoenix1757019 MSTB2.5/2-ST-5.08 (żeński)';row[2]='Przy źródle za F1; mate1786174; osłonić i zamocować'
 if row[0].startswith('Radiator Fischer'):row[0]='Radiator Fischer SK129-63STS';row[2]='2 osobne; footprint HS_Fischer_SK129_63.5_STS_D2.8; przymiarka przed Gerberami'
 if row[0].startswith('Śruba M3 +'):row[0]='Śruba M3x10 + podkładka + nakrętka do TO-220';row[2]='Montaż z izolacją wg MECHANIKA; potwierdzić prześwit i długość tulejki'
rows.append(['LK1 / drut Cu2.5mm2 około20mm','1','Zwora zdejmowana przez odlutowanie; nie doliczać rezystora'])
with (P/'docs/BOM-MECHANIKA.csv').open('w',newline='',encoding='utf-8-sig') as f:csv.writer(f,delimiter=';').writerows(rows)

group={}
for p in parts.values():
 if p['mpn'].startswith(('PCB','Tinned','Copper')):continue
 g=group.setdefault(p['mpn'],{'Nazwa':p['display'],'MPN':p['mpn'],'Ilosc_szt':0,'Oznaczenia':[],'Zrodlo':p['url']});g['Ilosc_szt']+=1;g['Oznaczenia'].append(p['ref'])
with (P/'docs/ZAKUPY.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,['Nazwa','MPN','Ilosc_szt','Oznaczenia','Zrodlo'],delimiter=';');w.writeheader()
 for g in group.values():g['Oznaczenia']=', '.join(g['Oznaczenia']);w.writerow(g)

interfaces=list(csv.DictReader((P/'baseline/interfejsy.csv').open(encoding='utf-8-sig'),delimiter=';'))
interfaces=[r for r in interfaces if r['lacze'] in ['BAT','PG','SUPPLY']]
for row in interfaces:
 for key in ['koniec_A','koniec_B','koniec_lutowany']:
  row[key]=row[key].replace('P01/J_PGB','P01/J5').replace('P01/J_SUPPLYA','P01/J6').replace('P01/J_BATB','P01/J7')
 row['wersja']='P01-R3';row['kotwa_mm']='12.5'
 if row['lacze']=='BAT':row['typ_wtyku']='H_BAT:1786174 meski; EXT:1757019 zenski'
with (P/'docs/interfejsy.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,interfaces[0].keys(),delimiter=';');w.writeheader();w.writerows(interfaces)

hold_bom=[['Oznaczenie','Nazwa','MPN','Ilosc_szt','Uwagi'],
 ['C_H1-C_H3','22000uF 35V SNAP-IN','HC1V229M35045HA','3','P10; body35x45; Ceff/ESR do pomiaru w0..50C'],
 ['D_OR,D_CHARGE','Schottky podwojna 100V TO220','STPS20100CT','2','D_OR oddzielne anody; D_CHARGE anody zwarte'],
 ['R_CHARGE','47R 25W 5% przykrecony','HSA2547RJ / TE 5-1625971-1','1','Osobna blacha chlodzaca wg karty; nie przy banku'],
 ['R_BLEED','4k7 0.5W 1%','MFR-50FTE52-4K7','1','Powolne rozladowanie, zmierzyc przed serwisem'],
 ['C_BUS','22uF 50V','EEUFR1H220','1','Pojemnosc liczona do budzetu P01'],
 ['F_HOLD','Bezpiecznik T2A DC + oprawa','Dobor DC/I2t przy odbiorze P02','1 komplet','Przy banku; nie dodano do zakupow P01'],
 ['H_HOLD','Wiazka150mm 3xAWG18 PTH -> MSTB3p','P02:1757022; header1757255','1 komplet','Próby stołowe; 1=VPROT,2=GND,3=VLOG_RES; kotwy12.5mm; kodowanie względem SUPPLY do zamknięcia w projekcie P02'],
 ['MECH','Mocowanie banku i rezystora','wg gabarytow w PROJEKT','1 komplet','Oslony zaciskow i podparcie kondensatorow']]
with (P/'integration/P02-HOLD/BOM.csv').open('w',newline='',encoding='utf-8-sig') as f:csv.writer(f,delimiter=';').writerows(hold_bom)
write('integration/P02-HOLD/ZRODLA.md','''
# Źródła i zakup części obwodu HOLD

- [SAMWHA HC, producent](https://www.tme.eu/Document/52dbc9ab47efa879b9859910ffff5ecc/hc.pdf): pojemność±20%, gabaryty, upływ.
- [Oferta HC1V229M35045HA](https://www.tme.eu/en/details/hc1v229m35045ha/snap-in-electrolytic-capacitors/samwha/):23.09.2026 pokazywała270szt., MOQ1.
- [STPS20100CT, producent](https://www.st.com/resource/en/datasheet/stps20100c.pdf): pinoutAKA, napięcia, straty; ten sam typ co D2 P01.
- [TE HSA2547RJ](https://www.te.com/en/product-5-1625971-1.html): warunki montażu rezystora.
- [Oferta47Ω25W](https://www.tme.eu/pl/details/ax25wr-47r/rezystory-mocy/te-connectivity/5-1625971-1/):23.09.2026 pokazywała185szt., MOQ1.
- [TRACO TSR2](https://www.tracopower.com/products/tsr2.pdf): zakresy wejściowe i wymagania przetwornic.

To BOM obwodu do projektu P02, nie lista zmian na P01. Przed wydaniem całej P02
zamknąć dobór bezpiecznika/oprawy i pomiaru gotowości rezerwy oraz mechanikę banku.
''')

zone=(P/'reference/R1-docs/P01-strefy.svg').read_text(encoding='utf-8').replace('/ R1','/ R3').replace('Q2 / D4 / C5 / C6','Q2 TO-220 / D9 / C5-C6').replace('STIS','STS')
write('mechanical/P01-strefy.svg',zone)

# Existing observations remain; the new section narrows methods and adds recovery.
a=old('ODBIOR.md').replace('P01-R2','P01-R3').replace('BOM R2','BOM R3').replace('tab=D=VPROT','tab=D=P01_Q1_DRAIN')
a=a.replace('## 7. Dynamika — protokół R2 zastępujący sekcję R1','## 7. Dynamika — protokół R3')
a=a.replace('VGS i VDS mierz sondą różnicową albo różnicą dwóch kanałów z obiema masami na GND.', 'VGS i VDS mierz zatwierdzonym stanowiskiem z docs/METROLOGIA.md. Odejmowanie kanałów wymaga osobnej kwalifikacji niepewności.')
a=a.replace('efektywna rozdzielczość VGS≤0,1V; podać granicę detekcji prądu/ładunku.', 'niepewność VGS≤0,10V, czasu≤2µs i ładunku≤2µC; wymagana ocena z METROLOGIA.md. Rozdzielczość nie jest niepewnością.')
a=a.replace('dodatni ładunek gałęzi Q1≤10µC po ocenie offsetu i displacement.', 'dodatni ładunek gałęzi Q1≤10µC po ocenie offsetu i displacement; nie zastępować tego warunku samym ΔVPROT.')
i=a.index('Automatyczne powtórzenia odbioru')
a=a[:i]+'''### 7.6 Powrót po krótkim błędzie — nowy wymagany pomiar

Na ustalonym zasilaniu14V wymuś INHIBIT przez10µs/50µs/1ms, potem zwolnij.
J3 wolno sterować tylko suchym stykiem albo otwartym kolektorem do GND,
bez podawania napięcia z generatora na ten węzeł. Zmierzyć faktyczne ENABLE;
szerokość impulsu generatora nie jest automatycznie szerokością ENABLE.
Obciążenie3W i6W stałej mocy, ze znanym sposobem odcięcia przy niskim napięciu.
Rejestrować czas wyłączenia Q1, najniższe VPROT i czas odzyskania zasilania.
Potem trzy impulsy50µs w odstępach20ms. Spadek VPROT na samej P01 jest spodziewany;
nie oznacza zaliczenia ciągłości LOGGER-a. Powrót VPROT≥95%VS w≤300ms,
bez samoczynnego ARM. Długi fault ma pozostawić wyjście wyłączone.

### 7.7 Integracja z P02-HOLD

Dołączać dopiero po niezależnym odbiorze P01 i obwodu HOLD. Zmierzyć moc wszystkich
odbiorników, napięcie rezerwy i szyny5V/3V3/ADC. Przy Ceff≥52,8mF, rezerwie≥9,5V,
poborze≤6W na VLOG_RES i spadku gałęzi≤1,2V przerwa źródła50ms ma zachować
VLOG_RES≥7V i działanie przetwornic. Fizyczny ARM ma pozostać rozbrojony po błędzie.
Powtórzyć w0/25/50°C, z USB i bez, przy aktywnym SD/Wi-Fi/CAN oraz serią faultów.
Sprawdzić rzeczywisty brak restartu i ciągłość numeracji próbek/konfiguracji na SD.
Przerwa zasilania samego sensora z ECU wymaga oznaczenia danych jako nieważne.
Dodatkowo rozładowana rezerwa, długi fault, powrót i doładowanie: nie mogą powodować
prądu wstecznego do VPROT ani uruchomienia silnika. Nie wymagać nieograniczonego
podtrzymania. Rezerwa na50ms nie gwarantuje zakończenia operacji karty SD.

'''+a[i:]
a=a.replace('| -14/-24 V, upływ wsteczny |','| Powrót po10/50/1000µs i seria faultów | | NIE ZBADANO |\n| Integracja HOLD:50ms/6W, SD, USB, ARM | | NIE ZBADANO |\n| -14/-24 V, upływ wsteczny |')
a+='\nMetoda pomiaru i marginesy: METROLOGIA.md. Powerbank nie dopuszcza masy DHO804 na SOURCE.\n'
write('docs/ODBIOR.md',a)

write('docs/PRZEGLAD.md','''
# Przegląd R3 i przejście do layoutu

| Pozycja | Status | Pozostała czynność |
|---|---|---|
| Schemat P01 i delta R2 | ZMIENIONO I SPRAWDZONO AUTOMATYCZNIE | Przegląd wąskiej delty: LK1/net DRAIN, C6 i mechanika. |
| R1-01 | SPRAWDZONE NIEZALEŻNIE W R2; REGRESJA ZACHOWANA | Pomiar rzeczywistego egzemplarza. |
| R2-01 | DECYZJA ARCHITEKTURY WPROWADZONA | Wykonanie P02-HOLD i odbiór integracyjny, przed użyciem LOGGER-a. |
| R2-02 | DOSTĘP I PROTOKÓŁ WPROWADZONE | Kwalifikacja rzeczywistej sondy/stanowiska. |
| B-01: C6 | DOBRANO DOSTĘPNĄ CZĘŚĆ | Ponowne sprawdzenie oferty przy zakupie; przymiarka. |
| M-01: radiatory | DOBRANO STS; WYMIARY I FOOTPRINT ZAPISANE | Sprawdzić faktyczny montaż i mocowanie obudowy na wydruku1:1. |
| Layout | NIEWYKONANY | Rozmieszczenie, routing, kontrola LK1/Kelvin/termików, DRC. |
| H-01: sprzęt, SOA, termika | NIE ZBADANO | ODBIOR i METROLOGIA; dopiero potem integracja. |
| P07 | HOLD | Czekamy na rzeczywisty moduł BTS7960. |

Do layoutu nie są potrzebne gotowe PCB pozostałych modułów. Interfejs P01/P02 jest
ustalony; pojemność HOLD nie trafia bezpośrednio na VPROT. Nie zamykać kontroli
sprzętu samymi symulacjami i nie odtwarzać całego EGRLab przy tej delcie.
''')

write('docs/PROCES.md',old('PROCES.md')+'''

## R3 — obowiązkowe uzupełnienie procesu

1. Każda ochrona ma test początku błędu, trwania, powrotu i serii krótkich błędów.
   Oprócz rezystora używać modelu mocy stałej z jawnym UVLO. Sprawdzić zimny start
   i stan z naładowanymi kondensatorami. Kryterium ochrony mocy jest oddzielne od
   kryterium ciągłości pomiarów.
2. Przed zamrożeniem testu zdefiniować przyrząd, sposób odniesienia masy, punkty
   pomiarowe i niepewność. Sprawdzić instrukcję przyrządu. Wynik z marginesem
   mniejszym od niepewności ma status NIE ROZSTRZYGNIĘTO.
3. Zmiana C/R/tolerancji/footprintu wymaga ponownego zestawu podłączenie–start–OFF–powrót.
   Zmiana wartości dopuszczalnej wymaga decyzji z uzasadnieniem i zachowania starego
   wyniku; nie wolno usuwać niezaliczonej próby.
4. Przed layoutem dobór obejmuje zakup1–5szt., właściwy wariant obudowy, montaż,
   narzędzia i lutowanie. Stan sklepu zapisać z datą; nie jest gwarancją dostępności.
5. Testy mają czytać rzeczywisty eksport CAD. Nowe połączenie musi mieć mutację
   wykrywaną przez test: w R3 są to obejście LK1 i powrót do niewłaściwego C6.
6. Zamrozić schemat dopiero po przeglądzie delty; podczas layoutu zmiany wracają
   do schematu/BOM i odpowiednich testów. Po layout: DRC, pin1 złączy, rzeczywiste
   szprychy, brak obejścia bocznika, odstępy radiatorów i kontrola wydruku1:1.
''')
print('R3 documentation and purchasing tables generated.')
